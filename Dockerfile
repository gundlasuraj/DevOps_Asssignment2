# ===== Builder/Test Stage =====
# Use a slim image for a smaller footprint, as we don't need tkinter for testing.
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Copy only the necessary files for testing
COPY . .
COPY ACEest_Fitness.py .
COPY test_app.py .

# Install dependencies, including testing tools
RUN pip install --no-cache-dir -r requirements.txt

# Run tests using pytest. This step validates the code.
# The docker build will fail here if tests do not pass.
RUN pytest


# ===== Final/Production Stage =====
# The final image is just the tested application code.
# We don't need a final stage if we are not creating a runnable image of the GUI app.
# If this were a web app, we would create a slim final image here.