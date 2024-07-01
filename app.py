from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

PROMETHEUS_URL = "http://<prometheus-service-ip>:9090"

@app.route('/webhook', methods=['POST'])
def webhook():
    alert = request.json
    enriched_alert = enrich_alert(alert)
    take_action(enriched_alert)
    return jsonify({"status": "success"}), 200

def enrich_alert(alert):
    pod_name = alert['labels']['pod']
    namespace = alert['labels']['namespace']

    # Query Prometheus for memory usage and limits
    memory_usage = query_data(f'container_memory_usage_bytes{{pod="{pod_name}",namespace="{namespace}"}}')
    memory_limit = query_data(f'kube_pod_container_resource_limits_memory_bytes{{pod="{pod_name}",namespace="{namespace}"}}')

    alert['enriched_data'] = {
        "memory_usage": f"{memory_usage} bytes",
        "memory_limit": f"{memory_limit} bytes",
        "suggested_action": "Consider increasing memory limits or analyzing heap dump."
    }
    return alert

def query_data(query):
    response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': query})
    result = response.json()['data']['result']
    if result:
        return result[0]['value'][1]
    return "0"
    # Test Data
    # if 'container_memory_usage_bytes' in query:
    #     return "500000000"
    # if 'kube_pod_container_resource_limits_memory_bytes' in query:
    #     return "1000000000"
    # return "0"

def take_action(alert):
    send_to_slack(alert)
    # Additional actions can be added here

def send_to_slack(alert):
    webhook_url = 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    slack_data = {
        "text": f"Alert received: {alert['annotations']['description']}\n"
                f"Memory Usage: {alert['enriched_data']['memory_usage']}\n"
                f"Memory Limit: {alert['enriched_data']['memory_limit']}\n"
                f"Suggested Action: {alert['enriched_data']['suggested_action']}"
    }
    response = requests.post(
        webhook_url, json=slack_data,
        headers={'Content-Type': 'application/json'}
    )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

