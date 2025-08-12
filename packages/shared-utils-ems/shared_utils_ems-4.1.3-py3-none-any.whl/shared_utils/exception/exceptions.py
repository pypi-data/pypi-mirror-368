from rest_framework import status
from rest_framework.exceptions import APIException


class Problem(APIException):
    """
    A dynamic, structured exception class following RFC 7807 Problem Details.
    """

    def __init__(self, type_uri, title, status_code, detail=None, instance=None, **kwargs):
        """
        :param type_uri: A URI identifying the type of error.
        :param title: A short, human-readable summary of the error type.
        :param status_code: HTTP status code for this error.
        :param detail: A human-readable explanation of the specific error occurrence.
        :param instance: A URI identifying the specific occurrence of the problem.
        :param kwargs: Additional fields (e.g., validation errors).
        """
        self.type_uri = type_uri
        self.title = title
        self.status_code = status_code
        self.detail = detail
        self.instance = instance
        self.extra_fields = kwargs
        super().__init__(detail)

    def get_full_details(self):
        problem_details = {
            'type': self.type_uri,
            'title': self.title,
            'status': self.status_code,
            'detail': self.detail
        }

        if self.instance:
            problem_details['instance'] = self.instance
        if self.extra_fields:
            problem_details.update(self.extra_fields)

        return problem_details


class ValidationErrorProblem(Problem):
    def __init__(self, invalid_params):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.1",
            title="Your request parameters didn't validate.",
            status_code=status.HTTP_400_BAD_REQUEST,
            invalid_params=invalid_params
        )


class NotFoundProblem(Problem):
    def __init__(self, resource='Resource'):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.4",
            title="The requested resource was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The resource '{resource}' could not be found."
        )


class UnauthorizedProblem(Problem):
    def __init__(self, detail="Authentication credentials are missing or invalid."):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7235#section-3.1",
            title="Unauthorized Access",
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenProblem(Problem):
    def __init__(self, detail="You do not have permission to perform this action."):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.3",
            title="Forbidden",
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ConflictProblem(Problem):
    def __init__(self, detail="A conflict occurred with the current state of the resource."):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7231#section-6.5.8",
            title="Conflict",
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


class InternalServerProblem(Problem):
    def __init__(self, detail="An unexpected error occurred. Please try again later."):
        super().__init__(
            type_uri="https://datatracker.ietf.org/doc/html/rfc7231#section-6.6.1",
            title="Internal Server Error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
