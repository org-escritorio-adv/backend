"""
Autenticação e autorização via Keycloak.

- get_current_user: extrai e valida o token JWT do header Authorization.
- require_roles: factory de dependency que restringe acesso por realm roles.
"""

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from jose import jwk
from jose.utils import base64url_decode

from src.config import KEYCLOAK_CLIENT_ID, KEYCLOAK_REALM, KEYCLOAK_SERVER_URL

# ── Esquema de segurança ────────────────────────────────────────────────────
_bearer_scheme = HTTPBearer()

# ── Cache da JWKS (chaves públicas) ─────────────────────────────────────────
_jwks_cache: dict | None = None


def _jwks_url() -> str:
    return (
        f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"
        f"/protocol/openid-connect/certs"
    )


def _issuer_url() -> str:
    return f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}"


async def _get_jwks() -> dict:
    """Busca as chaves JWKS do Keycloak (com cache em memória)."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(_jwks_url())
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def _extract_realm_roles(token_payload: dict) -> list[str]:
    """Extrai as realm_roles do payload do token JWT do Keycloak."""
    realm_access = token_payload.get("realm_access", {})
    return realm_access.get("roles", [])


# ── Dependencies ────────────────────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict:
    """
    Dependency do FastAPI que valida o token JWT do Keycloak.

    Retorna um dict com:
        - sub: ID do usuário no Keycloak
        - email: e-mail do usuário
        - preferred_username: username
        - realm_roles: lista de roles do realm
    """
    token = credentials.credentials

    try:
        jwks = await _get_jwks()
        # Extrair o header do JWT para pegar o kid
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Encontrar a chave correspondente no JWKS
        rsa_key = None
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if rsa_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Chave pública não encontrada para validar o token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_iss": False,
                "verify_aud": False,
            },
        )

    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou expirado: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "sub": payload.get("sub"),
        "email": payload.get("email"),
        "preferred_username": payload.get("preferred_username"),
        "realm_roles": _extract_realm_roles(payload),
    }


def require_roles(*allowed_roles: str):
    """
    Factory que retorna uma dependency do FastAPI exigindo que o usuário
    tenha pelo menos uma das roles informadas.

    Exemplo de uso:
        @router.get("/", dependencies=[Depends(require_roles("admin", "advogado"))])
    """

    async def _check_roles(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_roles = current_user.get("realm_roles", [])
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acesso negado. Roles necessárias: {list(allowed_roles)}. "
                    f"Suas roles: {user_roles}"
                ),
            )
        return current_user

    return _check_roles
