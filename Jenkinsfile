pipeline {
    agent any // We will define the agent for each stage

    environment {
        // Use the commit hash for a unique, traceable image tag.
        // We define it here so it's available in all stages.
        // Using a script block is more robust for capturing command output.
        IMAGE_NAME = "surajgundla/aceest-fitness" 
        // This must match the 'name' field in your deployment YAMLs
        K8S_CONTAINER_NAME = 'aceest-fitness-container'
        // Define the service name for the Blue-Green switch
        K8S_SERVICE_NAME = 'aceest-fitness-app-svc'
        LIVE_COLOR = ""
        INACTIVE_COLOR = ""
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
                //input "Image built. Proceed with push to Docker Hub?"
                echo "Pushing the image to Docker Hub..."
                script {
                    // The 'dockerhub-credentials' ID must match the one you created in Jenkins
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        def img = docker.image("${IMAGE_NAME}:${IMAGE_TAG}")
                        // Push the uniquely tagged image first
                        img.push()
                        // Then, tag the same image as 'latest' and push that tag
                        img.push('latest')
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            // This stage needs kubectl configured
            agent any
            steps {
                withKubeConfig([credentialsId: 'kubeconfig']) {

                    script {
                        // === 1. Determine which color is LIVE ===
                        try {
                            echo "Checking which color is live..."
                            // This command will fail if the service doesn't exist, triggering the catch block.
                            LIVE_COLOR = bat(returnStdout: true, script: "kubectl get svc ${K8S_SERVICE_NAME} -o jsonpath='{.spec.selector.color}'").trim()
                            
                            if (LIVE_COLOR == 'blue') {
                                INACTIVE_COLOR = 'green'
                            } else {
                                INACTIVE_COLOR = 'blue'
                            }
                        } catch (Exception e) {
                            // This block executes on the very first run when the service is not found.
                            echo "Service ${K8S_SERVICE_NAME} not found. Assuming first-time deployment."
                            echo "Defaulting to deploy 'blue' as the first environment."
                            LIVE_COLOR = 'green'      // The color we will switch FROM (doesn't exist yet)
                            INACTIVE_COLOR = 'blue'   // The color we will deploy TO

                            // Apply all configurations to create the environment from scratch.
                            bat "kubectl apply -f service.yaml"
                            bat "kubectl apply -f deployment-blue.yaml"
                            bat "kubectl apply -f deployment-green.yaml"
                        }
                        echo "Live color is: ${LIVE_COLOR}. Deploying to inactive color: ${INACTIVE_COLOR}."
                    }

                    // === 2. Apply the inactive deployment with the new image ===
                    
                    echo "Updating Kubernetes deployment to image: ${IMAGE_NAME}:${IMAGE_TAG}"
                    bat "kubectl set image deployment/aceest-fitness-app-${INACTIVE_COLOR} ${K8S_CONTAINER_NAME}=${IMAGE_NAME}:${IMAGE_TAG}"

                    // === 3. Wait for the new deployment to be ready ===
                    // The pipeline will fail here if the new pods can't start, preventing a bad release.
                    bat "kubectl rollout status deployment/aceest-fitness-app-${INACTIVE_COLOR}"
                }
            }
        }

        stage('Promote to Live') {
            agent any
            steps {
                // === 4. Manual approval before switching traffic ===
                // This is a critical safety gate. You can test the "inactive" service before promoting.
                input "Promote ${INACTIVE_COLOR} deployment to live?"
                
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    script {
                        // === 5. Switch the service to point to the new color ===
                        // On Windows, the JSON payload for the patch command must use escaped double quotes.
                        // The entire -p argument is wrapped in a single set of double quotes.
                        def patchCmd = "kubectl patch service ${K8S_SERVICE_NAME} -p \"{\\\"spec\\\":{\\\"selector\\\":{\\\"color\\\":\\\"${INACTIVE_COLOR}\\\"}}}\""
                        echo "Switching live traffic to ${INACTIVE_COLOR}..."
                        bat patchCmd
                        
                        // Verify the switch
                        def newLiveColor = bat(returnStdout: true, script: "kubectl get svc ${K8S_SERVICE_NAME} -o jsonpath='{.spec.selector.color}'").trim()
                        if (newLiveColor == INACTIVE_COLOR) {
                            echo "Successfully switched. ${newLiveColor} is now live."
                        } else {
                            error("Failed to switch service. Current live color is still ${newLiveColor}.")
                        }
                    }
                }
            }
        }
    } 
}