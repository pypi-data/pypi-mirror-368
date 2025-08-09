from analytics_ingest.internal.schemas.inputs.network_input import make_network_input
from analytics_ingest.internal.schemas.network_schema import NetworkStatsSchema
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations


def create_network(executor: GraphQLExecutor, config, variables: dict):
    payload = make_network_input(config, variables)
    executor.execute(GraphQLMutations.create_network_stats_mutation(), payload)


def create_network_payload(config, variables):
    schema = NetworkSchema.from_variables(variables)
    return make_network_input(config, schema)
