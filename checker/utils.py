import pathlib, yaml, logging.config, logging

def load_config(config_path):
    config_file = pathlib.Path(config_path)
    with open(config_file) as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)

    if "logging.yaml" in config_path:
        logging.config.dictConfig(config)

    return config