from analytics_ingest.internal.schemas.signal_schema import SignalSchema


def make_signal_input(config_id, batch, message_id, variables):
    signal = SignalSchema.from_variables(config_id, message_id, batch, variables)
    return {"input": {"signals": [signal.model_dump()]}}
