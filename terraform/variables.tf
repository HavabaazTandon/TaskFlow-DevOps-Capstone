variable "namespace" {
  description = "Kubernetes namespace for TaskFlow"
  type        = string
  default     = "taskflow-terraform"
}

variable "app_name" {
  description = "TaskFlow application name"
  type        = string
  default     = "taskflow"
}

variable "image" {
  description = "Container image"
  type        = string
  default     = "taskflow-app:k8s"
}

variable "replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 1
}

variable "secret_key" {
  description = "Flask application secret key"
  type        = string
  sensitive   = true
}
