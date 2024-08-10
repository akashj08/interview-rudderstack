from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get environment variables
slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
prometheus_url = os.getenv("PROMETHEUS_URL")  # e.g., http://prometheus-server:9090

# Function to fetch resource utilization data from Prometheus
def fetch_resource_utilization(namespace, pod_name):
    query_cpu = f'sum(rate(container_cpu_usage_seconds_total{{namespace="{namespace}", pod="{pod_name}"}}[5m]))'
    query_memory = f'sum(container_memory_usage_bytes{{namespace="{namespace}", pod="{pod_name}"}})'

    cpu_utilization = query_prometheus(query_cpu)
    memory_utilization = query_prometheus(query_memory)

    return {
        'cpu_utilization': f'{cpu_utilization:.2f} cores' if cpu_utilization else 'N/A',
        'memory_utilization': f'{memory_utilization / (1024 * 1024):.2f} MiB' if memory_utilization else 'N/A'
    }

# Function to query Prometheus
def query_prometheus(query):
    try:
        response = requests.get(f'{prometheus_url}/api/v1/query', params={'query': query})
        response.raise_for_status()
        results = response.json().get('data', {}).get('result', [])

        if results:
            # Return the first result value (assuming it's a single value query)
            return float(results[0]['value'][1])
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error querying Prometheus: {e}")
        return None

# Function to enrich the alert data
def enrich_alert_data(alert):
    namespace = alert['labels'].get('namespace')
    pod_name = alert['labels'].get('pod')

    # Fetch resource utilization data from Prometheus
    resource_utilization = fetch_resource_utilization(namespace, pod_name)

    # Add fetched data to the alert
    alert['enriched_data'] = resource_utilization
    return alert

# Function to send a message to Slack
def send_to_slack(message):
    if not slack_webhook_url:
        logger.error("Slack webhook URL not configured.")
        return
    
    payload = {"text": message}
    response = requests.post(slack_webhook_url, json=payload)
    if response.status_code == 200:
        logger.info("Message sent to Slack successfully")
    else:
        logger.error("Failed to send message to Slack")

# Endpoint to receive alerts
@app.route('/alert', methods=['POST'])
def receive_alert():
    alert = request.json
    logger.info("Received alert: %s", alert)

    # Handle only specific alerts
    if alert['labels']['alertname'] == 'KubePodCrashLooping':
        # Enrich alert data
        enriched_alert = enrich_alert_data(alert)
        logger.info("Enriched alert data: %s", enriched_alert)

        # Take action based on the enriched alert
        action_message = f"Alert: {enriched_alert['annotations']['summary']}\n" \
                         f"Description: {enriched_alert['annotations']['description']}\n" \
                         f"CPU Utilization: {enriched_alert['enriched_data']['cpu_utilization']}\n" \
                         f"Memory Utilization: {enriched_alert['enriched_data']['memory_utilization']}\n" \
                         f"Severity: {alert['labels']['severity']}\n" \
                         f"Runbook URL: {enriched_alert['annotations'].get('runbook_url', 'N/A')}"
        
        send_to_slack(action_message)

        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "ignored"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
