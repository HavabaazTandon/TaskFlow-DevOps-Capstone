#!/usr/bin/env bash
set -u

echo "======================================"
echo "       TASKFLOW DEVOPS DEMO"
echo "======================================"

# 1. Start Docker
echo ""
echo "[1/6] Starting Docker..."
sudo service docker start || true

for i in {1..30}; do
    if docker info >/dev/null 2>&1; then
        break
    fi
    sleep 2
done

if ! docker info >/dev/null 2>&1; then
    echo "ERROR: Docker is not available."
    exit 1
fi

# 2. Load application secret
echo ""
echo "[2/6] Loading application configuration..."

if [[ ! -s .secrets/dev-secret ]]; then
    echo "ERROR: .secrets/dev-secret is missing."
    exit 1
fi

export SECRET_KEY="$(cat .secrets/dev-secret)"

# 3. Start Docker Compose services
echo ""
echo "[3/6] Starting TaskFlow, Jenkins, Prometheus and Grafana..."
docker compose up -d || echo "WARNING: Check Docker Compose output."

# 4. Start existing SonarQube and ELK containers
echo ""
echo "[4/6] Starting security and logging services..."

start_if_exists() {
    local name="$1"

    if docker container inspect "$name" >/dev/null 2>&1; then
        if [[ "$(docker inspect -f '{{.State.Running}}' "$name")" != "true" ]]; then
            docker start "$name" || echo "WARNING: Could not start $name"
        else
            echo "$name is already running."
        fi
    else
        echo "$name container not found; skipping."
    fi
}

start_if_exists sonarqube
start_if_exists devsecops-elasticsearch
start_if_exists devsecops-logstash
start_if_exists devsecops-kibana

# 5. Start Kubernetes
echo ""
echo "[5/6] Starting Minikube..."
minikube start || echo "WARNING: Minikube did not start successfully."

# 6. Verify services
echo ""
echo "[6/6] Checking project status..."

echo ""
echo "---- Docker containers ----"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "---- Kubernetes pods ----"
kubectl get pods 2>/dev/null || echo "Kubernetes is not available."

echo ""
echo "---- ArgoCD applications ----"
kubectl get applications -n argocd 2>/dev/null || echo "ArgoCD is not available."

echo ""
echo "======================================"
echo "       DEMO STARTUP FINISHED"
echo "======================================"
echo ""
echo "TaskFlow:    http://localhost:5002"
echo "Jenkins:     http://localhost:8083"
echo "Prometheus:  http://localhost:9091"
echo "Grafana:     http://localhost:3001"
echo "SonarQube:   http://localhost:9000"
echo "Kibana:      http://localhost:5601"
echo ""
echo "Kubernetes app: use port-forward if needed:"
echo "kubectl port-forward service/taskflow-service 5003:5002"
echo ""
echo "ArgoCD UI: start its port-forward when required:"
echo "kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "Then open https://localhost:8080"
echo ""
echo "Check all warnings above before presenting."
