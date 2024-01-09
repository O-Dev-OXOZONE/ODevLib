from django.db import IntegrityError


class OdevlibIntegrityError(IntegrityError):
    """
    This is a custom IntegrityError class for odevlib.
    Attributes:
        eng_description (str): English description of the error.
        ui_description (str): UI description of the error.
        error_code (int): Error code.
    Attributes were used to match the structure of the Error class.
    """
    def __init__(self, eng_description: str, ui_description: str, error_code: int):
        self.eng_description = eng_description
        self.ui_description = ui_description
        self.error_code = error_code
