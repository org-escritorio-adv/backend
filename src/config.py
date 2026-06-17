import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. "
        "Example: postgresql+psycopg2://user:pass@postgres:5432/dbname"
    )
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Keycloak
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "escritorio-adv")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "backend-api")
KEYCLOAK_ADMIN_CLIENT_ID = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID", "backend-client")
KEYCLOAK_ADMIN_CLIENT_SECRET = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", "gUHc20eRvmYZBKiMUSv0M5qa5A44x7ev")

# DataJud
DATAJUD_BASE_URL = os.getenv("DATAJUD_BASE_URL", "https://api-publica.datajud.cnj.jus.br")
DATAJUD_API_KEY = os.getenv("DATAJUD_API_KEY", "")

# Resend (e-mail transacional)
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "noreply@escritorio-adv.com.br")
