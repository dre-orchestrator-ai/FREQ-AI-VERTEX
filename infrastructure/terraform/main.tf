# =============================================================================
# FREQ AI INFRASTRUCTURE - Main Configuration
# =============================================================================
# Terraform configuration for the FREQ AI Sophisticated Operational Lattice
# Deployed on AWS with Bedrock, Lambda, IoT Core, and supporting services
# =============================================================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Remote state configuration (uncomment for production)
  # backend "s3" {
  #   bucket         = "freq-ai-terraform-state"
  #   key            = "lattice/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "freq-ai-terraform-locks"
  # }
}

# =============================================================================
# PROVIDER CONFIGURATION
# =============================================================================

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "FREQ-AI"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "ChiefDre"
    }
  }
}

# =============================================================================
# DATA SOURCES
# =============================================================================

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# =============================================================================
# LOCAL VALUES
# =============================================================================

locals {
  account_id = data.aws_caller_identity.current.account_id
  region     = data.aws_region.current.name

  # Naming convention
  name_prefix = "freq-ai-${var.environment}"

  # Lattice node configuration
  lattice_nodes = {
    ssc = {
      name        = "Strategic Synthesis Core"
      level       = 1
      memory      = 1024
      timeout     = 120
      substrate   = "opus-4.5"
    }
    cge = {
      name        = "Cognitive Governance Engine"
      level       = 2
      memory      = 512
      timeout     = 60
      substrate   = "opus-4.5"
    }
    sil = {
      name        = "Strategic Intelligence Lead"
      level       = 3
      memory      = 512
      timeout     = 60
      substrate   = "gemini-flash"
    }
    sa = {
      name        = "System Architect"
      level       = 4
      memory      = 512
      timeout     = 60
      substrate   = "gemini-pro"
    }
    tom = {
      name        = "Runtime Realization Node"
      level       = 5
      memory      = 1024
      timeout     = 30
      substrate   = "gemini-flash"
    }
  }

  # Common tags for all resources
  common_tags = {
    Project     = "FREQ-AI"
    Environment = var.environment
    Lattice     = "SOL-v2"
  }
}

# =============================================================================
# S3 BUCKETS - Iron Vault & Artifacts
# =============================================================================

# Iron Vault - Raw mission data storage
resource "aws_s3_bucket" "iron_vault" {
  bucket = "${local.name_prefix}-iron-vault"

  tags = merge(local.common_tags, {
    Purpose = "Raw mission data storage"
  })
}

resource "aws_s3_bucket_versioning" "iron_vault" {
  bucket = aws_s3_bucket.iron_vault.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "iron_vault" {
  bucket = aws_s3_bucket.iron_vault.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "iron_vault" {
  bucket = aws_s3_bucket.iron_vault.id

  rule {
    id     = "archive-old-data"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    expiration {
      days = 2555  # 7 years for regulatory compliance
    }
  }
}

# Lambda deployment artifacts
resource "aws_s3_bucket" "lambda_artifacts" {
  bucket = "${local.name_prefix}-lambda-artifacts"

  tags = merge(local.common_tags, {
    Purpose = "Lambda deployment packages"
  })
}

# =============================================================================
# DYNAMODB TABLES - State & Audit
# =============================================================================

# Mission state table
resource "aws_dynamodb_table" "missions" {
  name         = "${local.name_prefix}-missions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "mission_id"

  attribute {
    name = "mission_id"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  global_secondary_index {
    name            = "status-index"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = merge(local.common_tags, {
    Purpose = "Mission state tracking"
  })
}

# Cognitive Audit Trail
resource "aws_dynamodb_table" "audit_trail" {
  name         = "${local.name_prefix}-audit-trail"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "entry_id"

  attribute {
    name = "entry_id"
    type = "S"
  }

  attribute {
    name = "node_type"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  global_secondary_index {
    name            = "node-timestamp-index"
    hash_key        = "node_type"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = merge(local.common_tags, {
    Purpose = "Cognitive Audit Trail"
  })
}

# Governance decisions (VETO records)
resource "aws_dynamodb_table" "governance" {
  name         = "${local.name_prefix}-governance"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "decision_id"

  attribute {
    name = "decision_id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = merge(local.common_tags, {
    Purpose = "Governance decisions and VETO records"
  })
}

# =============================================================================
# SQS QUEUES - Semantic Bus
# =============================================================================

# Dead letter queue for failed messages
resource "aws_sqs_queue" "semantic_bus_dlq" {
  name                      = "${local.name_prefix}-semantic-bus-dlq.fifo"
  fifo_queue                = true
  message_retention_seconds = 1209600  # 14 days

  tags = merge(local.common_tags, {
    Purpose = "Dead letter queue for Semantic Bus"
  })
}

# Main Semantic Bus queue
resource "aws_sqs_queue" "semantic_bus" {
  name                        = "${local.name_prefix}-semantic-bus.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = 300
  message_retention_seconds   = 86400  # 1 day

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.semantic_bus_dlq.arn
    maxReceiveCount     = 3
  })

  tags = merge(local.common_tags, {
    Purpose = "Semantic Bus for inter-node communication"
  })
}

# Node-specific queues for parallel processing
resource "aws_sqs_queue" "node_queues" {
  for_each = local.lattice_nodes

  name                        = "${local.name_prefix}-${each.key}-queue.fifo"
  fifo_queue                  = true
  content_based_deduplication = true
  visibility_timeout_seconds  = each.value.timeout * 2
  message_retention_seconds   = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.semantic_bus_dlq.arn
    maxReceiveCount     = 3
  })

  tags = merge(local.common_tags, {
    Purpose = "Queue for ${each.value.name}"
    Level   = each.value.level
  })
}

# =============================================================================
# IAM ROLES - Lambda Execution
# =============================================================================

# Lambda execution role
resource "aws_iam_role" "lambda_execution" {
  name = "${local.name_prefix}-lambda-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# Bedrock access policy
resource "aws_iam_role_policy" "bedrock_access" {
  name = "bedrock-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:*::foundation-model/anthropic.claude-*",
          "arn:aws:bedrock:*:${local.account_id}:inference-profile/*"
        ]
      }
    ]
  })
}

