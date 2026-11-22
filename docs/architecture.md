# TaskFlow – System Architecture

## Architecture Diagram

```mermaid
flowchart TB
        U[User / Browser] --> APP[TaskFlow Flask Application]
        APP --> DB[(SQLite Database)]
        APP --> METRICS[Prometheus Metrics]

        DEV[Developer] --> GH[GitHub Repository]
        GH --> J[Jenkins CI Pipeline]
        J --> TEST[Automated Pytest Tests]
        TEST --> IMG[Docker Image Build]

        IMG --> DC[Docker Compose]
        IMG --> K8S[Kubernetes Deployment]
        DC --> APP
        K8S --> SVC[Kubernetes Service]
        SVC --> PODS[TaskFlow Pods]

        TF[Terraform] --> K8S
        AN[Ansible] --> K8S

        PROM[Prometheus] --> G[Grafana]
        PODS --> LOG[Fluent Bit]
        LOG --> ES[Elasticsearch]
        ES --> KB[Kibana]

        SONAR[SonarQube] --> SEC[Security Analysis]
        K8S --> BG[Blue-Green Deployment]
```

## Architecture Notes

- GitHub stores source code and DevOps configuration.
- Jenkins performs checkout, dependency installation, automated tests and Docker image building.
- Docker Compose runs the local application and supporting services.
- Kubernetes provides orchestration, services and persistent storage.
- Terraform provisions Kubernetes resources using a reusable module.
- Ansible provides configuration management and deployment automation.
- Prometheus and Grafana provide monitoring.
- Fluent Bit, Elasticsearch and Kibana provide centralized logging.
- SonarQube supports static code analysis.
- Blue-Green deployment configuration is maintained in Kubernetes manifests.
- ArgoCD is not included in this diagram because repository-managed GitOps configuration has not yet been verified.
