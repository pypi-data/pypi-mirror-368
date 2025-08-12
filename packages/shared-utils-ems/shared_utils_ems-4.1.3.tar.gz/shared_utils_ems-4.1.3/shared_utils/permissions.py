from rest_framework.permissions import BasePermission
from django.http import HttpRequest
from rest_framework.exceptions import AuthenticationFailed


class IsAuthenticatedViaJWT(BasePermission):
    """
    Custom permission that ensures the request has a valid JWT,
    contains required claims, and is not anonymous.
    """

    required_claims = ['user_id', 'email', 'role']
    required_roles = ['attendee', 'staff', 'admin']

    def has_permission(self, request: HttpRequest, view):
        user = request.user
        token = request.auth

        if not user or user.is_anonymous or user.role not in self.required_roles:
            raise AuthenticationFailed('User is not authenticated.')

        if not token:
            raise AuthenticationFailed('Invalid or missing JWT token.')

        for claim in self.required_claims:
            if claim not in token:
                raise AuthenticationFailed(
                    f"Missing claim: '{claim}' in token.")

        return True


class HasRolePermission(BasePermission):
    """This will check if the user has the appropriate role to access the resource."""
    required_roles = []

    def has_permission(self, request: HttpRequest, view):
        user_role = request.user.role
        return user_role in self.required_roles