# DynamoDB access policy
resource "aws_iam_role_policy" "dynamodb_access" {
  name = "dynamodb-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.missions.arn,
          "${aws_dynamodb_table.missions.arn}/index/*",
          aws_dynamodb_table.audit_trail.arn,
          "${aws_dynamodb_table.audit_trail.arn}/index/*",
          aws_dynamodb_table.governance.arn
        ]
      }
    ]
  })
}

# SQS access policy
resource "aws_iam_role_policy" "sqs_access" {
  name = "sqs-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = concat(
          [aws_sqs_queue.semantic_bus.arn],
          [for q in aws_sqs_queue.node_queues : q.arn]
        )
      }
    ]
  })
}

# S3 access policy
resource "aws_iam_role_policy" "s3_access" {
  name = "s3-access"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.iron_vault.arn,
          "${aws_s3_bucket.iron_vault.arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch Logs policy
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# =============================================================================
# IOT CORE - Drone Telemetry
# =============================================================================

# IoT Policy for drones
resource "aws_iot_policy" "drone_policy" {
  name = "${local.name_prefix}-drone-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = [
          "arn:aws:iot:${local.region}:${local.account_id}:client/freq-drone-*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = [
          "arn:aws:iot:${local.region}:${local.account_id}:topic/freq/drone/*/telemetry",
          "arn:aws:iot:${local.region}:${local.account_id}:topic/freq/drone/*/scan/*",
          "arn:aws:iot:${local.region}:${local.account_id}:topic/freq/drone/*/alert"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe"
        ]
        Resource = [
          "arn:aws:iot:${local.region}:${local.account_id}:topicfilter/freq/drone/*/command"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Receive"
        ]
        Resource = [
          "arn:aws:iot:${local.region}:${local.account_id}:topic/freq/drone/*/command"
        ]
      }
    ]
  })
}

# IoT Topic Rule - Route telemetry to Lambda
resource "aws_iot_topic_rule" "drone_telemetry" {
  name        = "${replace(local.name_prefix, "-", "_")}_drone_telemetry"
  description = "Route drone telemetry to TOM Lambda"
  enabled     = true
  sql         = "SELECT * FROM 'freq/drone/+/telemetry'"
  sql_version = "2016-03-23"

  lambda {
    function_arn = aws_lambda_function.lattice_nodes["tom"].arn
  }

  error_action {
    cloudwatch_logs {
      log_group_name = aws_cloudwatch_log_group.iot_errors.name
      role_arn       = aws_iam_role.iot_logging.arn
    }
  }

  tags = local.common_tags
}

# IoT Topic Rule - Scan complete notifications
resource "aws_iot_topic_rule" "scan_complete" {
  name        = "${replace(local.name_prefix, "-", "_")}_scan_complete"
  description = "Route scan completion to processing"
  enabled     = true
  sql         = "SELECT * FROM 'freq/drone/+/scan/complete'"
  sql_version = "2016-03-23"

  sqs {
    queue_url  = aws_sqs_queue.node_queues["tom"].url
    role_arn   = aws_iam_role.iot_sqs.arn
    use_base64 = false
  }

  tags = local.common_tags
}

# IAM role for IoT to SQS
resource "aws_iam_role" "iot_sqs" {
  name = "${local.name_prefix}-iot-sqs"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "iot.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "iot_sqs" {
  name = "sqs-publish"
  role = aws_iam_role.iot_sqs.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sqs:SendMessage"
        Resource = aws_sqs_queue.node_queues["tom"].arn
      }
    ]
  })
}

# IAM role for IoT logging
resource "aws_iam_role" "iot_logging" {
  name = "${local.name_prefix}-iot-logging"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "iot.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "iot_logging" {
  name = "cloudwatch-logs"
  role = aws_iam_role.iot_logging.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.iot_errors.arn}:*"
      }
    ]
  })
}

# =============================================================================
# CLOUDWATCH - Observability
# =============================================================================

