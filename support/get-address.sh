#!/bin/bash
set -euxo pipefail

app_name=elevorin-prima-test-flask-app
current_stack=$(pulumi stack --show-name)

if [ "$current_stack" == "localdev" ]; then
    minikube_ip=$(minikube ip)
    minikube_node_port=$(minikube kubectl -- get service ${app_name} -o jsonpath='{.spec.ports[0].nodePort}')
    minikube_host_address="${minikube_ip}:${minikube_node_port}"
    echo "export HOST_ADDRESS=http://${minikube_host_address}"
else
    pulumi stack output kubeconfig > /tmp/elevorin-kubeconfig
    chmod 600 /tmp/elevorin-kubeconfig
    eks_host_address=$(KUBECONFIG=/tmp/elevorin-kubeconfig kubectl get ingress ${app_name} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
    echo "export HOST_ADDRESS=http://${eks_host_address}"
fi
