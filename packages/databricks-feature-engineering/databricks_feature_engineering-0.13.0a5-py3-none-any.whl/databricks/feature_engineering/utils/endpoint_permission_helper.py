import logging
import re
import uuid
from typing import Any, Dict, List, Tuple

from mlflow.utils import databricks_utils
from sqlalchemy import create_engine, text

from databricks.ml_features.utils.rest_utils import http_request, verify_rest_response
from databricks.sdk import WorkspaceClient

_logger = logging.getLogger(__name__)


class EndpointPermissionHelper:
    def __init__(
        self, fe_client: "FeatureEngineeringClient", workspace_client: WorkspaceClient
    ):
        self.fe_client = fe_client
        self.workspace_client = workspace_client

    def _get_endpoint_events_reversed(self, endpoint_name: str) -> List[Dict[str, Any]]:
        """
        Get the events of an endpoint in reverse order, so the most recent event is parsed first.
        """
        url = f"/api/2.0/serving-endpoints/{endpoint_name}/events"
        response = http_request(
            host_creds=databricks_utils.get_databricks_host_creds(),
            endpoint=url,
            method="GET",
        )
        verify_rest_response(response, url)
        return response.json()["events"][::-1]

    def _get_feature_spec_dependencies(
        self, feature_spec_name: str
    ) -> List[Dict[str, Any]]:
        """
        Get a feature spec with its dependencies.
        The option include_dependencies is not available in the SDK.
        """
        url = f"/api/2.0/unity-catalog/functions/{feature_spec_name}?include_dependencies=true"
        response = http_request(
            host_creds=databricks_utils.get_databricks_host_creds(),
            endpoint=url,
            method="GET",
        )
        verify_rest_response(response, url)
        return response.json()["routine_dependencies"]

    def _get_service_principal_id(self, endpoint_name):
        events = self._get_endpoint_events_reversed(endpoint_name)
        for event in events:
            message = event.get("message", "")
            if "principal creation with ID" in message and "succeeded" in message:
                match = re.search(r"ID `([a-f0-9\-]+)` succeeded", message)
                if match:
                    return match.group(1)
        raise ValueError(
            f"Cannot infer service principal id from the endpoint {endpoint_name}. "
            + "Please make sure the endpoint is ready or specify lakebase_role explicitly."
        )

    def _get_dependency_tables(self, endpoint_name):
        endpoint = self.workspace_client.serving_endpoints.get(endpoint_name)
        # Prefer pending config because that's the upcoming version.
        endpoint_config = endpoint.pending_config or endpoint.config
        served_entities = endpoint_config.served_entities
        if len(served_entities) != 1:
            raise ValueError(
                f"Endpoint {endpoint_name} must have exactly one served entity."
            )
        served_entity = served_entities[0]
        tables = []
        if not served_entity.entity_version:
            dependenciesDict = self._get_feature_spec_dependencies(
                served_entity.entity_name
            )
            for dependency in dependenciesDict["dependencies"]:
                if dependency.get("table"):
                    tables.append(dependency["table"]["table_full_name"])
        else:
            model_version = self.workspace_client.model_versions.get(
                served_entity.entity_name, served_entity.entity_version
            )
            dependencies = model_version.model_version_dependencies.dependencies
            for dependency in dependencies:
                if dependency.table:
                    tables.append(dependency.table.table_full_name)
        return tables

    def _get_online_tables(self, tables: List[str]) -> List[str]:
        online_table_names = []
        for table in tables:
            feature_table = self.fe_client.get_table(name=table)
            online_table_names.append(feature_table.online_stores[0].name)
        return online_table_names

    def _get_db_instance_name(self, online_table_names: List[str]) -> str:
        instance_names = set()
        for online_table_name in online_table_names:
            synced_table = self.workspace_client.database.get_synced_database_table(
                online_table_name
            )
            instance_name = (
                synced_table.effective_database_instance_name
                or synced_table.database_instance_name
            )
            instance_names.add(instance_name)
        if not instance_names:
            raise ValueError(
                "The endpoint does not depend on Databricks Online Feature Store"
            )
        if len(instance_names) > 1:
            raise ValueError(
                f"Endpoint depending on multiple Databricks Online Feature Stores is not supported. This endpoint depends on {instance_names}"
            )
        return instance_names.pop()

    def _get_pg_dns(self, instance_name: str) -> str:
        instance = self.workspace_client.database.get_database_instance(instance_name)
        return instance.read_write_dns

    def _get_username_cred(self, instance_name: str) -> Tuple[str, str]:
        # Not importing at the top to make FE client instantiable in unit tests
        from databricks.sdk.runtime import dbutils

        context = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
        user_name = context.userName().get()
        cred = self.workspace_client.database.generate_database_credential(
            request_id=str(uuid.uuid4()), instance_names=[instance_name]
        )
        return user_name, cred.token

    def _grant_select_permission_pg(
        self,
        dns: str,
        username: str,
        password: str,
        database: str,
        schema: str,
        table: str,
        role: str,
    ):
        engine = create_engine(
            f"postgresql+psycopg2://{username}:{password}@{dns}:5432/{database}?sslmode=require"
        )
        try:
            with engine.connect() as conn:
                conn.execute(text(f'GRANT USAGE ON SCHEMA "{schema}" TO "{role}"'))
                conn.execute(
                    text(f'GRANT SELECT ON TABLE "{schema}"."{table}" TO "{role}"')
                )
                _logger.info(
                    f"Granted SELECT permission on {schema}.{table} to service principal {role}"
                )
                conn.commit()
        except Exception as e:
            _logger.error(f"Failed to grant permission for the endpoint:")
            raise e

    def grant_permission(
        self, endpoint_name: str, endpoint_service_principal: str = None
    ):
        service_principal_id = (
            endpoint_service_principal or self._get_service_principal_id(endpoint_name)
        )
        tables = self._get_dependency_tables(endpoint_name)
        online_tables = self._get_online_tables(tables)
        # This will raise an error if there are multiple instances involved.
        instance_name = self._get_db_instance_name(online_tables)
        dns = self._get_pg_dns(instance_name)
        # Current user's credentials.
        username, password = self._get_username_cred(instance_name)
        for online_table in online_tables:
            database, schema, pg_table = online_table.split(".")
            self._grant_select_permission_pg(
                dns,
                username,
                password,
                database,
                schema,
                pg_table,
                service_principal_id,
            )
