from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """Override get_user() to support multiple user models."""
        role = validated_token.get('role')
        user_id = validated_token.get('user_id')

        if not role and not user_id:
            raise AuthenticationFailed('Token missing role or user_id')

        # This must be defined in settings.py of each service
        role_model_map = getattr(settings, 'JWT_ROLE_MODEL_MAP', None)

        if not role_model_map or not isinstance(role_model_map, dict):
            raise ImproperlyConfigured(
                'JWT_ROLE_MODEL_MAP must be defined in settings.py')

        model = role_model_map.get(role)
        if not model:
            raise AuthenticationFailed(
                f'Role {role} is not registered in JWT_ROLE_MODEL_MAP')

        try:
            if hasattr(model, '_meta'):  # django model
                status_flag = f'is_{role}'
                user = model.objects.filter(
                    id=user_id, **{status_flag: True}).first()

                if user:
                    return user
                raise AuthenticationFailed('User not found or inactive.')

            elif hasattr(model, 'get_user'):
                user = model.get_user(user_id)

                if user:
                    return user
                raise AuthenticationFailed('Remote user not found.')

            else:
                raise ImproperlyConfigured(
                    f'{model} is not a valid user model class')

        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')
