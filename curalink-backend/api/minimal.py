def handler(request):
    """Minimal Vercel Python function"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": '{"message": "Hello from CuraLink API", "status": "working"}'
    }
