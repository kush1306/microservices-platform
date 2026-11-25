# Microservices Platform – Cloud Infrastructure & CI/CD

A cloud-native microservices platform built using Python, FastAPI, Docker, Kubernetes, Jenkins, Terraform, and AWS. This project demonstrates containerization, CI/CD automation, infrastructure provisioning, and deployment of multiple independent services on Amazon EKS.

## Project Overview

The platform consists of six independent microservices developed using FastAPI. Each service runs in its own Docker container and communicates with other services through defined APIs.

The infrastructure is provisioned using Terraform, while Jenkins automates the CI/CD workflow. Docker images are stored in Amazon Elastic Container Registry (ECR), and Kubernetes manages application deployment and orchestration on Amazon EKS.

## Architecture

```text
                 Developer
                     |
                     v
                GitHub Repository
                     |
                     v
                Jenkins Pipeline
                     |
          +----------+----------+
          |                     |
          v                     v
    Docker Build          Terraform
          |                     |
          v                     v
      AWS ECR              AWS Infrastructure
          |                     |
          +----------+----------+
                     |
                     v
                Amazon EKS
                     |
          +----------+----------+
          |          |          |
          v          v          v
       Service 1  Service 2  Service 3
          |          |          |
          +----------+----------+
                     |
              Other Services
```

## Microservices

| Service | Responsibility |
|---|---|
| Authentication Service | Handles authentication-related operations |
| User Service | Manages user-related operations |
| Product Service | Handles product information |
| Inventory Service | Manages inventory operations |
| Order Service | Handles order processing |
| Notification Service | Handles notification-related operations |

Each microservice is independently containerized and deployed.

## Technology Stack

**Programming & Frameworks**
- Python
- FastAPI
- REST APIs

**Containerization & Orchestration**
- Docker
- Docker Compose
- Kubernetes
- Amazon EKS

**CI/CD & Version Control**
- Jenkins
- Git
- GitHub

**Cloud & Infrastructure**
- Amazon Web Services (AWS)
- Amazon EC2
- Amazon ECR
- Amazon EKS
- Amazon S3
- IAM
- Security Groups
- Terraform (HCL)

**Storage**
- Kubernetes Persistent Volumes
- Persistent Volume Claims (PVC)
- AWS EBS CSI
- GP3 Storage

## DevOps Implementation

### 1. Containerization
- Created Dockerfiles for individual microservices.
- Built container images for each service.
- Used Docker Compose for local multi-container orchestration.
- Configured service networking and environment variables.

### 2. CI/CD with Jenkins
- Integrated Jenkins with the GitHub repository.
- Configured a Jenkins pipeline to automate application build and deployment-related tasks.
- Automated Docker image building.
- Used AWS ECR as the container image registry.

### 3. Infrastructure as Code with Terraform
- Used Terraform to provision AWS infrastructure.
- Managed infrastructure configuration through reusable HCL definitions.
- Provisioned EC2-based infrastructure and supporting AWS resources.
- Configured networking and security-related resources.

### 4. Kubernetes Deployment on Amazon EKS
- Deployed containerized microservices to Amazon EKS.
- Created Kubernetes Deployments and Services.
- Used ClusterIP Services for internal service communication.
- Configured container health probes.
- Implemented persistent storage using Persistent Volume Claims and AWS EBS CSI with GP3 volumes.

### 5. AWS Security and Access Management
- Used IAM roles and policies for AWS access management.
- Worked with EKS Pod Identity for workload-level AWS permissions.
- Configured security groups to control network access.

## Key Learning Outcomes

- Hands-on experience with microservices architecture.
- Containerization and multi-container application management.
- CI/CD pipeline development using Jenkins.
- Infrastructure provisioning using Terraform.
- Kubernetes deployment and troubleshooting.
- Amazon EKS cluster and workload management.
- AWS IAM and workload identity concepts.
- Persistent storage configuration using Kubernetes and AWS EBS.

## Repository Structure

```text
microservices-platform/
│
├── services/
│   ├── auth-service/
│   ├── user-service/
│   ├── product-service/
│   ├── inventory-service/
│   ├── order-service/
│   └── notification-service/
│
├── kubernetes/
│   ├── k8s-deployment.yaml
│   └── ...
│
├── terraform/
│   └── ...
│
├── jenkins/
│   └── Jenkinsfile
│
├── docker-compose.yml
│
└── README.md
```

*Note: Repository structure may evolve as the project develops.*

## Project Status

This project was developed as a hands-on DevOps and cloud engineering implementation, covering containerization, infrastructure as code, CI/CD workflows, Kubernetes orchestration, and AWS integration.

---

**Author:** Kush Arora

**GitHub:** https://github.com/kush1306

**Project Repository:** https://github.com/kush1306/microservices-platform
