

# KubeADM Process ##
- Not required for deployment on pre-existing, fleshed out kube clusters

## Requires: ##
* coredns (to resolve ip between the pods and postgres)
* defined pod CIDR

## Kube Admin Process ##

#### Steps ####

- `kubeadm init --pod-network-cidr=10.244.0.0/16` # defined cidr is required for coredns
- `sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config`
- `sudo chown $(id -u):$(id -g) $HOME/.kube/config`
- copy config to any secondary machines

#### Update configs to use external address: ####
  - `mv /etc/kubernetes/pki/apiserver.{crt,key} ~`
  - create kubeadm.yml file if dne as descibed. Need to add external ip to certSANs
  - `kubeadm init phase certs apiserver --config /root/kubeadm.yml` #fix certs to include remote IP for port forwarding
  - `delete pod kube-apiserver-shivaserv`
  - apply: https://devops.stackexchange.com/questions/9483/how-can-i-add-an-additional-ip-hostname-to-my-kubernetes-certificate

#### Deploy ingress pod: ####
  `kubectl apply -f kube_nginx_deploy.yml`
  - have to add hostNetwork: true to get it to listen on port 80 on the localhost if this is a baremetal implementation

Remove taint if needed:
  `kubectl taint nodes shivaserv node-role.kubernetes.io/control-plane:NoSchedule-`


## Kube Deployment Process ##
- Build docker image for api and push to dockerhub # e.g. gitprotean/starlonk-api-init:latest
- Apply all pod, service and ingress manifests
  - `kubectl apply -f kube_pg.yml -f kube_api.yml -f api_ingress.yml`


## Alternative: Docker Compose ##
- Navigate into docker directory
- `docker-compose up`
