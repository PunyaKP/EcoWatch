pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ecowatch .'
            }
        }

        stage('Stop Old Container') {
            steps {
                bat 'docker stop ecowatch || exit 0'
                bat 'docker rm ecowatch || exit 0'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d --name ecowatch -p 5000:5000 ecowatch'
            }
        }
    }
}