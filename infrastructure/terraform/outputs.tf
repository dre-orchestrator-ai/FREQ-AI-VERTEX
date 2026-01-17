# =============================================================================
# FREQ AI INFRASTRUCTURE - Outputs
# =============================================================================

# =============================================================================
# LAMBDA FUNCTIONS
# =============================================================================

output "lambda_function_arns" {
  description = "ARNs of all lattice node Lambda functions"
  value = {
    for key, lambda in aws_lambda_function.lattice_nodes :
    key => lambda.arn
  }
}

output "lambda_function_names" {
  description = "Names of all lattice node Lambda functions"
  value = {
    for key, lambda in aws_lambda_function.lattice_nodes :
    key => lambda.function_name
  }
}

# =============================================================================
# SQS QUEUES
# =============================================================================

output "semantic_bus_url" {
  description = "URL of the Semantic Bus SQS queue"
  value       = aws_sqs_queue.semantic_bus.url
}

output "semantic_bus_arn" {
  description = "ARN of the Semantic Bus SQS queue"
  value       = aws_sqs_queue.semantic_bus.arn
}

output "node_queue_urls" {
  description = "URLs of node-specific SQS queues"
  value = {
    for key, queue in aws_sqs_queue.node_queues :
    key => queue.url
  }
}

# =============================================================================
# DYNAMODB TABLES
# =============================================================================

output "missions_table_name" {
  description = "Name of the missions DynamoDB table"
  value       = aws_dynamodb_table.missions.name
}

output "missions_table_arn" {
  description = "ARN of the missions DynamoDB table"
  value       = aws_dynamodb_table.missions.arn
}

output "audit_trail_table_name" {
  description = "Name of the audit trail DynamoDB table"
  value       = aws_dynamodb_table.audit_trail.name
}

output "audit_trail_table_arn" {
  description = "ARN of the audit trail DynamoDB table"
  value       = aws_dynamodb_table.audit_trail.arn
}

output "governance_table_name" {
  description = "Name of the governance DynamoDB table"
  value       = aws_dynamodb_table.governance.name
}

# =============================================================================
# S3 BUCKETS
# =============================================================================

output "iron_vault_bucket" {
  description = "Name of the Iron Vault S3 bucket"
  value       = aws_s3_bucket.iron_vault.id
}

output "iron_vault_arn" {
  description = "ARN of the Iron Vault S3 bucket"
  value       = aws_s3_bucket.iron_vault.arn
}

output "lambda_artifacts_bucket" {
  description = "Name of the Lambda artifacts S3 bucket"
  value       = aws_s3_bucket.lambda_artifacts.id
}

# =============================================================================
# IOT CORE
# =============================================================================

output "iot_drone_policy_name" {
  description = "Name of the IoT policy for drones"
  value       = aws_iot_policy.drone_policy.name
}

output "iot_endpoint" {
  description = "IoT Core endpoint for drone connections"
  value       = data.aws_iot_endpoint.current.endpoint_address
}

# =============================================================================
# IAM
# =============================================================================

output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

# =============================================================================
# CLOUDWATCH
# =============================================================================

output "dashboard_url" {
  description = "URL to the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.lattice.dashboard_name}"
}

# =============================================================================
# SUMMARY
# =============================================================================

output "deployment_summary" {
  description = "Summary of deployed resources"
  value = {
    environment      = var.environment
    region           = var.aws_region
    lambda_count     = length(aws_lambda_function.lattice_nodes)
    sqs_queues       = length(aws_sqs_queue.node_queues) + 1
    dynamodb_tables  = 3
    s3_buckets       = 2
    iot_topic_rules  = 2
  }
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_iot_endpoint" "current" {
  endpoint_type = "iot:Data-ATS"
}
