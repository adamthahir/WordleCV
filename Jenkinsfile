Jenkinsfile (Declarative Pipeline)
pipeline {
    agent { docker { image 'python:3.9.12-alpine' } }
    stages {
        stage('build') {
            steps {
                sh 'python --version'
            }
        }
    }
}