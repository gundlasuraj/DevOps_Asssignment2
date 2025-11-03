# ===== Builder/Test Stage =====
# Use a full Python image that includes build tools and tkinter support
FROM python:3.11 as builder

# Set the working directory
WORKDIR /app

# Copy all files to the app directory
COPY . .

# Install dependencies, including testing tools
RUN pip install --no-cache-dir -r requirements.txt

# Run tests using pytest. This step validates the code.
# The docker build command will fail here if tests do not pass.
RUN pytest --cov=. --cov-report=xml


# ===== Final/Production Stage =====
# Use a slim image for a smaller final footprint
FROM python:3.11-slim as final

# Set the working directory in the container
WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
# Copy only the application file from the builder stage
COPY --from=builder /app/ACEest_Fitness.py .

# Define the command to run your application
CMD ["python", "ACEest_Fitness.py"]