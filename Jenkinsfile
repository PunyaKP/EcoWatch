pipeline {
    agent any

    environment {
        AWS_REGION       = 'ap-south-1'
        ECR_REPO         = 'ecowatch-app'
        AWS_ACCOUNT_ID   = credentials('AWS_ACCOUNT_ID')
        ECR_REGISTRY     = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        IMAGE_TAG        = "${env.BUILD_NUMBER}"
        EC2_HOST         = credentials('EC2_HOST')
        EC2_USER         = 'ubuntu'
        SECRET_KEY       = credentials('ECOWATCH_SECRET_KEY')
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling code from GitHub...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${ECR_REPO}:${IMAGE_TAG} .
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    docker tag ${ECR_REPO}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:latest
                """
            }
        }

        stage('Push to AWS ECR') {
            steps {
                echo '☁️ Pushing to Amazon ECR...'
                sh """
                    aws ecr get-login-password --region ${AWS_REGION} | \
                    docker login --username AWS --password-stdin ${ECR_REGISTRY}

                    docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    docker push ${ECR_REGISTRY}/${ECR_REPO}:latest
                """
            }
        }

        stage('Deploy to AWS EC2') {
            steps {
                echo '🚀 Deploying to EC2...'
                sshagent(['EC2_SSH_KEY']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                            aws ecr get-login-password --region ${AWS_REGION} | \
                            docker login --username AWS --password-stdin ${ECR_REGISTRY}

                            docker pull ${ECR_REGISTRY}/${ECR_REPO}:latest

                            docker stop ecowatch || true
                            docker rm ecowatch   || true

                            docker run -d \
                              --name ecowatch \
                              --restart unless-stopped \
                              -p 80:5000 \
                              -e SECRET_KEY=${SECRET_KEY} \
                              -v /home/ubuntu/ecowatch-uploads:/app/uploads \
                              ${ECR_REGISTRY}/${ECR_REPO}:latest
                        '
                    """
                }
            }
        }

        stage('Health Check') {
            steps {
                echo '🏥 Checking deployment health...'
                sh "sleep 10 && curl -f http://${EC2_HOST}/health || exit 1"
            }
        }
    }

    post {
        success {
            echo '✅ EcoWatch deployed successfully!'
        }
        failure {
            echo '❌ Deployment failed — check logs above'
        }
        always {
            sh 'docker image prune -f || true'
        }
    }
}