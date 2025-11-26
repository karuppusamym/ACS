from openai import OpenAI
from app.core.config import settings

print("="*60)
print("OpenAI API Key Test")
print("="*60)
print()

# Check if API key is set
if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key-here":
    print("❌ OpenAI API key is not configured!")
    print()
    print("Please add your API key to backend/.env:")
    print("OPENAI_API_KEY=sk-proj-your-actual-key-here")
    print()
    print("Get your key from: https://platform.openai.com/api-keys")
    exit(1)

print(f"API Key found: {settings.OPENAI_API_KEY[:10]}...{settings.OPENAI_API_KEY[-4:]}")
print()

# Test the API key
try:
    print("Testing OpenAI API connection...")
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello! API key is working!'"}
        ],
        max_tokens=20
    )
    
    print("✅ OpenAI API Key is WORKING!")
    print()
    print(f"Response: {response.choices[0].message.content}")
    print(f"Tokens used: {response.usage.total_tokens}")
    print(f"Model: {response.model}")
    print()
    print("="*60)
    print("SUCCESS! Your OpenAI integration is ready!")
    print("="*60)
    
except Exception as e:
    print("❌ OpenAI API Key test FAILED!")
    print()
    print(f"Error: {str(e)}")
    print()
    print("Common issues:")
    print("1. Invalid API key - check if it starts with 'sk-'")
    print("2. Quota exceeded - add credits at https://platform.openai.com/account/billing")
    print("3. Rate limit - wait a minute and try again")
    print()
    exit(1)
