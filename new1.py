import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# Configure the API key
genai.configure(api_key=api_key)

# List available models
models = genai.list_models()

# Loop through and print model names
for model in models:
    print(model.name)
