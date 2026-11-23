# TaskFlow – DevOps Automation Capstone

A task management web application developed using Python Flask and supported by an end-to-end DevOps workflow.

This project demonstrates source control, CI/CD automation, containerization, Kubernetes orchestration, infrastructure automation, monitoring, centralized logging, security and GitOps.

## 1. Project Overview

TaskFlow is a web-based task management application developed as part of the ENSP461 DevOps & Automation Capstone Project for B.Tech Computer Science and Engineering.

The project combines application development with automated testing, packaging, deployment, monitoring and operational management.

## 2. Application Features

- User registration and login
- Task creation, viewing, updating and deletion
- Database connectivity
- Responsive web interface
- REST API support
- Application error handling
- Containerized application deployment

## 3. Technology Stack

| Category | Technologies |
|---|---|
| Application | Python, Flask |
| Frontend | HTML, CSS |
| Database | SQLite |
| Version Control | Git, GitHub |
| CI/CD | Jenkins |
| Containerization | Docker, Docker Compose |
| Orchestration | Kubernetes, Minikube |
| Configuration Management | Ansible |
| Infrastructure as Code | Terraform |
| Monitoring | Prometheus, Grafana |
| Logging | Fluent Bit, Elasticsearch, Kibana |
| Security Analysis | SonarQube |
| Deployment Strategy | Blue-Green |
| GitOps | ArgoCD |

## 4. DevOps Implementation – 11 Phases

### Phase 1 – Git and GitHub
- Created and maintained a GitHub repository.
- Used branches for development.
- Practised branch merging and merge conflict resolution.
- Maintained project commit history.

### Phase 2 – Jenkins CI/CD
- Created an automated pipeline using Jenkinsfile.
- Automated source checkout and dependency installation.
- Integrated automated application testing.
- Automated Docker image building.
- Configured the Jenkins pipeline to run checkout, tests and Docker image builds. Automatic push-trigger behaviour must be verified in the Jenkins job configuration.

### Phase 3 – Docker
- Created a Dockerfile for the Flask application.
- Built and ran the application as a Docker container.
- Configured multiple services using Docker Compose.

### Phase 4 – Kubernetes
- Created Deployments and Services.
- Configured ConfigMaps and Secrets.
- Implemented persistent storage using PVC resources.
- Verified scaling, rolling updates and rollback.

### Phase 5 – Ansible
Created playbooks for:
- Docker installation
- Kubernetes installation
- Application deployment
- Application configuration management

### Phase 6 – Terraform
- Implemented Infrastructure as Code.
- Defined variables and outputs.
- Used a Terraform module for TaskFlow resources.
- Validated and planned Kubernetes infrastructure configuration.

### Phase 7 – Monitoring
- Integrated Prometheus for metrics collection.
- Configured Grafana dashboards.
- Monitored application metrics, CPU, memory and container health.
- Verified Prometheus monitoring targets.

### Phase 8 – Centralized Logging
- Deployed Fluent Bit as a Kubernetes DaemonSet.
- Configured Kubernetes log collection.
- Forwarded logs to Elasticsearch.
- Used Kibana to search and explore indexed logs.

### Phase 9 – Security
- Integrated SonarQube for static code analysis.
- Configured secure Jenkins credentials.
- Used non-root execution in the application container.
- Implemented Kubernetes RBAC.
- Protected application secrets and sensitive files.

### Phase 10 – Blue-Green Deployment
- Created separate Blue and Green application deployments.
- Configured service-based traffic switching.
- Tested deployment switching and rollback.

### Phase 11 – GitOps with ArgoCD
- GitOps is part of the project scope. The repository does not currently contain an ArgoCD Application manifest, so repository-managed synchronization is not claimed as complete.

## 5. Repository Structure

