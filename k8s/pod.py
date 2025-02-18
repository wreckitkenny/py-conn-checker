import json, requests, os, logging

logger = logging.getLogger(os.path.dirname(__file__).split("/")[-1])

def create_namespaced_pod(client, namespace, pod_name, body):
    try:
        client.CoreV1Api().create_namespaced_pod(namespace=namespace, body=body)
        while True:
            response = client.CoreV1Api().read_namespaced_pod(namespace=namespace, name=pod_name)
            if response.status.phase == 'Running':
                break
        return True
    except client.exceptions.ApiException as e:
        logger.error("[{}] {}.".format(namespace, json.loads(e.body)['message']))
    return False

def delete_namespaced_pod(client, namespace, pod_name):
    try:
        client.CoreV1Api().delete_namespaced_pod(namespace=namespace, name=pod_name,
                                                 body=client.V1DeleteOptions(grace_period_seconds=0))
        return True
    except client.exceptions.ApiException as e:
        logger.error("[{}] {}".format(namespace, json.loads(e.body)['message']))
    return False

def exec_namespaced_pod(client, stream, cluster_name, namespace, pod_name, src_name, dst_name, dst_port):
    # command = "telnet {} {}".format(dst_name, dst_port)
    command = ("curl --telnet-option BOGUS=1 --connect-timeout 3 -s -v telnet://{}:{} 2>&1 | egrep -v 'Unknown telnet "
               "option|Closing connection'").format(dst_name, dst_port)
    execCommand = ["/bin/sh", "-c", command]

    response = stream(client.CoreV1Api().connect_get_namespaced_pod_exec, pod_name, namespace, command=execCommand,
                      stderr=True, stdin=False, stdout=True, tty=False, _preload_content=False)

    while response.is_open():
        response.update(timeout=1)

    response.close()

    sign = "💥"
    x = requests.get(os.getenv("HAPROXY_ADDR", default="http://127.0.0.1:5555") + "/v3/services/haproxy/stats/native",
                     auth=(os.getenv("HAPROXY_USER", default="admin"),
                           os.getenv("HAPROXY_PASS", default="default")))
    listOfBackend = [ i['name'] for i in x.json()['stats'] if 'backend_name' in i]
    if dst_name in listOfBackend:
        sign = "💯"

    commandOutput = (">>>>>>>>>> [{}/{}] From {} to {}:{} {}".format(cluster_name, namespace, src_name, dst_name, dst_port, sign)
                      + "\n" + "{}".format(response.read_stdout().strip()))
                      # + "\n" + "STDOUT>>\n{}".format(response.read_stdout().strip())
                      # + "\n" + "STDERR>>\n{}".format(response.read_stderr().strip()))
    return commandOutput