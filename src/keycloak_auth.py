"""
Autenticação e autorização via Keycloak.

- get_current_user: extrai e valida o token JWT do header Authorization.
- require_roles: factory de dependency que restringe acesso por realm roles.
"""

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.config import KEYCLOAK_REALM, KEYCLOAK_SERVER_URL
from src.database import get_db
from src.shared.permissoes import efetivas

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


async def _get_jwks(force_refresh: bool = False) -> dict:
    """Busca as chaves JWKS do Keycloak (com cache em memória).
    
    Se force_refresh=True, ignora o cache e busca chaves novas.
    Isso é necessário quando o Keycloak é reiniciado e gera novas chaves.
    """
    global _jwks_cache
    if _jwks_cache is None or force_refresh:
        async with httpx.AsyncClient() as client:
            resp = await client.get(_jwks_url())
            resp.raise_for_status()
            _jwks_cache = resp.json()
    return _jwks_cache


def _find_rsa_key(jwks: dict, kid: str) -> dict | None:
    """Procura a chave RSA no JWKS pelo kid do token."""
    for key in jwks.get("keys", []):
        if key["kid"] == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    return None


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
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        # Tenta com o cache primeiro
        jwks = await _get_jwks()
        rsa_key = _find_rsa_key(jwks, kid)

        # Se não achou, o Keycloak pode ter sido reiniciado e gerado novas chaves.
        # Busca chaves frescas uma vez antes de desistir.
        if rsa_key is None:
            jwks = await _get_jwks(force_refresh=True)
            rsa_key = _find_rsa_key(jwks, kid)

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
        user_roles = [r.lower() for r in current_user.get("realm_roles", [])]
        if not any(role.lower() in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acesso negado. Roles necessárias: {list(allowed_roles)}. "
                    f"Suas roles: {user_roles}"
                ),
            )
        return current_user

    return _check_roles


def _extrair_perfil(user_roles: list[str]) -> str:
    if "admin" in user_roles:
        return "admin"
    if "advogado" in user_roles:
        return "advogado"
    if "estagiario" in user_roles:
        return "estagiario"
    return "advogado"


def require_roles_or_permission(roles: list[str] | None, permissao: str | None):
    """
    Factory de dependency que libera acesso se o usuário tiver uma das
    `roles` informadas OU se a permissão individual `permissao` estiver
    ativa para ele (override salvo em Usuario.permissoes, ou padrão do
    perfil quando não há override).

    Usada para permitir que, por exemplo, um estagiário com a permissão
    "criarProcessos" ativada manualmente consiga criar processos mesmo
    sem ter a role "advogado"/"admin".
    """

    async def _check(
        current_user: dict = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> dict:
        user_roles = [r.lower() for r in current_user.get("realm_roles", [])]

        if roles and any(role.lower() in user_roles for role in roles):
            return current_user

        if permissao:
            # Import local para evitar ciclo de import no carregamento do módulo.
            from src.usuarios.model import Usuario as UsuarioModel

            local = (
                db.query(UsuarioModel)
                .filter(UsuarioModel.keycloak_id == current_user.get("sub"))
                .first()
            )
            perfil = local.perfil if local else _extrair_perfil(user_roles)
            overrides = local.permissoes if local else None
            if efetivas(perfil, overrides).get(permissao):
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Você não tem a role ou permissão necessária para esta ação.",
        )

    return _check