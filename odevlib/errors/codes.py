# For cases when other instances have relation on this one and their on_delete is set to PROTECTED.
from rest_framework import status


protected_instance: int = 1

# For cases when exception was not gracefully handled.
unhandled_error: int = 2

# For permission denials
permission_denied: int = 3

# When internal database inconsistencies are detected
internal_data_inconsistency: int = 4

# When requested object does not exist
does_not_exist: int = 5
not_found: int = 5

# When data supplied from client is invalid
invalid_request_data: int = 6

# When some internal error was detected and gracefully handled
internal_server_error: int = 7

# When no authentication information was provided
unauthenticated: int = 8

# Custom HTTP status codes for internal error codes
status_code_mapping = {
    invalid_request_data: status.HTTP_400_BAD_REQUEST,
    permission_denied: status.HTTP_403_FORBIDDEN,
    does_not_exist: status.HTTP_404_NOT_FOUND,
    not_found: status.HTTP_404_NOT_FOUND,
    internal_server_error: status.HTTP_500_INTERNAL_SERVER_ERROR,
    unauthenticated: status.HTTP_401_UNAUTHORIZED,
}
