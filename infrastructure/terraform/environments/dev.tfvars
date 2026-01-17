# =============================================================================
# FREQ AI - Development Environment
# =============================================================================

aws_region  = "us-east-1"
environment = "dev"

# Bedrock Model
bedrock_model_id = "anthropic.claude-opus-4-5-20251101-v1:0"

# Observability
enable_xray        = true
log_retention_days = 7

# Data retention (shorter for dev)
iron_vault_retention_days = 30
