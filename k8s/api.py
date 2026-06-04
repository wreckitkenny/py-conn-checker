from functools import lru_cache
from kubernetes import client, config


@lru_cache(maxsize=None)
def get_api(
    use_incluster: bool = True,
    kubeconfig: str | None = None,
    context: str | None = None,
) -> client:
    if use_incluster:
        config.load_incluster_config()
    else:
        config.load_kube_config(
            config_file=kubeconfig,
            context=context,
        )

    return client