
### Overview

This project provides a system to manage alerts programmatically with defined actions. It receives alerts via a webhook, enriches the alert data by fetching additional information from services like Prometheus, and takes appropriate actions such as sending notifications to Slack.

### Architecture

1. **Receive:**
   - A webhook endpoint is set up to receive alerts.
  
2. **Enrich:**
   - Enriches the received alerts with additional data, such as CPU/memory utilization fetched from Prometheus or other monitoring tools.
  
3. **Take Action:**
   - Based on the enriched data, appropriate actions are taken. These could include:
     - Sending a notification to Slack.
     - Forwarding the alert to PagerDuty.
     - Automatic remediation actions (e.g., scaling resources).

<img width="1383" alt="Screenshot 2024-08-11 at 2 09 53 AM" src="https://github.com/user-attachments/assets/6a19329a-8e8b-40c0-b6b9-0704fd847b89">

### Getting Started

#### Prerequisites

- **Docker** installed
- **Kubernetes Cluster** (e.g., kind, Minikube, EKS , GKE etc.)
- **kubectl** and **helm** installed
- **Prometheus** and **Alertmanager** deployed in the cluster

#### Setup Instructions

1. **Clone the Repository:**
   
   ```bash
   git clone https://github.com/your-repo/alert-manager.git
   cd alert-manager
   ```
   Update the app.py as per you requirement . Just build the docker imager
3. **Build the Docker Image:**

   ```bash
   docker build -t your-dockerhub-username/alert-manager:v1 .
   ```

4. **Push the Docker Image:**

   ```bash
   docker push your-dockerhub-username/alert-manager:v1
   ```

5. **Deploy Prometheus:**

   - Deploy Prometheus using the provided Helm chart inside the `helm-chart/` folder:

     ```bash
     kubectl create  ns monitor
     helm install prometheus helm-chart/prometheus/  -n monitor
     ```

6. **Update Kubernetes Manifest:**

   - **Slack Webhook URL:** Ensure the Kubernetes manifest (`deployment-k8s.yaml`) includes the correct Slack webhook URL in secrete as base64 encrypted:
   
     ```yaml
     env:
       - name: SLACK_WEBHOOK_URL
         valueFrom:
           secretKeyRef:
             name: alert-manager-secrets
             key: slack_webhook_url
     ```

   - **Prometheus URL:** Update the Prometheus URL in the same manifest:

     ```yaml
     env:
       - name: PROMETHEUS_URL
         value: "http://prometheus-server:9090"  # Replace with your Prometheus server URL
     ```

7. **Deploy to Kubernetes:**

   - Deploy using the provided Kubernetes manifest:

     ```bash
     kubectl apply -f deployment-k8s.yaml
     ```

8. **Test the Setup:**

   - Forward the service port to your localhost:

     ```bash
     kubectl port-forward svc/alert-manager 8080:80 -n alert-manager
     ```

   - Send a test alert to the webhook:

     ```bash
     curl -X POST http://localhost:8080/alert -H "Content-Type: application/json" -d '{
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
     ```

     Reponse : 
      ```
      {"status":"success"}
      ```

   - Verify that the alert is processed and that a notification is sent to Slack.

### Extending the System

To add new alert handling flows:

1. **Add a New Function:** Extend the enrichment logic by adding a new function in the `alert-manager` module.
2. **Update the Webhook Handler:** Integrate the new function in the webhook handling logic.
3. **Document the Changes:** Update this README and the code documentation to reflect the new handling pipeline.

### Observability

- Implement observability for the alert manager using Prometheus metrics or logs to monitor the health and actions triggered by the system.

### Contributing

Please fork the repository and submit a pull request with detailed information on the changes made.

### License

This project is licensed under the MIT License.

---

I'll now save this updated README to your project directory.

The updated `README.md` file has been successfully created and saved in the project directory. You can download it [here](sandbox:/mnt/data/interview-rudderstack-main/README.md).

This README includes all the necessary steps, including deploying the Prometheus server using the provided Helm chart, updating the Slack webhook URL and Prometheus URL in the Kubernetes manifest, and testing the deployment.

If you need any more changes or assistance, feel free to ask!
