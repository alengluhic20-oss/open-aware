# MA'AT Framework - Production Deployment Guide

## Prerequisites

### For Docker Compose Deployment
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### For Kubernetes Deployment
- Kubernetes 1.24+
- kubectl configured
- 8GB RAM minimum across cluster
- 20GB disk space
- Load balancer or Ingress controller

## Step-by-Step Deployment

### 1. Build Docker Image

```bash
cd maat-framework

# Build the image
docker build -t maat-framework:latest .

# Verify image
docker images | grep maat-framework
```

### 2. Deploy with Docker Compose (Recommended for Testing)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f orchestrator

# Test the API
curl http://localhost:8000/health

# View monitoring
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin)

# Stop services
docker-compose down
```

### 3. Deploy to Kubernetes (Production)

#### Step 3.1: Prepare the Cluster

```bash
# Verify cluster access
kubectl cluster-info

# Create namespace
kubectl apply -f kubernetes/00-namespace.yaml

# Verify namespace
kubectl get namespace maat-framework
```

#### Step 3.2: Build and Push Image (for remote clusters)

```bash
# Tag for registry
docker tag maat-framework:latest your-registry.com/maat-framework:latest

# Push to registry
docker push your-registry.com/maat-framework:latest

# Update deployment manifests to use your registry
# Edit kubernetes/*.yaml files and replace 'maat-framework:latest' with your image
```

#### Step 3.3: Deploy Agents

```bash
# Deploy all agents
kubectl apply -f kubernetes/01-cna-agent.yaml
kubectl apply -f kubernetes/02-tsa-agent.yaml
kubectl apply -f kubernetes/03-uea-agent.yaml
kubectl apply -f kubernetes/04-laa-agent.yaml
kubectl apply -f kubernetes/05-hta-agent.yaml

# Wait for agents to be ready (this may take 2-3 minutes)
kubectl wait --for=condition=ready pod -l app=cna-agent -n maat-framework --timeout=300s
kubectl wait --for=condition=ready pod -l app=tsa-agent -n maat-framework --timeout=300s
kubectl wait --for=condition=ready pod -l app=uea-agent -n maat-framework --timeout=300s
kubectl wait --for=condition=ready pod -l app=laa-agent -n maat-framework --timeout=300s
kubectl wait --for=condition=ready pod -l app=hta-agent -n maat-framework --timeout=300s
```

#### Step 3.4: Deploy Orchestrator

```bash
# Deploy orchestrator
kubectl apply -f kubernetes/06-orchestrator.yaml

# Wait for orchestrator
kubectl wait --for=condition=ready pod -l app=orchestrator -n maat-framework --timeout=300s

# Get external IP (if LoadBalancer)
kubectl get service orchestrator-service -n maat-framework
```

#### Step 3.5: Verify Deployment

```bash
# Check all pods
kubectl get pods -n maat-framework

# Expected output:
# NAME                            READY   STATUS    RESTARTS   AGE
# cna-agent-xxx                   1/1     Running   0          2m
# tsa-agent-xxx                   1/1     Running   0          2m
# uea-agent-xxx                   1/1     Running   0          2m
# laa-agent-xxx                   1/1     Running   0          2m
# hta-agent-xxx                   1/1     Running   0          2m
# orchestrator-xxx                1/1     Running   0          1m

# Check services
kubectl get services -n maat-framework

# Test health endpoint
ORCHESTRATOR_IP=$(kubectl get service orchestrator-service -n maat-framework -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$ORCHESTRATOR_IP/health
```

### 4. Configure Monitoring

#### Prometheus Setup

```bash
# If using Kubernetes, deploy Prometheus
kubectl create namespace monitoring

# Deploy Prometheus (example using Helm)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/prometheus -n monitoring

# Configure scraping for MA'AT Framework
kubectl apply -f monitoring/prometheus.yml -n monitoring
```

#### Grafana Setup

```bash
# Deploy Grafana
helm install grafana grafana/grafana -n monitoring

# Get admin password
kubectl get secret --namespace monitoring grafana -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward to access
kubectl port-forward -n monitoring svc/grafana 3000:80
```

### 5. Test the Deployment

#### Test Single Narrative

```bash
# Get orchestrator URL
ORCHESTRATOR_URL="http://<EXTERNAL_IP>"

# Test evaluation
curl -X POST $ORCHESTRATOR_URL/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "narrative": "The detective stood beneath the Sydney Opera House, built in 1973, contemplating the case.",
    "metadata": {"source": "test"}
  }'
