pipeline {
    agent any // We will define the agent for each stage

    environment {
        // Use the commit hash for a unique, traceable image tag.
        // We define it here so it's available in all stages.
        IMAGE_TAG = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
        IMAGE_NAME = "surajgundla/aceest-fitness"
    }

    stages {
        stage('Checkout') {
            steps {
                // Get the latest code from the repository
                checkout scm
            }
        }

        stage('Install Dependencies') {
            agent {
                docker { image 'python:3.11-slim' }
            }
            steps {
                // Commands are now run inside the python:3.11-slim container
                sh 'pip install --no-cache-dir -r requirements.txt'
            }
        }

        stage('Test and Build Image') {
            // This stage runs on a Docker-capable agent
            agent any
            steps {
                // Use a multi-stage Dockerfile that includes testing
                // This is a more modern approach that keeps the pipeline cleaner
                // and makes the build process more portable.
                sh 'docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f dockerfile .'
            }
        }

        stage('Push Docker Image') {
            // This stage also needs a Docker-capable agent
            agent any
            steps {
                // This post-build 'input' step is great for manual verification
                // before pushing an image that might be used by others.
                input "Image built. Proceed with push to Docker Hub?"
                script {
                    // The 'dockerhub-credentials' ID must match the one you created in Jenkins
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        
                        def customImage = docker.image("${IMAGE_NAME}:${IMAGE_TAG}")
                        // Push the uniquely tagged image
                        customImage.push()
                        // Also tag this build as 'latest' and push
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            // This stage needs kubectl configured
            agent any
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
                    echo "Updating Kubernetes deployment to image: ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "kubectl set image deployment/aceest-fitness-app aceest-fitness-container=${IMAGE_NAME}:${IMAGE_TAG}"

                    // Wait for the deployment to complete its rollout.
                    // The pipeline will fail here if the new pods can't start.
                    sh 'kubectl rollout status deployment/aceest-fitness-app'
                }
            }
        }
    } 
}