# Log group for lattice nodes
resource "aws_cloudwatch_log_group" "lattice_nodes" {
  for_each = local.lattice_nodes

  name              = "/aws/lambda/${local.name_prefix}-${each.key}"
  retention_in_days = 30

  tags = merge(local.common_tags, {
    Node  = each.value.name
    Level = each.value.level
  })
}

# Log group for IoT errors
resource "aws_cloudwatch_log_group" "iot_errors" {
  name              = "/aws/iot/${local.name_prefix}-errors"
  retention_in_days = 30

  tags = local.common_tags
}

# Dashboard for lattice monitoring
resource "aws_cloudwatch_dashboard" "lattice" {
  dashboard_name = "${local.name_prefix}-lattice-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda Invocations by Node"
          region = local.region
          metrics = [
            for key, node in local.lattice_nodes : [
              "AWS/Lambda", "Invocations",
              "FunctionName", "${local.name_prefix}-${key}",
              { label = "${node.name} (L${node.level})" }
            ]
          ]
          stat   = "Sum"
          period = 60
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          title  = "Lambda Duration (FREQ LAW: <2000ms)"
          region = local.region
          metrics = [
            for key, node in local.lattice_nodes : [
              "AWS/Lambda", "Duration",
              "FunctionName", "${local.name_prefix}-${key}",
              { label = "${node.name}" }
            ]
          ]
          stat   = "Average"
          period = 60
          annotations = {
            horizontal = [
              {
                label = "FREQ LAW Limit"
                value = 2000
                color = "#ff0000"
              }
            ]
          }
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "Semantic Bus Messages"
          region = local.region
          metrics = [
            ["AWS/SQS", "NumberOfMessagesSent", "QueueName", "${local.name_prefix}-semantic-bus.fifo"],
            ["AWS/SQS", "NumberOfMessagesReceived", "QueueName", "${local.name_prefix}-semantic-bus.fifo"],
            ["AWS/SQS", "ApproximateNumberOfMessagesVisible", "QueueName", "${local.name_prefix}-semantic-bus.fifo"]
          ]
          stat   = "Sum"
          period = 60
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "Lambda Errors"
          region = local.region
          metrics = [
            for key, node in local.lattice_nodes : [
              "AWS/Lambda", "Errors",
              "FunctionName", "${local.name_prefix}-${key}",
              { label = "${node.name}" }
            ]
          ]
          stat   = "Sum"
          period = 60
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 6
        width  = 8
        height = 6
        properties = {
          title  = "IoT Messages"
          region = local.region
          metrics = [
            ["AWS/IoT", "PublishIn.Success", { label = "Messages Received" }],
            ["AWS/IoT", "RuleMessageThrottled", { label = "Throttled" }]
          ]
          stat   = "Sum"
          period = 60
        }
      }
    ]
  })
}

# =============================================================================
# LAMBDA FUNCTIONS - Lattice Nodes
# =============================================================================

resource "aws_lambda_function" "lattice_nodes" {
  for_each = local.lattice_nodes

  function_name = "${local.name_prefix}-${each.key}"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.11"
  timeout       = each.value.timeout
  memory_size   = each.value.memory

  # Placeholder - will be updated with actual deployment package
  filename         = data.archive_file.lambda_placeholder.output_path
  source_code_hash = data.archive_file.lambda_placeholder.output_base64sha256

  environment {
    variables = {
      NODE_TYPE          = each.key
      NODE_LEVEL         = each.value.level
      SUBSTRATE          = each.value.substrate
      SEMANTIC_BUS_QUEUE = aws_sqs_queue.semantic_bus.url
      NODE_QUEUE         = aws_sqs_queue.node_queues[each.key].url
      MISSIONS_TABLE     = aws_dynamodb_table.missions.name
      AUDIT_TABLE        = aws_dynamodb_table.audit_trail.name
      GOVERNANCE_TABLE   = aws_dynamodb_table.governance.name
      IRON_VAULT_BUCKET  = aws_s3_bucket.iron_vault.id
      ENVIRONMENT        = var.environment
      FREQ_LAW_LATENCY   = "2000"
    }
  }

  tags = merge(local.common_tags, {
    Node  = each.value.name
    Level = each.value.level
  })
}

# Lambda placeholder package
data "archive_file" "lambda_placeholder" {
  type        = "zip"
  output_path = "${path.module}/lambda_placeholder.zip"

  source {
    content  = <<-EOF
      def lambda_handler(event, context):
          return {
              'statusCode': 200,
              'body': 'FREQ AI Node - Placeholder'
          }
    EOF
    filename = "handler.py"
  }
}

# SQS trigger for each node
resource "aws_lambda_event_source_mapping" "node_sqs_triggers" {
  for_each = local.lattice_nodes

  event_source_arn = aws_sqs_queue.node_queues[each.key].arn
  function_name    = aws_lambda_function.lattice_nodes[each.key].arn
  batch_size       = 1
}

# IoT trigger permission for TOM
resource "aws_lambda_permission" "iot_tom" {
  statement_id  = "AllowIoTInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lattice_nodes["tom"].function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.drone_telemetry.arn
}
