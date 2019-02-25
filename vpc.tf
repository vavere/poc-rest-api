resource "aws_vpc" "poc_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "poc_vpc"
  }
}
resource "aws_security_group" "poc_sec_grp" {
  name = "poc_sec_grp"
  vpc_id = "${aws_vpc.poc_vpc.id}"
  ingress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["127.0.0.1/32"]
    self = true
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "poc_sec_grp"
  }
}

resource "aws_subnet" "poc_subnet_a" {
  vpc_id = "${aws_vpc.poc_vpc.id}"
  cidr_block = "10.0.1.0/24"
  availability_zone = "${var.region}a"
  tags = {
    Name = "poc_subnet_a"
  }
}

resource "aws_subnet" "poc_subnet_b" {
  vpc_id = "${aws_vpc.poc_vpc.id}"
  cidr_block = "10.0.2.0/24"
  availability_zone = "${var.region}b"
  tags = {
    Name = "poc_subnet_b"
  }
}

resource "aws_subnet" "poc_subnet_c" {
  vpc_id = "${aws_vpc.poc_vpc.id}"
  cidr_block = "10.0.3.0/24"
  availability_zone = "${var.region}c"
  tags = {
    Name = "poc_subnet_c"
  }
}

resource "aws_db_subnet_group" "poc_subnet_group" {
  name  = "main"
  subnet_ids = ["${aws_subnet.poc_subnet_a.id}", "${aws_subnet.poc_subnet_b.id}", "${aws_subnet.poc_subnet_c.id}"]
  tags = {
    Name = "poc_subnet_group"
  }
}
