# advanced-rag-document-querying-portal

## Commands to be follwed:
```
conda create -n documentqueryingportal python = 3.10
```
```
conda activate documentqueryingportal
```

To install all packages required for this project:
pip install -r requirements.txt


What all should be having for this project
1. LLM model: open ai, groq, gemini, claude, hugging face
2. Embedding model: open ai, huggingface, gemini
3. vector database: ##inmemory ##ondisk ##cloud-based db

## why do we need setuptools
We use the setuptools library to package our project as a Python package so it can be installed and imported like any other libraries.

When we run:
```
pip install -e .
```

pip uses setuptools to install the project. The -e means editable mode (development mode). Instead of copying the code, Python creates a link to the project directory. During this process, setuptools creates a .egg-info folder.

This folder stores metadata about the project, such as:

1. project name
2. version
3. dependencies
4. author

This metadata helps pip and Python manage the package including installation, dependency tracking, and uninstallation.

To run this application: 
uvicorn api.main:app --reload, uvicorn api.main:app --port 8080 --reload
uvicorn is server to run an application.

Build Docker image:
                    docker build -t rag-based-document-portal .

Run docker container: 
                    docker run -d -p 8093:8080 --name rag-doc-portal rag-based-document-portal

Access swagger page: 
                    http://localhost:8093/docs

To Run tests: pytest tests/unit_tests.py -v

##Setup Pre hook 
cd ~/Documents/Advanced-RAG-Based-Document-Querying-Platform

touch .git/hooks/pre-push
chmod +x .git/hooks/pre-push

nano .git/hooks/pre-push

#!/bin/bash

echo "Running tests before push..."

PYTHONPATH=. pytest tests/
if [ $? -ne 0 ]; then
  echo "Tests failed. Push aborted."
  exit 1
fi

echo "Tests passed. Proceeding with push..."


AWS Setup for CI/CD (ECR + GitHub Actions)
1. Create ECR Repository

Create an Amazon ECR repository to store your Docker images.

Note down the repository name:

ECR_REPOSITORY = documentportal

After pushing your image, you will get an image URI like:

<aws_account_id>.dkr.ecr.<region>.amazonaws.com/documentportal:latest

Use this URI in deployment :

ContainerDefinitions:
  - Name: document-portal-container
    Image: <ECR_IMAGE_URI>

2. Create IAM User for GitHub Actions

Create an IAM user to allow GitHub Actions to push images to ECR.

Steps:
Go to AWS IAM Console
Create a new user (e.g., github-actions-user)
Attach required permissions:
AmazonEC2ContainerRegistryFullAccess (or scoped permissions for production)
Generate:
Access Key ID
Secret Access Key

3. Add Credentials to GitHub Secrets

Go to your repository settings:

GitHub repository secrets

Then: Navigate to:

Settings → Secrets and variables → Actions
Click "New repository secret"
Add the following secrets:

Store API keys in AWS Secrets Manager. (OPEN_API_KEY, GROQ_API)

Create an ECS cluster (Fargate or EC2).

Create a task definition using your container configuration:

https://ap-southeast-2.console.aws.amazon.com/ecs/v2/task-definitions/documentportaltd/1/containers



ADD IAM ROLE:
The ecsTaskExecutionRole allows ECS tasks to:

                        Pull container images from ECR
                        Send logs to CloudWatch
                        Retrieve secrets from AWS Secrets Manager

1.Go to IAM Console
Open AWS Console
Navigate to IAM (Identity and Access Management)
Click Roles → Create role

2.Select Trusted Entity:
Choose: AWS service
Service: Elastic Container Service
Use case: Elastic Container Service Task

3.Attach Permissions:
Attach the following AWS-managed policy:
            AmazonECSTaskExecutionRolePolicy
4.Create TWO separate inline policies under the same role.
Policy 1: AllowECSLogs
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowECSLogs",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
🔵 Policy 2: AllowSecretsAccess
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSecretsAccess",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:ap-southeast-2:459497895986:secret:api_keys-nZTtj8*"
    }
  ]
}