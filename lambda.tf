variable "database" {
  default = "poc_db"
}

resource "aws_db_instance" "poc_db" {
  identifier = "pocdb"
  allocated_storage = 20
  storage_type = "gp2"
  engine = "mysql"
  instance_class = "db.t3.micro"
  name = "${var.database}"
  username = "${var.username}"
  password = "${var.password}"
  db_subnet_group_name = "${aws_db_subnet_group.poc_subnet_group.id}"
  vpc_security_group_ids = ["${list("${aws_security_group.poc_sec_grp.id}")}"]
  skip_final_snapshot  = true
}

resource "aws_iam_role" "poc_lambda_role" {
  name = "lambda-vpc-execution-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "poc_role_policy" {
    role = "${aws_iam_role.poc_lambda_role.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

data "archive_file" "lambda" {
  type = "zip"
  source_dir ="lambda"
  output_path = "app.zip"
}

resource "aws_lambda_function" "poc_lambda" {
  filename = "app.zip"
  function_name = "poc_lambda"
  role  = "arn:aws:iam::${var.account_id}:role/lambda-vpc-execution-role"
  handler = "app.handler"
  runtime = "python3.7"
  source_code_hash = "${base64sha256(file("${data.archive_file.lambda.output_path}"))}"
  vpc_config {
    subnet_ids = ["${aws_subnet.poc_subnet_a.id}", "${aws_subnet.poc_subnet_b.id}", "${aws_subnet.poc_subnet_c.id}"]
    security_group_ids = ["${list("${aws_security_group.poc_sec_grp.id}")}"]
  }
  environment {
    variables = {
      rds_endpoint = "${aws_db_instance.poc_db.endpoint}"
      rds_database = "${var.database}"
      rds_username = "${var.username}"
      rds_password = "${var.password}"
    }
  }
}
