pipeline {
    agent any

    environment {
        // Define a version number. This can be managed dynamically.
        // Using the build number for dynamic versioning.
        APP_VERSION = "1.0.${env.BUILD_NUMBER}"
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
                    bat 'python -m venv venv'
                    // Activate the virtual environment and install dependencies.
                    bat 'venv\\Scripts\\activate.bat && pip install --upgrade pip'
                    bat 'venv\\Scripts\\activate.bat && pip install -r requirements.txt'
                }
            }
        }

        stage('Run Tests') {
            steps {
                // Run tests with pytest and generate a coverage report
                bat 'venv\\Scripts\\activate.bat && pytest --cov=ACEest_Fitness --cov-report=xml --junitxml=test-results.xml'
            }
            post {
                always {
                    // Publish the test results and coverage report
                    junit 'test-results.xml'
                    publishCoverage adapters: [coberturaAdapter(path: 'coverage.xml')]
                }
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
    }
}