pipeline {
    agent any
    // Use a Docker agent to ensure a consistent and clean build environment
    agent {
        docker {
            image 'python:3.11-slim'
            args '-u root' // Run as root to install packages if needed
        }
    }

    environment {
        // Ensure Docker Hub username is set for image tagging
        DOCKER_HUB_USERNAME = 'surajgundla'
        // The name of your application's image
        IMAGE_NAME = "${DOCKER_HUB_USERNAME}/fitness-app"
        // Kubernetes namespace to deploy to
        K8S_NAMESPACE = 'default'
    }

    stages {
        stage('Checkout') {
            steps {
                // Get the latest code from the repository
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                // Commands are now run inside the python:3.11-slim container
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                // The JUnit plugin can publish these test results
                sh 'pip install pytest-cov'
                sh 'pytest --cov=ACEest_Fitness --cov-report=xml --junitxml=test-results.xml'
            }
        }

        stage('Build and Push Docker Image') {
            // This stage needs a different agent that has Docker installed.
            agent any
            steps {
                steps {
                    script {
                        // The 'dockerhub-credentials' ID must match the one you created in Jenkins
                        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                            def customImage = docker.build("${IMAGE_NAME}:${IMAGE_TAG}", '.')
                            // Push the uniquely tagged image
                            customImage.push()
                            // Also tag this build as 'latest' and push
                            customImage.push('latest')
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                // Use the withKubeConfig wrapper to securely access your cluster
                // 'kubeconfig' is the ID of your Secret File credential in Jenkins
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh 'kubectl get nodes' // Verify connection

                    // Apply the service. This usually only needs to be done once.
                    // The --dry-run and -o yaml flags are useful for debugging.
                    sh 'kubectl apply -f k8s/service.yaml'

                    // Apply the deployment. This will create or update it.
                    sh 'kubectl apply -f k8s/deployment.yaml'

                    // This is the key command for automation.
                    // It updates the image of the running deployment to the new version we just built.
                    echo "Updating deployment to image: ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "kubectl set image deployment/aceest-fitness-app aceest-fitness-container=${IMAGE_NAME}:${IMAGE_TAG}"

                    // Wait for the deployment to complete its rollout.
                    // The pipeline will fail here if the new pods can't start.
                    sh 'kubectl rollout status deployment/aceest-fitness-app'
                }
            }
        }
    } 
}