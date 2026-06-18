import os
import re
import secrets
import requests
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database import get_db
from src.auth.model import PasswordResetToken
from src.config import KEYCLOAK_SERVER_URL, KEYCLOAK_REALM

router = APIRouter(prefix="/auth", tags=["auth"])

BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")
BREVO_FROM_EMAIL = os.getenv("BREVO_FROM_EMAIL", "noreply@escritorio-adv.com.br")
BREVO_FROM_NAME = os.getenv("BREVO_FROM_NAME", "Barcelos & Takaki")
KEYCLOAK_CLIENT_ID_ADMIN = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID", "backend-client")
KEYCLOAK_CLIENT_SECRET_ADMIN = os.getenv("KEYCLOAK_ADMIN_CLIENT_SECRET", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

_rate_limit_store: dict[str, list[datetime]] = defaultdict(list)
_RATE_LIMIT = 20
_RATE_WINDOW = timedelta(minutes=15)


def _check_rate_limit(ip: str):
    now = datetime.now(timezone.utc)
    cutoff = now - _RATE_WINDOW
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > cutoff]
    if len(_rate_limit_store[ip]) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Muitas tentativas. Tente novamente em 15 minutos.")
    _rate_limit_store[ip].append(now)


def _obter_token_admin() -> str:
    url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    response = requests.post(
        url,
        data={
            "grant_type": "client_credentials",
            "client_id": KEYCLOAK_CLIENT_ID_ADMIN,
            "client_secret": KEYCLOAK_CLIENT_SECRET_ADMIN,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Erro de autenticação interna.")
    return response.json()["access_token"]


def _buscar_usuario_por_email(email: str) -> dict | None:
    token = _obter_token_admin()
    response = requests.get(
        f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users",
        params={"email": email, "exact": "true"},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code != 200:
        return None
    users = response.json()
    return users[0] if users else None


def _enviar_email_reset(email: str, token: str):
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 520px; margin: 0 auto; padding: 32px 24px; background: #f6f5f5; border-radius: 12px;">
      <h2 style="color: #1a2b3c; margin: 0 0 8px;">Redefinição de Senha</h2>
      <p style="color: #45556c; margin: 0 0 24px; font-size: 15px;">
        Você solicitou a redefinição de senha no sistema <strong>Barcelos &amp; Takaki</strong>.
      </p>
      <p style="color: #45556c; margin: 0 0 12px; font-size: 14px;">Use o código abaixo para continuar:</p>
      <div style="background: #ffffff; border-radius: 10px; padding: 20px 32px; text-align: center; margin: 0 0 24px; border: 1px solid #e5e7eb;">
        <span style="font-size: 36px; font-weight: 700; letter-spacing: 10px; color: #1a2b3c; font-family: monospace;">
          {token}
        </span>
      </div>
      <p style="color: #62748e; font-size: 13px; margin: 0;">
        Este código expira em <strong>15 minutos</strong>.<br>
        Se você não solicitou essa redefinição, ignore este e-mail.
      </p>
    </div>
    """
    if not BREVO_API_KEY:
        return
    requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "Content-Type": "application/json",
            "accept": "application/json",
        },
        json={
            "sender": {"email": BREVO_FROM_EMAIL, "name": BREVO_FROM_NAME},
            "to": [{"email": email}],
            "subject": "Código de redefinição de senha — Barcelos & Takaki",
            "htmlContent": html,
        },
        timeout=10,
    )


class ForgotPasswordBody(BaseModel):
    email: str


class VerifyTokenBody(BaseModel):
    email: str
    token: str


class ResetPasswordBody(BaseModel):
    email: str
    token: str
    nova_senha: str


@router.post("/forgot-password", status_code=200)
def forgot_password(body: ForgotPasswordBody, request: Request, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    # Remove tokens anteriores do mesmo email
    db.query(PasswordResetToken).filter(PasswordResetToken.email == body.email).delete()
    db.commit()

    user = _buscar_usuario_por_email(body.email)
    if user:
        raw_token = secrets.token_hex(3)  # 6-char hex
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        db.add(PasswordResetToken(email=body.email, token=raw_token, expires_at=expires_at))
        db.commit()
        _enviar_email_reset(body.email, raw_token)

        if ENVIRONMENT != "production":
            return {
                "message": "Se este e-mail estiver cadastrado, você receberá as instruções em breve.",
                "debug_token": raw_token,
            }

    return {"message": "Se este e-mail estiver cadastrado, você receberá as instruções em breve."}


@router.post("/verify-reset-token", status_code=200)
def verify_reset_token(body: VerifyTokenBody, db: Session = Depends(get_db)):
    record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.email == body.email,
            PasswordResetToken.token == body.token,
            PasswordResetToken.expires_at > func.now(),
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Token inválido ou expirado.")
    return {"valid": True}


@router.post("/reset-password", status_code=200)
def reset_password(body: ResetPasswordBody, db: Session = Depends(get_db)):
    pwd = body.nova_senha
    if len(pwd) < 8:
        raise HTTPException(status_code=422, detail="A senha deve ter pelo menos 8 caracteres.")
    if not re.search(r"[A-Z]", pwd):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos uma letra maiúscula.")
    if not re.search(r"[0-9]", pwd):
        raise HTTPException(status_code=422, detail="A senha deve conter pelo menos um número.")

    record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.email == body.email,
            PasswordResetToken.token == body.token,
            PasswordResetToken.expires_at > func.now(),
        )
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Token inválido ou expirado.")

    user = _buscar_usuario_por_email(body.email)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    admin_token = _obter_token_admin()
    resp = requests.put(
        f"{KEYCLOAK_SERVER_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user['id']}/reset-password",
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        json={"type": "password", "value": body.nova_senha, "temporary": False},
    )
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=500, detail="Erro ao atualizar senha no sistema de autenticação.")

    db.delete(record)
    db.commit()

    return {"message": "Senha redefinida com sucesso."}
