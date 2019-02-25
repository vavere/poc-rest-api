
resource "aws_api_gateway_rest_api" "poc_api" {
  name = "poc_api"
}

resource "aws_lambda_permission" "poc_api_invoke_perms" {
  statement_id = "allow_poc_api_invoke"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.poc_lambda.arn}"
  principal = "apigateway.amazonaws.com"
  source_arn = "${aws_api_gateway_rest_api.poc_api.execution_arn}/*/*/*"
}

resource "aws_api_gateway_method" "any_root" {
  rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
  resource_id = "${aws_api_gateway_rest_api.poc_api.root_resource_id}"
  http_method = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "any_root_integration" {
  rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
  resource_id = "${aws_api_gateway_rest_api.poc_api.root_resource_id}"
  http_method = "${aws_api_gateway_method.any_root.http_method}"
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.poc_lambda.arn}/invocations"
}
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
  parent_id = "${aws_api_gateway_rest_api.poc_api.root_resource_id}"
  path_part = "{proxy+}"
}

resource "aws_api_gateway_method" "any_proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
  resource_id = "${aws_api_gateway_resource.proxy.id}"
  http_method = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "any_proxy_integration" {
  rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
  resource_id = "${aws_api_gateway_resource.proxy.id}"
  http_method = "${aws_api_gateway_method.any_proxy.http_method}"
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = "arn:aws:apigateway:${var.region}:lambda:path/2015-03-31/functions/${aws_lambda_function.poc_lambda.arn}/invocations"
}

resource "aws_api_gateway_deployment" "dev" {
 depends_on = ["aws_api_gateway_integration.any_root_integration", "aws_api_gateway_integration.any_proxy_integration"]
 rest_api_id = "${aws_api_gateway_rest_api.poc_api.id}"
 stage_name = "dev"
}