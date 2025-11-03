pipeline {
    agent any

    environment {
        // Define a version number. This can be managed dynamically.
        // Using the build number for dynamic versioning.
        APP_VERSION = "1.0.${env.BUILD_NUMBER}"
        PYTHON_HOME = 'C:\\Users\\Suraj\\AppData\\Local\\Python\\pythoncore-3.14-64'
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
                script {
                    // Use 'bat' for Windows commands.
                    // Ensure python is in your system's PATH.
                    bat '"%PYTHON_HOME%\\python.exe" -m venv venv'
                    // Use the python/pip from inside the venv for all subsequent steps
                    bat 'venv\\Scripts\\python.exe -m pip install --upgrade pip'
                    bat 'venv\\Scripts\\pip.exe install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                // Run tests with pytest and generate a coverage report
                bat 'venv\\Scripts\\pytest.exe --cov=ACEest_Fitness --cov-report=xml --junitxml=test-results.xml'
            }
        }

        stage('Archive Artifacts') {
            steps {
                // Use the built-in 'tar' command to create a compressed archive on Windows.
                // The 'a' flag automatically selects the archive format based on the extension (.zip).
                bat "tar -a -cf ACEestFitness-v${env.APP_VERSION}.zip ACEest_Fitness.py test_ACEest_Fitness.py requirements.txt"
                archiveArtifacts artifacts: "*.zip", fingerprint: true
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                script {
                    // Ensure the Docker Pipeline plugin is installed in Jenkins
                    // The 'dockerhub-credentials' ID must match the one you create in Jenkins
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        
                        // Define your Docker Hub username and image name
                        def imageName = "surajgundla/aceest-fitness:${env.BUILD_NUMBER}"
                        
                        // Build the Docker image from the Dockerfile in the current directory
                        def customImage = docker.build(imageName, '.')
                        
                        // Push the image to Docker Hub
                        customImage.push()
                    }
                }
            }
        }
    }
}