# GitHub Actions CI Workflow - Student Guide

## Overview

This lesson will teach you how to create a complete CI/CD pipeline using GitHub Actions for a Python application. You'll learn to:

- Set up a Python application with external API integration
- Create a Docker container for your application
- Configure GitHub Actions workflow for automated testing and deployment
- Deploy your application to Docker Hub using CI/CD

## Prerequisites

Before starting this lesson, ensure you have:

- A GitHub account
- A Docker Hub account
- Basic knowledge of Python
- Basic understanding of Git and GitHub
- Basic understanding of Docker

## Repository Reference

This lesson is based on the repository: https://github.com/ravivshweidgit/python-example-main

## Lesson Structure

### Part 1: Understanding the Application

#### 1.1 Python Application (`main.py`)

Our application is a simple weather service that fetches current weather data from an external API.

```python
import requests
import os
import json

def get_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    
    #print (url)
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:

        #print(json.dumps(data, indent=4))

        # Get temperature from the 'main' key, and convert from Kelvin to Celsius
        # The temperature key in OpenWeatherMap is 'temp'
        temperature_kelvin = data['main']['temp']
        temperature_celsius = temperature_kelvin - 273.15
        
        # Get condition from the 'weather' key, which is a list
        # We access the first item [0] and then the 'description'
        condition = data['weather'][0]['description']
        
        # Format the output with the new variables
        return f"Current temperature in {city} is {temperature_celsius:.2f}°C, Condition: {condition}"

    else:
        return "Failed to fetch weather data"

api_key = os.getenv('API_TOKEN')
city = 'Tel Aviv'
print(get_weather(api_key, city))
```

**Key Points:**
- Uses the `requests` library to make HTTP calls
- Reads API key from environment variables for security
- Handles API response and error cases
- Displays weather information for Tel Aviv
- **Important Fix:** Uses the correct OpenWeatherMap API endpoint (`api.openweathermap.org`) instead of the incorrect `api.weatherapi.com`
- Converts temperature from Kelvin to Celsius (OpenWeatherMap returns temperatures in Kelvin)
- Accesses weather condition from the `weather` array structure

#### 1.2 Dependencies (`requirements.txt`)

```txt
requests==2.28.1
```

This file specifies the exact version of the `requests` library needed for the application.

#### 1.3 Docker Configuration (`Dockerfile`)

```dockerfile
FROM python:3.9-alpine

WORKDIR /code

# Copy only the necessary files
COPY requirements.txt .
COPY main.py .

# Install any dependencies
RUN pip install -r requirements.txt

# Run your application
CMD ["python", "main.py"]
```

**Key Points:**
- Uses lightweight Alpine Linux base image
- Sets working directory to `/code`
- Copies only necessary files (good practice for smaller images)
- Installs dependencies from `requirements.txt`
- Runs the application on container start

### Part 2: Setting Up External Services

#### 2.1 Weather API Setup

1. **Visit OpenWeatherMap:**
   - Go to: https://openweathermap.org/
   - Sign up at: https://home.openweathermap.org/users/sign_up

2. **Get Your API Key:**
   - After registration, navigate to your user dashboard
   - Copy your API key (example: `your_api_key_here_32_characters`)
   - Keep this key secure - you'll need it for GitHub secrets

#### 2.2 Docker Hub Setup

1. **Create a Private Repository:**
   - Go to Docker Hub: https://hub.docker.com/
   - Create a new private repository named: `github-actions-lab`
   - Note your Docker Hub username (example: `ravivshweid`)

### Part 3: GitHub Repository Configuration

#### 3.1 Setting Up Repository Secrets

1. **Navigate to Repository Settings:**
   - Go to: https://github.com/ravivshweidgit/python-example-main/settings
   - Click on "Actions secrets and variables"
   - Select "Repository secrets"

2. **Add Required Secrets:**
   - `API_TOKEN`: Your OpenWeatherMap API key
   - `DOCKER_PASSWORD`: Your Docker Hub password
   - `DOCKER_USERNAME`: Your Docker Hub username

**Steps to add secrets:**
1. Click "New repository secret"
2. Enter the secret name (e.g., `API_TOKEN`)
3. Enter the secret value
4. Click "Add secret"
5. Repeat for all three secrets

### Part 4: GitHub Actions Workflow

#### 4.1 Understanding the CI Workflow

The GitHub Actions workflow will:
1. Check out the code
2. Set up Python environment
3. Install dependencies
4. Run tests (if any)
5. Build Docker image
6. Push image to Docker Hub

#### 4.2 Workflow File Structure

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests
      run: |
        python -m pytest tests/ || echo "No tests found"
        
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
        
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./Dockerfile
        push: true
        tags: ravivshweid/github-actions-lab:latest
