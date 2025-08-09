def make_configuration_input_from_schema(config_schema):
    return {"input": config_schema.model_dump()}
