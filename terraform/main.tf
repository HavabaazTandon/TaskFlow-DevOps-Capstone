terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.35"
    }
  }
}

provider "kubernetes" {
  config_path    = pathexpand("~/.kube/config")
  config_context = "minikube"
}

module "taskflow" {
  source = "./modules/taskflow"

  namespace  = var.namespace
  app_name   = var.app_name
  image      = var.image
  replicas   = var.replicas
  secret_key = var.secret_key
}
