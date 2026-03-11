"""
Virtual Environment (venv) Usage Guide

This module demonstrates the creation and activation of Python virtual environments.

Virtual environments are isolated Python environments that allow you to manage
project-specific dependencies without affecting the system-wide Python installation.

Creation:
    To create a new virtual environment, use:
    python -m venv <environment_name>
    
    Example:
    python -m venv my_env

Activation:
    On Windows:
        my_env\Scripts\activate
    
    On macOS/Linux:
        source my_env/bin/activate
    
    After activation, your shell prompt will be prefixed with the environment name.

Deactivation:
    To exit the virtual environment, simply run:
        deactivate

Benefits:
    - Isolate project dependencies
    - Avoid version conflicts between projects
    - Easier deployment and reproducibility
    - Clean project management
"""