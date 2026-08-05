# Deployment (AWS ECR + ECS via GitHub Actions)

This doc is my own notes on how I set up CI/CD for this project. It's mostly here so I don't forget how I wired it up.

## Pre-push test hook

Before pushing, I want tests to run automatically so a broken build never gets pushed. Setup:

```
cd ~/Documents/Advanced-RAG-Based-Document-Querying-Platform

touch .git/hooks/pre-push
chmod +x .git/hooks/pre-push

nano .git/hooks/pre-push
```

Contents of `.git/hooks/pre-push`:
```bash
#!/bin/bash

echo "Running tests before push..."

PYTHONPATH=. pytest tests/
if [ $? -ne 0 ]; then
  echo "Tests failed. Push aborted."
  exit 1
fi

echo "Tests passed. Proceeding with push..."
```

## 1. Create ECR repository

Create an Amazon ECR repository to store the Docker images.

Repository name: `documentportal`

After pushing an image, you get an image URI like:
```
<aws_account_id>.dkr.ecr.<region>.amazonaws.com/documentportal:latest
```
Use this URI in the ECS task definition:
```
ContainerDefinitions:
  - Name: document-portal-container
    Image: <ECR_IMAGE_URI>
```

## 2. Create an IAM user for GitHub Actions

This is the user GitHub Actions uses to push images to ECR.

Steps:
1. Go to the AWS IAM console.
2. Create a new user (e.g., `github-actions-user`).
3. Attach permissions: `AmazonEC2ContainerRegistryFullAccess` (or scope this down for production).
4. Generate an Access Key ID + Secret Access Key for it.

## 3. Add credentials to GitHub secrets

Repo settings → **Settings → Secrets and variables → Actions** → "New repository secret".

Add the Access Key ID and Secret Access Key from step 2 here.

The app's own API keys (`OPENAI_API_KEY`, `GROQ_API_KEY`) don't go here though, those get stored in AWS Secrets Manager instead. That's what the `secretsmanager:GetSecretValue` permission in step 5 is for, it lets the ECS task pull them at runtime.

## 4. ECS cluster + task definition

Create an ECS cluster (Fargate or EC2), then create a task definition using the container config above.

Task definition console for this project: `https://<region>.console.aws.amazon.com/ecs/v2/task-definitions/documentportaltd/1/containers`

## 5. IAM role for the ECS task (`ecsTaskExecutionRole`)

This role lets the running ECS task:
- pull the container image from ECR
- send logs to CloudWatch
- read secrets from AWS Secrets Manager

Steps:
1. IAM console → Roles → Create role.
2. Trusted entity: AWS service → Elastic Container Service → Elastic Container Service Task.
3. Attach the AWS-managed policy `AmazonECSTaskExecutionRolePolicy`.
4. Add two inline policies to the same role:

**AllowECSLogs**
```json
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
```

**AllowSecretsAccess**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSecretsAccess",
      "Effect": "Allow",
      "Action": "secretsmanager:GetSecretValue",
      "Resource": "arn:aws:secretsmanager:<region>:<aws_account_id>:secret:api_keys-*"
    }
  ]
}
```

> Note: swap `<region>` and `<aws_account_id>` for your own values, don't commit the real ARN or account ID to a public repo.
