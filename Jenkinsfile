pipeline {
    agent any // We will define the agent for each stage

    environment {
        // Use the commit hash for a unique, traceable image tag.
        // We define it here so it's available in all stages.
        // Using a script block is more robust for capturing command output.
        IMAGE_TAG = "" 
        IMAGE_NAME = "surajgundla/aceest-fitness"
        // Define the name of the container and deployment for easier reference
        K8S_DEPLOYMENT_NAME = 'aceest-fitness-app'
        // This must match the 'name' field in your deployment.yaml container spec
        K8S_CONTAINER_NAME = 'aceest-fitness-container'
    }

    stages {
        stage('Checkout') {
            steps {
                // Get the latest code from the repository
                checkout scm
                // Set the IMAGE_TAG after checkout to ensure we have the git repo
                script {
                    IMAGE_TAG = bat(returnStdout: true, script: '@echo off & git rev-parse --short HEAD').trim()
                    echo "Building with IMAGE_TAG: ${IMAGE_TAG}"
                }
            }
        }

    

        stage('Test and Build Image') {
            // This stage runs on a Docker-capable agent
            agent any
            steps {
                // Use a multi-stage Dockerfile that includes testing
                // This is a more modern approach that keeps the pipeline cleaner.
                script {
                    def dockerBuildCmd = "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -f Dockerfile ."
                    bat dockerBuildCmd
                }
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
                        
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push()
                        // Push the uniquely tagged image
                        docker.image("${IMAGE_NAME}:${IMAGE_TAG}").push('latest')
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
                    bat 'kubectl get nodes' // Verify connection

                    // Apply the service. This usually only needs to be done once.
                    // The --dry-run and -o yaml flags are useful for debugging.
                    bat 'kubectl apply -f k8s/service.yaml'

                    // Apply the deployment. This will create or update it.
                    bat 'kubectl apply -f k8s/deployment.yaml'

                    // This is the key command for automation.
                    // It updates the image of the running deployment to the new version we just built.
                    echo "Updating Kubernetes deployment to image: ${IMAGE_NAME}:${IMAGE_TAG}"
                      bat "kubectl set image deployment/${K8S_DEPLOYMENT_NAME} ${K8S_CONTAINER_NAME}=${IMAGE_NAME}:${IMAGE_TAG}"

                    // Wait for the deployment to complete its rollout.
                    // The pipeline will fail here if the new pods can't start.
                    bat 'kubectl rollout status deployment/aceest-fitness-app'
                }
            }
        }
    } 
}