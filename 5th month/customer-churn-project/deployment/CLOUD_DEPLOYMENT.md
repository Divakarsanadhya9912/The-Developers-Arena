# Cloud Deployment Guide

This document describes how to take the containerized churn-prediction
service from `docker-compose` (single host) to a horizontally-scalable
cloud deployment.

## 1. Container Registry

Build and push the image to a registry before deploying to any cloud
orchestrator:

```bash
docker build -t churn-prediction-api:1.0.0 .

# AWS ECR
aws ecr create-repository --repository-name churn-prediction-api
docker tag churn-prediction-api:1.0.0 <account_id>.dkr.ecr.<region>.amazonaws.com/churn-prediction-api:1.0.0
docker push <account_id>.dkr.ecr.<region>.amazonaws.com/churn-prediction-api:1.0.0

# Google Artifact Registry
gcloud artifacts repositories create churn-models --repository-format=docker --location=us-central1
docker tag churn-prediction-api:1.0.0 us-central1-docker.pkg.dev/<project>/churn-models/churn-prediction-api:1.0.0
docker push us-central1-docker.pkg.dev/<project>/churn-models/churn-prediction-api:1.0.0

# Azure Container Registry
az acr create --resource-group churn-rg --name churnregistry --sku Basic
docker tag churn-prediction-api:1.0.0 churnregistry.azurecr.io/churn-prediction-api:1.0.0
docker push churnregistry.azurecr.io/churn-prediction-api:1.0.0
```

## 2. Kubernetes Manifests

For orchestrated, auto-scaling deployment, apply the manifests below.

### Deployment (`deployment/k8s-deployment.yaml` excerpt)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: churn-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: churn-api
  template:
    metadata:
      labels:
        app: churn-api
    spec:
      containers:
        - name: churn-api
          image: <registry>/churn-prediction-api:1.0.0
          ports:
            - containerPort: 8000
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata:
  name: churn-api-service
spec:
  selector:
    app: churn-api
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: churn-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: churn-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

Apply with:

```bash
kubectl apply -f deployment/k8s-deployment.yaml
kubectl get pods -l app=churn-api
kubectl get hpa churn-api-hpa
```

## 3. Managed Container Platforms (simpler alternative to K8s)

| Platform              | Command                                                                 |
| ---------------------- | ------------------------------------------------------------------------ |
| AWS ECS Fargate       | `aws ecs create-service --cluster churn --task-definition churn-api ...` |
| Google Cloud Run      | `gcloud run deploy churn-api --image <image> --port 8000 --memory 1Gi`   |
| Azure Container Apps  | `az containerapp create --name churn-api --image <image> --target-port 8000` |

Cloud Run / Container Apps are recommended for this workload's traffic
profile — they scale to zero when idle and scale out automatically
under load, without managing a cluster.

## 4. Scalability Considerations

- **Stateless service** — the API holds no per-request state, so any
  number of replicas can run behind a load balancer with no session
  affinity required.
- **Model loading** — the Keras model and preprocessor are loaded once
  at process startup (`get_predictor()` is memoised), not per-request,
  avoiding repeated disk I/O under load.
- **Batch endpoint** — `/batch_predict` amortizes the fixed cost of a
  forward pass across up to 500 records, which is far more throughput-
  efficient than 500 individual `/predict` calls.
- **Horizontal scaling triggers** — CPU utilization > 70% (HPA above)
  or P95 latency > 250ms (Prometheus alert) should trigger scale-out.
- **Database/cache layer** — for high-volume production use, add a
  Redis cache keyed on `CustomerID` for customers scored within the
  last hour, since churn probability changes slowly day-to-day.
- **Connection pooling** — if a real database replaces CSV files, use
  a pooled async driver (e.g. `asyncpg`) rather than per-request
  connections.

## 5. Rollback Strategy

Tag every image with a semantic version and keep the previous image
available:

```bash
kubectl set image deployment/churn-api churn-api=<registry>/churn-prediction-api:0.9.0
```

This reverts traffic to the previous model version in seconds if the
new release shows elevated error rates or unexpected drift.
