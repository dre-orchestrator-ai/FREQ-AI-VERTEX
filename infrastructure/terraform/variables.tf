# =============================================================================
# FREQ AI INFRASTRUCTURE - Variables
# =============================================================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "bedrock_model_id" {
  description = "Bedrock model ID for Claude Opus 4.5"
  type        = string
  default     = "anthropic.claude-opus-4-5-20251101-v1:0"
}

variable "enable_xray" {
  description = "Enable AWS X-Ray tracing"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

variable "iron_vault_retention_days" {
  description = "Days before archiving data in Iron Vault"
  type        = number
  default     = 2555  # ~7 years for regulatory compliance
}
