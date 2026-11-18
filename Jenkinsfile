pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Python Environment') {
            steps {
                sh 'python3 -m venv .venv'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '.venv/bin/pip install --upgrade pip'
                sh '.venv/bin/pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '.venv/bin/python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t taskflow-app:${BUILD_NUMBER} .'
            }
        }
    }
}
