# ZKAuth Python SDK

Zero-knowledge proof authentication for Python applications.

## Installation

```bash
pip install zkauth-sdk
```

## Quick Start

### Basic Usage

```python
from zkauth import ZKAuthClient

client = ZKAuthClient(
    api_key="your-api-key",
    base_url="https://zkauth-engine.vercel.app"
)

# Sign up a new user
signup_result = await client.sign_up(
    email="user@example.com",
    password="secure-password"
)

# Sign in
signin_result = await client.sign_in(
    email="user@example.com",
    password="secure-password"
)

if signin_result.success:
    print(f"User authenticated: {signin_result.user.email}")
```

### Django Integration

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'zkauth.integrations.django',
]

ZKAUTH_CONFIG = {
    'API_KEY': 'your-api-key',
    'BASE_URL': 'https://zkauth-engine.vercel.app',
}

# views.py
from zkauth.integrations.django import zkauth_required

@zkauth_required
def protected_view(request):
    user = request.zkauth_user
    return JsonResponse({'user': user.email})
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from zkauth.integrations.fastapi import ZKAuthMiddleware, get_current_user

app = FastAPI()

# Add ZKAuth middleware
app.add_middleware(
    ZKAuthMiddleware,
    api_key="your-api-key",
    base_url="https://zkauth-engine.vercel.app"
)

@app.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user.email}
```

## Features

- ✅ Async/await support
- ✅ Django and FastAPI integrations
- ✅ Type hints with Pydantic models
- ✅ Comprehensive error handling
- ✅ Session management
- ✅ Device fingerprinting
- ✅ Python 3.8+ support

## API Reference

See [python.md](./python.md) for complete API documentation.

## License

MIT
