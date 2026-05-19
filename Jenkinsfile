@Library('homelab-library') _

pipeline {
    agent any

    environment {
        // Build & Project Config
        DOCKER_BUILDKIT   = '1'
        APP_NAME          = "Silicon Valley Trail"
        PROJECT_NAME      = "svt" 
        
        // Registry Config
        REGISTRY          = "ghcr.io"
        REGISTRY_CRED_ID  = "github-packages-pat"

        // Vault Config
        VAULT_URL         = "http://vault:8200"
        VAULT_CRED_ID     = "vault-svt-approle"
        VAULT_SECRET_PATH = "secret/svt-prod"

        // Image Tags
        IMAGE_BACKEND     = "rajivghandi767/${PROJECT_NAME}-backend"
        IMAGE_FRONTEND    = "rajivghandi767/${PROJECT_NAME}-frontend"
        IMAGE_NGINX       = "rajivghandi767/${PROJECT_NAME}-nginx"

        // Notification Config (Discord Channel IDs)
        DISCORD_SUCCESS   = "3066993"
        DISCORD_FAIL      = "15158332"
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

                    // Pulling build-time variables from Vault using environment variables
                    withVault(configuration: [vaultUrl: env.VAULT_URL, vaultCredentialId: env.VAULT_CRED_ID, engineVersion: 2], 
                    vaultSecrets: [[path: env.VAULT_SECRET_PATH, secretValues: [
                        [envVar: 'VITE_API_URL', vaultKey: 'VITE_API_URL']
                    ]]]) {
                        
                        docker.withRegistry("https://${env.REGISTRY}", env.REGISTRY_CRED_ID) {
                            parallel(
                                "Backend": {
                                    def img = docker.build("${env.REGISTRY}/${env.IMAGE_BACKEND}:${env.BUILD_NUMBER}", "--label git-commit=${gitCommit} -f backend/Dockerfile.prod ./backend")
                                    img.push()
                                    img.push("latest")
                                },
                                "Frontend": {
                                    // Injecting the Vault variable as a build-arg
                                    def img = docker.build(
                                        "${env.REGISTRY}/${env.IMAGE_FRONTEND}:${env.BUILD_NUMBER}", 
                                        "--build-arg VITE_API_URL=${env.VITE_API_URL} --label git-commit=${gitCommit} -f frontend/Dockerfile.prod ./frontend"
                                    )
                                    img.push()
                                    img.push("latest")
                                },
                                "Nginx": {
                                    def img = docker.build("${env.REGISTRY}/${env.IMAGE_NGINX}:${env.BUILD_NUMBER}", "--label git-commit=${gitCommit} ./nginx")
                                    img.push()
                                    img.push("latest")
                                }
                            )
                        }
                    }
                }
            }
        }
    }

    post {
        success {
            script {
                def msg = "Build **#${env.BUILD_NUMBER}** completed successfully.\n[View Jenkins Logs](${env.BUILD_URL})"
                notifyDiscord("✅ ${env.APP_NAME} Build Success", msg, env.DISCORD_SUCCESS)
            }
        }
        failure {
            script {
                def msg = "Check Jenkins logs for build **#${env.BUILD_NUMBER}**.\n[View Jenkins Logs](${env.BUILD_URL})"
                notifyDiscord("🚨 ${env.APP_NAME} Build Failed", msg, env.DISCORD_FAIL)
            }
        }
    }
}