# Alert Manager with Enrichment and Slack Notifications

This project sets up a Flask application that receives alerts from Alertmanager, enriches them with additional data from Prometheus, and sends notifications to Slack.

## Prerequisites

- Docker
- Kubernetes cluster (e.g., kind cluster)
- Prometheus and Alertmanager deployed in the Kubernetes cluster
- Slack webhook URL for sending notifications

## Setup Instructions

### Step 1: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/your-username/alert-manager-enrichment.git
cd alert-manager-enrichment
```
### Step 2: Build the Docker Image
Build the Docker image for the Flask application:

``` bash 
docker build -t alert-manager-enrichment .
```

# Step 3 : Deploy Prometheus and Alertmanager

```bash 
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack
```

# Step 4: Deploy the Flask Application

``` bash 
kubectl apply -f flask-deployment.yaml
```

Test Alert Webhook
``` bash 
curl -X POST http://<flask-service-ip>:80/webhook -H "Content-Type: application/json" -d '{
    "annotations": {
        "description": "Pod customer/customer-rs-transformer-9b75b488c-cpfd7 (rs-transformer) is restarting 2.11 times / 10 minutes.",
        "runbook_url": "https://github.com/kubernetes-monitoring/kubernetes-mixin/tree/master/runbook.md#alert-name-kubepodcrashlooping",
        "summary": "Pod is crash looping."
    },
    "labels": {
        "alertname": "KubePodCrashLooping",
        "cluster": "cluster-main",
        "container": "rs-transformer",
        "endpoint": "http",
        "job": "kube-state-metrics",
        "namespace": "customer",
        "pod": "customer-rs-transformer-9b75b488c-cpfd7",
        "priority": "P0",
        "prometheus": "monitoring/kube-prometheus-stack-prometheus",
        "region": "us-west-1",
        "replica": "0",
        "service": "kube-prometheus-stack-kube-state-metrics",
        "severity": "CRITICAL"
    },
    "startsAt": "2022-03-02T07:31:57.339Z",
    "status": "firing"
}'

'''
