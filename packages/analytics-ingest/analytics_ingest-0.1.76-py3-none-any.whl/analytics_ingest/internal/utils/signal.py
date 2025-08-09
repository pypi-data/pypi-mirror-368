from analytics_ingest.internal.schemas.inputs.signal_input import make_signal_input
from analytics_ingest.internal.utils.batching import Batcher
from analytics_ingest.internal.utils.graphql_executor import GraphQLExecutor
from analytics_ingest.internal.utils.mutations import GraphQLMutations


def build_batched_signal_inputs(config_id, variables, message_id, batch_size):
    if "data" not in variables:
        raise ValueError("Missing required field: 'data'")
    batches = Batcher.create_batches(variables["data"], batch_size)
    return [
        make_signal_input(config_id, batch, message_id, variables) for batch in batches
    ]


def create_signal(
    executor: GraphQLExecutor,
    config_id: str,
    variables: dict,
    message_id: str,
    batch_size: int,
):
    inputs = build_batched_signal_inputs(config_id, variables, message_id, batch_size)
    for payload in inputs:
        executor.execute(GraphQLMutations.upsert_signal_data(), payload)
