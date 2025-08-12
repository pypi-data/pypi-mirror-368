# DemoLab

A Flask web application for URL redirection and workspace management.

## Features

- User authentication through API
- Workspace initialization and management
- URL redirection to user workspaces
- User workspace查询接口

## Installation

You can install DemoLab from PyPI:
pip install demolab
Or install from source:
git clone https://github.com/levindemo/demolab.git
cd demolab
pip install .
## Usage

Start the DemoLab application:
demolab
The application will start on http://localhost:5000 by default.

## Configuration

You can configure the application using environment variables:

- `AUTH_SERVICE_URL`: URL of the authentication service (default: http://localhost:5000/auth)
- `INIT_WORKSPACE_SCRIPT`: Path to the workspace initialization script
- `USER_CONFIG_PATH`: Path to the user configuration JSON file
- `WORKSPACE_LOG_PATH`: Path to the workspace logs directory
- `SECRET_KEY`: Secret key for Flask application security
- `VALID_INIT_TOKENS`: Comma-separated list of valid initialization tokens

## API Endpoints

- `GET /`: Login page
- `POST /api/login`: Authentication endpoint
- `GET /lab_init/<token>/<user>`: Initialize user workspace and redirect
- `GET /users/<user>`: Get user workspace information
