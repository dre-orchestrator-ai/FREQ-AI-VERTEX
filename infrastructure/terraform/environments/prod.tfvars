# =============================================================================
# FREQ AI - Production Environment
# =============================================================================

aws_region  = "us-east-1"
environment = "prod"

# Bedrock Model
bedrock_model_id = "anthropic.claude-opus-4-5-20251101-v1:0"

# Observability
enable_xray        = true
log_retention_days = 90

# Data retention (7 years for regulatory compliance)
iron_vault_retention_days = 2555
