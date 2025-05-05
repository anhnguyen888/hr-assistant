#!/usr/bin/env python3
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import get_assistant

# Get the HR assistant instance
assistant = get_assistant()

# Test with a simple question
question = "Chính sách nghỉ phép của công ty là gì?"
print(f"Question: {question}")
response = assistant.ask(question)
print(f"Response: {response}")
