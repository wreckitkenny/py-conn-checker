from k8s import get_api, create_namespaced_pod, exec_namespaced_pod, delete_namespaced_pod
from kubernetes.stream import stream
import json, logging, os

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def request_handler(json_request):
    # Create a namespaced pod
    execOutList = list()
    cluster_name = json_request["cluster_name"].rstrip()
    namespace = json_request["namespace"].rstrip()
    srcName = json_request["src_name"].rstrip()
    dstName = json_request["dst_name"].rstrip()
    dstPort = json_request["dst_port"].rstrip()
    pod_name = "checking-from-{}-to-{}-port-{}".format(srcName, dstName, dstPort)
    with open('templates/pod.json') as json_file:
        body = json.load(json_file)
        body['metadata']['labels']['app.kubernetes.io/name'] = srcName
        body['metadata']['name'] = pod_name

    # print("[{}] Creating a connection checker pod named [{}].".format(namespace, pod_name))
    logger.info("[{}] Creating a connection checker pod named [{}].".format(namespace, pod_name))
    createdResponse = create_namespaced_pod(client=get_api(), namespace=namespace, pod_name=pod_name, body=body)
    if createdResponse:
        logger.info("[{}] Created a namespaced pod [{}] successfully.".format(namespace, pod_name))
    else:
        logger.error("[{}] Failed to create a namespaced pod [{}].".format(namespace, pod_name))

    # Exec a namespaced pod
    logger.info("[{}] Executing a telnet command into pod [{}].".format(namespace, pod_name))
    execResponse = exec_namespaced_pod(client=get_api(), stream=stream, cluster_name=cluster_name, namespace=namespace, pod_name=pod_name,
                                            src_name=srcName, dst_name=dstName, dst_port=dstPort)
    execOutList.append(execResponse)
    logger.info("[{}] Executed a telnet command with an output:\n{}".format(namespace, execResponse))

    # Delete a namespaced pod
    logger.info("[{}] Deleting the pod {}.".format(namespace, pod_name))
    deleteResponse = delete_namespaced_pod(client=get_api(), namespace=namespace, pod_name=pod_name)
    if deleteResponse:
        logger.info("[{}] Forcefully deleted {} successfully.".format(namespace, pod_name))
    else:
        logger.error("[{}] Failed to delete a namespaced pod [{}].".format(namespace, pod_name))

    return "\n\n".join(execOutList)