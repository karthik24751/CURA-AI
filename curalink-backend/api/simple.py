import json

def handler(request, context):
    """Simple Vercel Python function for testing"""
    try:
        path = request.get('path', '/')

        # Root endpoint
        if path == '/' or path == '':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "Welcome to CuraLink API",
                    "version": "1.0.0",
                    "status": "operational"
                })
            }

        # Login endpoint
        elif path == '/api/auth/login':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "access_token": "mock_token_12345",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": "test@example.com",
                        "full_name": "Test User",
                        "role": "patient"
                    }
                })
            }

        # Register endpoint
        elif path == '/api/auth/register':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "access_token": "mock_token_67890",
                    "token_type": "bearer",
                    "user": {
                        "id": 1,
                        "email": "newuser@example.com",
                        "full_name": "New User",
                        "role": "patient"
                    }
                })
            }

        # Trials endpoint
        elif path == '/api/trials/':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "data": [
                        {
                            "nct_id": "NCT05123456",
                            "title": "Flu Vaccine Study",
                            "summary": "Vaccine research study",
                            "condition": "Influenza",
                            "location": "New York, NY",
                            "phase": "Phase 3",
                            "status": "Recruiting"
                        }
                    ]
                })
            }

        # Publications endpoint
        elif path == '/api/publications/':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "data": [
                        {
                            "id": "1",
                            "title": "Medical Research Paper",
                            "authors": "Dr. Smith",
                            "journal": "Medical Journal",
                            "year": 2024
                        }
                    ]
                })
            }

        # Experts endpoint
        elif path == '/api/experts/':
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({
                    "data": [
                        {
                            "id": 1,
                            "full_name": "Dr. Sarah Johnson",
                            "specialty": "Oncology",
                            "institution": "Medical Center",
                            "verified": True
                        }
                    ]
                })
            }

        # Default response
        else:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"status": "ok", "message": "CuraLink API"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