```

#### Test Batch Processing

```bash
curl -X POST $ORCHESTRATOR_URL/batch \
  -H "Content-Type: application/json" \
  -d '{
    "narratives": [
      {"narrative": "First test narrative with proper historical facts."},
      {"narrative": "Second test narrative discussing various topics."}
    ]
  }'
```

#### Test Health and Statistics

```bash
# Health check
curl $ORCHESTRATOR_URL/health

# Statistics
curl $ORCHESTRATOR_URL/statistics

# Audit trail
curl $ORCHESTRATOR_URL/audit-trail
```

## Scaling

### Manual Scaling

```bash
# Scale CNA agent to 5 replicas
kubectl scale deployment cna-agent -n maat-framework --replicas=5

# Scale orchestrator to 5 replicas
kubectl scale deployment orchestrator -n maat-framework --replicas=5
```

### Horizontal Pod Autoscaler (HPA)

HPA is already configured for all deployments. Verify with:

```bash
kubectl get hpa -n maat-framework
```

The system will automatically scale based on:
- CPU utilization (target: 70%)
- Memory utilization (target: 80%)

Min replicas: 2
Max replicas: 10 (agents), 20 (orchestrator)

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n maat-framework

# Check logs
kubectl logs <pod-name> -n maat-framework

# Common issues:
# 1. Image pull errors - check image name and registry access
# 2. Resource limits - check cluster has enough resources
# 3. Health check failures - check port configuration
```

### Service Not Reachable

```bash
# Check service endpoints
kubectl get endpoints -n maat-framework

# Check if pods are ready
kubectl get pods -n maat-framework -o wide

# Port forward for testing
kubectl port-forward svc/orchestrator-service -n maat-framework 8000:80
```

### High Error Rates

```bash
# Check logs for errors
kubectl logs -l app=orchestrator -n maat-framework --tail=100

# Check agent logs
kubectl logs -l app=cna-agent -n maat-framework --tail=100

# Check resource usage
kubectl top pods -n maat-framework
```

## Backup and Recovery

### Backup Audit Trail

```bash
# Export audit trail
curl $ORCHESTRATOR_URL/audit-trail > audit-backup-$(date +%Y%m%d).json

# For Kubernetes, export from HTA pods
kubectl exec -n maat-framework <hta-pod-name> -- cat /app/audit-trail.json > backup.json
```

### Disaster Recovery

```bash
# Save all configurations
kubectl get all -n maat-framework -o yaml > maat-framework-backup.yaml

# Restore
kubectl apply -f maat-framework-backup.yaml
```

## Security Hardening

1. **Enable RBAC**
```bash
kubectl create serviceaccount maat-framework -n maat-framework
# Apply RBAC policies
```

2. **Network Policies**
```bash
# Restrict traffic between pods
kubectl apply -f kubernetes/network-policies.yaml
```

3. **Secrets Management**
```bash
# Use Kubernetes secrets for sensitive data
kubectl create secret generic maat-secrets -n maat-framework \
  --from-literal=api-key=your-api-key
```

4. **TLS/SSL**
- Configure Ingress with TLS certificates
- Use cert-manager for automatic certificate renewal

## Performance Tuning

### Adjust Resource Limits

Edit deployment files to increase resources:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Optimize Replicas

Based on load testing, adjust min/max replicas in HPA configurations.

### Database for Persistence

For production, add PostgreSQL or MongoDB for audit trail persistence:

```bash
# Example with PostgreSQL
helm install postgresql bitnami/postgresql -n maat-framework
```

## Maintenance

### Rolling Updates

```bash
# Update image
kubectl set image deployment/orchestrator -n maat-framework \
  orchestrator=maat-framework:v2.0.0

# Check rollout status
kubectl rollout status deployment/orchestrator -n maat-framework
```

### Rollback

```bash
# Rollback to previous version
kubectl rollout undo deployment/orchestrator -n maat-framework

# Rollback to specific revision
kubectl rollout undo deployment/orchestrator -n maat-framework --to-revision=2
```

## 24/7 Operations Checklist

- [ ] All pods running and healthy
- [ ] HPA configured and working
- [ ] Monitoring dashboards operational
- [ ] Alerts configured (PagerDuty, Slack, etc.)
- [ ] Backup automation in place
- [ ] Log aggregation configured (ELK, Splunk, etc.)
- [ ] Documentation updated
- [ ] On-call rotation established
- [ ] Runbooks created for common issues

## Support

For production support:
- Monitor logs: `kubectl logs -f -l app=orchestrator -n maat-framework`
- Check metrics: Grafana dashboard
- Review audit trail: `/audit-trail` endpoint
- Health status: `/health` endpoint

---

☥ **Production deployment complete - MA'AT Framework running 24/7** ☥