- `app.py` – Flask application
- `Dockerfile` and `Dockerfile.jenkins` – Container configurations
- `docker-compose.yml` – Multi-service setup
- `Jenkinsfile` – CI/CD pipeline
- `ansible/playbooks/` – Automation playbooks
- `k8s/` – Kubernetes deployment, storage, RBAC and Blue-Green configurations
- `terraform/` – Infrastructure as Code and reusable module
- `logging/` – Fluent Bit and Logstash configurations
- `templates/` and `static/` – Application interface
- `tests/` – Automated tests
- `docs/architecture.md` – Mermaid system architecture diagram
- `docs/` – Project documentation and workflow evidence
- `start-demo.sh` – Local demo startup script

## 6. Prerequisites

The demonstration environment uses Ubuntu 24.04 under WSL2.

Required tools include Git, Python 3, Docker, Docker Compose, kubectl, Minikube, Jenkins, Ansible and Terraform. Monitoring, logging, security and GitOps services are configured as part of the project environment.

## 7. Clone the Repository

```bash
 git clone https://github.com/HavabaazTandon/TaskFlow-DevOps-Capstone.git
 cd TaskFlow-DevOps-Capstone
```

## 8. Start the Demonstration Environment

Create a local application secret if it does not already exist:

```bash
mkdir -p .secrets
chmod 700 .secrets
openssl rand -hex 32 > .secrets/dev-secret
chmod 600 .secrets/dev-secret
```

Start the environment:

```bash
chmod +x start-demo.sh
./start-demo.sh
```

The startup script starts Docker, Docker Compose services, available security and logging containers, and Minikube.

## 9. Dashboard Access

| Service | URL |
|---|---|
| TaskFlow Application | http://localhost:5002 |
| Jenkins | http://localhost:8083 |
| Prometheus | http://localhost:9091 |
| Grafana | http://localhost:3001 |
| SonarQube | http://localhost:9000 |
| Kibana | http://localhost:5601 |

### Kubernetes Application

Start the port-forward:

```bash
kubectl port-forward service/taskflow-service 5003:5002
```

Open http://localhost:5003. Keep the port-forward terminal open.

### ArgoCD Dashboard

Start the port-forward:

```bash
kubectl port-forward svc/argocd-server -n argocd 8090:443
```

Open https://localhost:8090. Keep the port-forward terminal open. If port 8090 is occupied, choose another free local port and use that port in the browser.

## 10. Verification Commands

Check running Docker containers: `docker compose ps`

Check Kubernetes pods: `kubectl get pods`

Check deployments: `kubectl get deployments`

Check services: `kubectl get services`

Check persistent storage: `kubectl get pvc`

Check Fluent Bit: `kubectl get daemonset fluent-bit -n logging`

Check ArgoCD applications: `kubectl get applications -n argocd`

## 11. Architecture

See [System Architecture](docs/architecture.md) for the Mermaid architecture diagram and component relationships.

## 12. Security Notes

- Application secrets are stored locally and excluded from Git.
- Terraform state and local variable files are excluded from Git.
- Jenkins credentials are managed through Jenkins credential storage.
- The application container uses a non-root user.
- Kubernetes RBAC restricts permissions.
- SonarQube is used for static code analysis.
- Never commit passwords, tokens, secret keys, database files or Terraform state files.

## 13. Project Outcomes

The repository contains the TaskFlow application and configurations for source control, automated testing, containerization, Kubernetes orchestration, infrastructure automation, monitoring, centralized logging, security analysis and Blue-Green deployment. Jenkins execution has been evidenced; automatic push triggering and repository-managed GitOps still require verification.

## 14. Future Scope

- Verify and configure automatic Jenkins triggers for every GitHub push.
- Improve automated security scanning and vulnerability remediation.
- Expand monitoring alerts and application metrics.
- Introduce automated backup and disaster recovery.
- Complete and verify repository-managed GitOps using ArgoCD or FluxCD.
- Improve deployment automation and operational dashboards.

---

**Project:** TaskFlow – DevOps Automation Capstone  
**Course:** ENSP461 – DevOps & Automation Lab  
**Programme:** B.Tech Computer Science and Engineering
### CI/CD Verification
Jenkins pipeline automatic trigger verification.
