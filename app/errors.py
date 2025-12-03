class AppError(Exception):
    pass


class EntityNotFoundError(AppError):

    def __init__(self, entity: str, identifier: str):
        self.message = f"{entity} with id/name '{identifier}' was not found."
        super().__init__(self.message)


class BusinessRuleError(AppError):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ExternalAPIError(AppError):

    def __init__(self, service: str, detail: str):
        self.message = f"Error communicating with {service}: {detail}"
        super().__init__(self.message)


class AuthenticationError(AppError):

    def __init__(self, message: str = "Authentication required"):
        self.message = message
        super().__init__(self.message)
