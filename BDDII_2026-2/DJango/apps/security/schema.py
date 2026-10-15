from drf_spectacular.extensions import OpenApiAuthenticationExtension

class StoreLabJWTScheme(OpenApiAuthenticationExtension):
    target_class = "apps.security.authentication.StoreLabJWTAuthentication"
    name = "bearerAuth"

    def get_security_definition(self, auto_schema):
        return {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
