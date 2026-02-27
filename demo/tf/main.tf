resource "aws_security_group" "bad" {
  name = "open-sg"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_s3_bucket" "public" {
  bucket = "demo-public-bucket"
  acl    = "public-read"
}
