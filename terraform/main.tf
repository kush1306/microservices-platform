provider "aws" {
    region = "us-east-1"
}
resource "aws_vpc" "microservices_platform_vpc"{
    cidr_block = "10.0.0.0/16"
    tags = {
        Name = "mp_vpc"
    }
}

resource "aws_internet_gateway" "microservices_platform_gw" {
  vpc_id = aws_vpc.microservices_platform_vpc.id

  tags = {
    Name = "microservices_platform_gw"
  }
}

resource "aws_route_table" "microservices_platform_route_table" {
  vpc_id = aws_vpc.microservices_platform_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.microservices_platform_gw.id
  }

  tags = {
    Name = "microservices_platform_route_table"
  }
}

resource "aws_subnet" "microservices_platform_subnet" {
    vpc_id = aws_vpc.microservices_platform_vpc.id
    cidr_block = "10.0.1.0/24"
    availability_zone = "us-east-1a"
    map_public_ip_on_launch = true
    tags = {
        Name = "mp_subnet"
    }
}

resource "aws_route_table_association" "microservices_platform_route_table_association" {
    subnet_id = aws_subnet.microservices_platform_subnet.id
    route_table_id = aws_route_table.microservices_platform_route_table.id
}

resource "aws_security_group" "microservices_platform_sg" {
    vpc_id = aws_vpc.microservices_platform_vpc.id
    name = "microservices_platform_sg"
    description = "Security group for microservices platform"
    ingress {
        from_port = 8000
        to_port = 8005
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["49.43.132.221/32"]
    }
    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
    tags = {
        Name = "mp_sg"
    }
}

resource "aws_instance" "microservices_platform_instance" {
    ami = "ami-0b6d9d3d33ba97d99"
    instance_type = "t2.micro"
    subnet_id = aws_subnet.microservices_platform_subnet.id
    vpc_security_group_ids = [aws_security_group.microservices_platform_sg.id]
    key_name = "mp_key"
    
    user_data = <<-EOF
       #!/bin/bash
       apt-get update
       apt-get install -y docker.io docker-compose-plugin
      systemctl enable docker
      systemctl start docker
EOF

    tags = {
        Name = "mp_instance"
    }
}
