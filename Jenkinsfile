pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/HavabaazTandon/TaskFlow-DevOps-Capstone.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python3 -m pip install --break-system-packages -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'python3 -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t taskflow-app:${BUILD_NUMBER} .'
            }
        }
    }
}
