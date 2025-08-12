class InvalidDocumentFormatException(ValueError):
    """Exception raised for invalid document formats."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"wowool.InvalidDocumentFormatException: {self.message}"
