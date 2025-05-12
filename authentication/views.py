from django.shortcuts import render
#jwt authentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

class ProtectedView(APIView):
    """
    A protected view that requires JWT authentication.
    Returns a message and user-specific data for authenticated users.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Return user-specific data
            user_data = {
                "username": request.user.username,
                "email": request.user.email,
            }
            return Response({"message": "This is protected", "user": user_data})
        except Exception as e:
            # Log the error (optional: integrate a logging framework)
            print(f"Error in ProtectedView: {e}")
            return Response({"error": "An unexpected error occurred."}, status=500)


