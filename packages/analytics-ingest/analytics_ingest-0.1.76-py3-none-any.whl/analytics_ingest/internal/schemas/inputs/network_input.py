from analytics_ingest.internal.schemas.network_schema import NetworkStatsSchema


def make_network_input(config, variables):
    stats = NetworkStatsSchema.from_variables(variables, config.vehicle_id)
    return {"input": stats.model_dump()}
