from analytics_ingest.internal.schemas.gps_schema import GPSSchema
from analytics_ingest.internal.schemas.inputs.gps_input import make_gps_input
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations
from analytics_ingest.internal.utils.serialization import serialize_payload


def create_gps(executor: GraphQLExecutor, config_id: str, gps: dict):
    gps_item = GPSSchema(**gps)
    payload = make_gps_input(config_id, [gps_item])
    payload = serialize_payload(payload)
    executor.execute(GraphQLMutations.upsert_gps_data(), payload)
