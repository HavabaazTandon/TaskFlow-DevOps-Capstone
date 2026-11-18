pipeline {
    agent any

    environment {
        TASKFLOW_SECRET = credentials('taskflow-app-secret')
    }

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
                sh 'test -n "$TASKFLOW_SECRET" && SECRET_KEY="$TASKFLOW_SECRET" .venv/bin/python -m pytest -v'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t taskflow-app:${BUILD_NUMBER} .'
            }
        }
    }
}