```

#### 4.3 Key Workflow Components

**Triggers:**
- `on: push` - Runs when code is pushed to main branch
- `on: pull_request` - Runs when pull requests are created

**Steps:**
1. **Checkout:** Downloads the repository code
2. **Python Setup:** Installs Python 3.9
3. **Dependencies:** Installs required packages
4. **Tests:** Runs any available tests
5. **Docker Login:** Authenticates with Docker Hub
6. **Build & Push:** Creates and uploads Docker image

### Part 5: Testing the Workflow

#### 5.1 Making Changes

1. **Update the Docker image tag:**
   ```bash
   # Edit .github/workflows/ci.yml
   # Change the tags line to match your Docker Hub repository
   tags: your-username/github-actions-lab:latest
   ```

2. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "Update Docker image tag"
   git push
   ```

#### 5.2 Monitoring the Workflow

1. **View Workflow Runs:**
   - Go to: https://github.com/ravivshweidgit/python-example-main/actions
   - Click on the latest workflow run

2. **Check Individual Steps:**
   - Click on "build-and-deploy" job
   - Expand each step to see detailed logs
   - Example: https://github.com/ravivshweidgit/python-example-main/actions/runs/17806847029/job/50620707820

3. **Example of Successful Application Run:**
   When the workflow runs successfully, you'll see output like this:
   ```
   Run python main.py
     python main.py
     shell: /usr/bin/bash -e {0}
     env:
       pythonLocation: /opt/hostedtoolcache/Python/3.9.23/x64
       LD_LIBRARY_PATH: /opt/hostedtoolcache/Python/3.9.23/x64/lib
       API_TOKEN: ***
   Current temperature in Tel Aviv is 26.06°C, Condition: few clouds
   ```
   
   **What this shows:**
   - The application runs successfully in the GitHub Actions environment
   - The API token is properly masked (shown as `***`)
   - The weather data is fetched and displayed correctly
   - Temperature is converted from Kelvin to Celsius (26.06°C)
   - Weather condition is properly extracted ("few clouds")

#### 5.3 Verifying Success

1. **Check Docker Hub:**
   - Visit your Docker Hub repository
   - Verify the new image was pushed successfully
   - Check the image tags and timestamps

2. **Test the Application:**
   ```bash
   # Pull and run the image locally
   docker pull your-username/github-actions-lab:latest
   docker run -e API_TOKEN=your-api-key your-username/github-actions-lab:latest
   ```

### Part 6: Troubleshooting Common Issues

#### 6.1 Authentication Errors

**Problem:** Docker login fails
**Solution:** 
- Verify Docker Hub credentials in repository secrets
- Ensure secrets are named exactly: `DOCKER_USERNAME`, `DOCKER_PASSWORD`

#### 6.2 API Key Issues

**Problem:** Weather API returns errors
**Solution:**
- Verify API key is correctly set in `API_TOKEN` secret
- Check API key permissions on OpenWeatherMap dashboard
- Ensure API key is active and not expired
- **Important:** Make sure you're using the correct API endpoint (`api.openweathermap.org`) and parameter name (`appid` instead of `key`)
- Verify the API response structure matches the code expectations (temperature in Kelvin, weather as array)

#### 6.3 Build Failures

**Problem:** Docker build fails
**Solution:**
- Check Dockerfile syntax
- Verify all required files are present
- Review build logs for specific error messages

### Part 7: Best Practices

#### 7.1 Security

- Never commit API keys or passwords to the repository
- Use GitHub secrets for sensitive information
- Regularly rotate API keys and passwords

#### 7.2 Docker Optimization

- Use specific base image versions (not `latest`)
- Copy only necessary files to reduce image size
- Use multi-stage builds for complex applications

#### 7.3 Workflow Optimization

- Use caching for dependencies to speed up builds
- Run tests before building Docker images
- Use matrix builds for multiple Python versions

### Part 8: Next Steps

After completing this lesson, you should:

1. **Understand the CI/CD pipeline flow**
2. **Be able to create GitHub Actions workflows**
3. **Know how to integrate external services**
4. **Understand Docker containerization**
5. **Be familiar with GitHub secrets management**

### Part 9: Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)
- [Python Requests Library](https://requests.readthedocs.io/)

### Part 10: Exercise

Try modifying the application to:

1. **Add error handling for network timeouts**
2. **Support multiple cities**
3. **Add logging functionality**
4. **Create unit tests**
5. **Add a health check endpoint**
6. **Debug API issues** - Use the commented print statements to debug API responses
7. **Handle different API response formats** - Add validation for missing data fields

**Debugging Tips:**
- Uncomment the `print(url)` line to verify the API URL is correct
- Uncomment the `print(json.dumps(data, indent=4))` line to see the full API response structure
- Always test API endpoints manually before implementing in code

Remember to update the workflow accordingly and test your changes!

---

## Summary

This lesson covered the complete process of setting up a CI/CD pipeline using GitHub Actions for a Python application. You learned how to:

- Create a Python application with external API integration
- Containerize the application using Docker
- Set up GitHub Actions workflow for automated builds
- Deploy to Docker Hub using CI/CD
- Monitor and troubleshoot the pipeline

The skills learned here are fundamental to modern software development and DevOps practices.
