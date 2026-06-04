from itertools import product
from pathlib import Path
import json
import logging
import os

from kubernetes.stream import stream
from k8s import (
    get_api,
    create_namespaced_pod,
    exec_namespaced_pod,
    delete_namespaced_pod,
)

logger = logging.getLogger(Path(__file__).resolve().parent.name)
POD_TEMPLATE_PATH = Path("templates/pod.json")


def _normalize_to_list(value):
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if value is None:
        return []
    value = str(value).strip()
    return [value] if value else []


def _build_pod_body(src_name: str, pod_name: str) -> dict:
    with POD_TEMPLATE_PATH.open(encoding="utf-8") as f:
        body = json.load(f)

    body["metadata"]["labels"]["app.kubernetes.io/name"] = src_name
    body["metadata"]["name"] = pod_name
    return body


def request_handler(json_request):
    api = get_api(use_incluster=os.getenv("INCLUSTER_MODE"), kubeconfig=os.getenv("KUBECONFIG"), context=os.getenv("KUBE_CONTEXT"))

    cluster_name = str(json_request["cluster_name"]).strip()
    namespace = str(json_request["namespace"]).strip()
    src_name = str(json_request["src_name"]).strip()
    dst_names = _normalize_to_list(json_request.get("dst_name"))
    dst_ports = _normalize_to_list(json_request.get("dst_port"))

    if not dst_names:
        raise ValueError("dst_name must not be empty")
    if not dst_ports:
        raise ValueError("dst_port must not be empty")

    pod_name = f"checker-{src_name}"
    exec_outputs = []
    body = _build_pod_body(src_name, pod_name)

    logger.info("[%s] Creating checker pod [%s]", namespace, pod_name)

    created = False
    try:
        created = create_namespaced_pod(
            client=api,
            namespace=namespace,
            pod_name=pod_name,
            body=body,
        )

        if not created:
            logger.error("[%s] Failed to create pod [%s]", namespace, pod_name)
            return ""

        logger.info("[%s] Created pod [%s] successfully", namespace, pod_name)

        for dst_name, dst_port in product(dst_names, dst_ports):
            logger.info(
                "[%s] Executing connectivity check from [%s] to [%s:%s] via pod [%s]",
                namespace,
                src_name,
                dst_name,
                dst_port,
                pod_name,
            )

            response = exec_namespaced_pod(
                client=api,
                stream=stream,
                cluster_name=cluster_name,
                namespace=namespace,
                pod_name=pod_name,
                src_name=src_name,
                dst_name=dst_name,
                dst_port=dst_port,
            )

            exec_outputs.append(response)
            logger.info(
                "[%s] Check result for [%s:%s]: %s",
                namespace,
                dst_name,
                dst_port,
                response,
            )

        return "\n\n".join(exec_outputs)

    finally:
        if created:
            logger.info("[%s] Deleting pod [%s]", namespace, pod_name)
            deleted = delete_namespaced_pod(
                client=api,
                namespace=namespace,
                pod_name=pod_name,
            )
            if deleted:
                logger.info("[%s] Deleted pod [%s] successfully", namespace, pod_name)
            else:
                logger.error("[%s] Failed to delete pod [%s]", namespace, pod_name)