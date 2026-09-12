import google.generativeai as genai
import os

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("--- Models available for your API key ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
