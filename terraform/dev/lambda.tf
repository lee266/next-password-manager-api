data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../lambda_code/lambda.py"
  output_path = "../lambda_code/lambda.zip"
}

resource "aws_iam_role" "lambda_ec2_role" {
  name = "lambda-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "lambda-ec2-role"
  }
}

resource "aws_iam_role_policy" "lambda_ec2_policy" {
  name = "lambda-ec2-policy"
  role = aws_iam_role.lambda_ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "ec2:DescribeInstances",
          "ec2:StartInstances",
          "ec2:StopInstances"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:ec2:*:*:instance/*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

resource "aws_lambda_function" "ec2_controller" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "ec2-start-stop-by-tag"
  role             = aws_iam_role.lambda_ec2_role.arn
  handler          = "lambda.lambda_handler"
  runtime          = "python3.13"
  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)
  timeout          = 60
  region           = var.aws_region
}

resource "aws_cloudwatch_event_rule" "start_ec2" {
  name                = "start-ec2"
  schedule_expression = var.start_schedule
  region              = var.aws_region
}

resource "aws_cloudwatch_event_rule" "stop_ec2" {
  name                = "stop-ec2"
  schedule_expression = var.stop_schedule
  region              = var.aws_region
}

resource "aws_cloudwatch_event_target" "start_target" {
  rule      = aws_cloudwatch_event_rule.start_ec2.name
  target_id = "start-ec2"
  arn       = aws_lambda_function.ec2_controller.arn
}

resource "aws_cloudwatch_event_target" "stop_target" {
  rule      = aws_cloudwatch_event_rule.stop_ec2.name
  target_id = "stop-ec2"
  arn       = aws_lambda_function.ec2_controller.arn
}

resource "aws_lambda_permission" "allow_eventbridge_start" {
  statement_id  = "AllowExecutionFromEventBridgeStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_controller.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_ec2.arn
  region        = var.aws_region
}

resource "aws_lambda_permission" "allow_eventbridge_stop" {
  statement_id  = "AllowExecutionFromEventBridgeStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_controller.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.stop_ec2.arn
  region       = var.aws_region
}
