def make_gps_input(config_id, gps_items):
    return {
        "input": {
            "configurationId": config_id,
            "data": [item.model_dump() for item in gps_items],
        }
    }
