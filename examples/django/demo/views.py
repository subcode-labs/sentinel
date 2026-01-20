from django.http import JsonResponse
from django.conf import settings
from sentinel_sdk import SentinelClient


def index(request):
    """
    Standard view showing configuration loaded at startup.
    """
    return JsonResponse(
        {
            "status": "online",
            "configured_secret_key_prefix": settings.SECRET_KEY[:5] + "...",
            "debug_mode": settings.DEBUG,
            "message": "Sentinel Integration Demo running!",
        }
    )


def runtime_secret(request):
    """
    Demonstrates fetching a secret at runtime (just-in-time access).
    """
    try:
        client = SentinelClient()
        # In a real app, you wouldn't return the secret value directly!
        # This is just for demonstration purposes.
        api_key = client.get_secret("demo_api_key")

        return JsonResponse(
            {
                "secret_name": "demo_api_key",
                "found": api_key is not None,
                "value_preview": f"{api_key.value[:4]}..." if api_key else None,
                "version": api_key.version if api_key else None,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
