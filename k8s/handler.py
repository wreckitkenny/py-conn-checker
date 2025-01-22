from k8s import get_api, create_namespaced_pod, exec_namespaced_pod, delete_namespaced_pod
from kubernetes.stream import stream
import json

def request_handler(json_request,pod_name="connection-checker"):
    # Create a namespaced pod
    execOutList = list()
    namespace = json_request["namespace"]
    srcName = json_request["src_name"]
    dstName = json_request["dst_name"]
    dstPort = json_request["dst_port"]
    with open('templates/pod.json') as json_file:
        body = json.load(json_file)
        body['metadata']['labels']['app.kubernetes.io/name'] = srcName

    print("[{}] Creating a connection checker pod named [{}].".format(namespace, pod_name))
    createdResponse = create_namespaced_pod(client=get_api(), namespace=namespace, pod_name=pod_name, body=body)
    if createdResponse:
        print("[{}] Created a namespaced pod [{}] successfully.".format(namespace, pod_name))
    else:
        print("[{}] Failed to create a namespaced pod [{}].".format(namespace, pod_name))

    # Exec a namespaced pod
    print("[{}] Executing a telnet command into pod [{}].".format(namespace, pod_name))
    execResponse = exec_namespaced_pod(client=get_api(), stream=stream, namespace=namespace, pod_name=pod_name,
                                            dst_name=dstName, dst_port=dstPort)
    execOutList.append(execResponse)
    print("[{}] Executed a telnet command with an output:\n{}".format(namespace, execResponse))

    # Delete a namespaced pod
    print("[{}] Deleting the pod {}.".format(namespace, pod_name))
    deleteResponse = delete_namespaced_pod(client=get_api(), namespace=namespace, pod_name=pod_name)
    if deleteResponse:
        print("[{}] Forcefully deleted {} successfully.".format(namespace, pod_name))
    else:
        print("[{}] Failed to delete a namespaced pod [{}].".format(namespace, pod_name))

    return "\n\n".join(execOutList)