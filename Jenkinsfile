pipeline {
    agent any

    stages {
        stage('Build Docker Image') {
            steps {
                bat 'docker build -t ecowatch .'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker stop ecowatch'
                bat 'docker rm ecowatch'
            }
        }
    }
}