class MessengerAPIError(Exception):
    """
    Custom exception class for handling API errors.
    """

    def __init__(self, status_code, error_response):
        self.status_code = status_code
        self.error_response = error_response

        # Try extracting Facebook-style error details
        error = (
            error_response.get("error", {}) if isinstance(error_response, dict) else {}
        )
        self.error_type = error.get("type", "Unknown")
        self.error_message = error.get("message", "Unknown error occurred.")
        self.error_code = error.get("code", "N/A")

        super().__init__(self.__str__())

    def __str__(self):
        return (
            f"MessengerAPIError (HTTP {self.status_code}): "
            f"[{self.error_type}] {self.error_message} (code {self.error_code})"
        )
