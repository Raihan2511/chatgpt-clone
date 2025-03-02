import google.generativeai as genai

# Set your API key
API_KEY = "AIzaSyAl67MS8iGGcAnMi9RJljSjWtcgRagiqOE"

# Configure the API key
genai.configure(api_key=API_KEY)

# List available models
models = genai.list_models()

# Loop through and print model names
for model in models:
    print(model.name)
