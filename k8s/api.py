from kubernetes import client, config

def get_api():
    config.load_incluster_config()
    # config.load_kube_config()
    return client
