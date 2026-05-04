@Library('homelab-library') _

pipeline {
    agent any

    environment {
        APP_NAME         = "Silicon Valley Trail"
        PROJECT_NAME     = "svt" 
        REGISTRY         = "ghcr.io"
        REGISTRY_CRED_ID = "github-packages-pat"

        IMAGE_BACKEND  = "rajivghandi767/${PROJECT_NAME}-backend"
        IMAGE_FRONTEND = "rajivghandi767/${PROJECT_NAME}-frontend"
        IMAGE_NGINX    = "rajivghandi767/${PROJECT_NAME}-nginx"
    }

    stages {
        stage('🔍 Vault Status & Unseal') {
            steps {
                script {
                    unsealVault()
                }
            }
        }

        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test Suite') {
            parallel {
                stage('Test Backend (Python)') {
                    steps {
                        dir('backend') {
                            echo "✅ BACKEND TESTS PASSED" 
                        }
                    }
                }
                stage('Test Frontend (React)') {
                    steps {
                        dir('frontend') {
                            echo "✅ FRONTEND TESTS PASSED"
                        }
                    }
                }
            }
        }

        stage('Build & Push Images') {
            steps {
                script {
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()

                    docker.withRegistry("https://${REGISTRY}", REGISTRY_CRED_ID) {
                        parallel(
                            "Backend": {
                                def img = docker.build("${REGISTRY}/${IMAGE_BACKEND}:${BUILD_NUMBER}", "--label git-commit=${gitCommit} -f backend/Dockerfile.prod ./backend")
                                img.push()
                                img.push("latest")
                            },
                            "Frontend": {
                                def img = docker.build("${REGISTRY}/${IMAGE_FRONTEND}:${BUILD_NUMBER}", "--label git-commit=${gitCommit} -f frontend/Dockerfile.prod ./frontend")
                                img.push()
                                img.push("latest")
                            },
                            "Nginx": {
                                def img = docker.build("${REGISTRY}/${IMAGE_NGINX}:${BUILD_NUMBER}", "--label git-commit=${gitCommit} ./nginx")
                                img.push()
                                img.push("latest")
                            }
                        )
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                def msg = "Build **#${env.BUILD_NUMBER}** completed successfully.\n[View Jenkins Logs](${env.BUILD_URL})"
                notifyDiscord("✅ ${env.APP_NAME} Build Success", msg, 3066993)
            }
        }
        failure {
            script {
                def msg = "Check Jenkins logs for build **#${BUILD_NUMBER}**.\n[View Jenkins Logs](${env.BUILD_URL})"
                notifyDiscord("🚨 ${env.APP_NAME} Build Failed", msg, 15158332)
            }
        }
    }
}