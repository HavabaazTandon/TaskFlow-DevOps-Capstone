variable "namespace" {
  type = string
}

variable "app_name" {
  type = string
}

variable "image" {
  type = string
}

variable "replicas" {
  type = number
}

variable "secret_key" {
  type      = string
  sensitive = true
}

resource "kubernetes_namespace" "taskflow" {
  metadata {
    name = var.namespace
  }
}

resource "kubernetes_config_map" "taskflow" {
  metadata {
    name      = "${var.app_name}-config"
    namespace = kubernetes_namespace.taskflow.metadata[0].name
  }

  data = {
    APP_ENV  = "production"
    APP_PORT = "5002"
  }
}

resource "kubernetes_secret" "taskflow" {
  metadata {
    name      = "${var.app_name}-secret"
    namespace = kubernetes_namespace.taskflow.metadata[0].name
  }

  data = {
    SECRET_KEY = var.secret_key
  }

  type = "Opaque"
}

resource "kubernetes_persistent_volume_claim" "taskflow" {
  metadata {
    name      = "${var.app_name}-storage"
    namespace = kubernetes_namespace.taskflow.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

resource "kubernetes_deployment" "taskflow" {
  metadata {
    name      = var.app_name
    namespace = kubernetes_namespace.taskflow.metadata[0].name

    labels = {
      app = var.app_name
    }
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = {
          app = var.app_name
        }
      }

      spec {
        container {
          name              = var.app_name
          image             = var.image
          image_pull_policy = "IfNotPresent"

          port {
            container_port = 5002
          }

          env {
            name = "SECRET_KEY"

            value_from {
              secret_key_ref {
                name = kubernetes_secret.taskflow.metadata[0].name
                key  = "SECRET_KEY"
              }
            }
          }

          env {
            name = "APP_ENV"

            value_from {
              config_map_key_ref {
                name = kubernetes_config_map.taskflow.metadata[0].name
                key  = "APP_ENV"
              }
            }
          }

          volume_mount {
            name       = "taskflow-storage"
            mount_path = "/app/instance"
          }
        }

        volume {
          name = "taskflow-storage"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.taskflow.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "taskflow" {
  metadata {
    name      = "${var.app_name}-service"
    namespace = kubernetes_namespace.taskflow.metadata[0].name
  }

  spec {
    selector = {
      app = var.app_name
    }

    type = "NodePort"

    port {
      port        = 5002
      target_port = 5002
      node_port   = 30083
    }
  }
}

output "namespace" {
  value = kubernetes_namespace.taskflow.metadata[0].name
}

output "service_name" {
  value = kubernetes_service.taskflow.metadata[0].name
}

output "service_port" {
  value = kubernetes_service.taskflow.spec[0].port[0].node_port
}
