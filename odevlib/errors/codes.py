# For cases when other instances have relation on this one and their on_delete is set to PROTECTED.
protected_instance: int = 1

# For cases when exception was not gracefully handled.
unhandled_error: int = 2

# For permission denials
permission_denied: int = 3

# When internal database inconsistencies are detected
internal_data_inconsistency: int = 4

# When requested object does not exist
does_not_exist: int = 5
not_found: int = 6

# When data supplied from client is invalid
invalid_request_data: int = 6

# When some internal error was detected and gracefully handled
internal_server_error: int = 7

# Custom HTTP status codes for internal error codes
status_code_mapping = {
    invalid_request_data: 400,
    permission_denied: 403,
    does_not_exist: 404,
    not_found: 404,
    internal_server_error: 500,
}
