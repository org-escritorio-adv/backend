"""
Service central de notificações.

Qualquer parte do sistema que precise avisar um usuário deve chamar
`criar_notificacao(...)` daqui — ela grava a notificação no banco (para aparecer
no sininho do topo) e, opcionalmente, dispara um e-mail via Brevo.

Mantém o mesmo padrão de envio de e-mail já usado em src/auth/router.py.
"""

import requests
from sqlalchemy.orm import Session

from src.config import BREVO_API_KEY, BREVO_FROM_EMAIL, BREVO_FROM_NAME
from src.notificacoes.model import Notificacao
from src.usuarios.model import Usuario


def _montar_html_email(titulo: str, mensagem: str) -> str:
    return f"""
    <div style="font-family: Inter, sans-serif; max-width: 520px; margin: 0 auto; padding: 32px 24px; background: #f6f5f5; border-radius: 12px;">
      <h2 style="color: #1a2b3c; margin: 0 0 8px;">{titulo}</h2>
      <p style="color: #45556c; margin: 0 0 24px; font-size: 15px;">
        {mensagem}
      </p>
      <p style="color: #62748e; font-size: 13px; margin: 0;">
        Você está recebendo este e-mail porque é usuário do sistema
        <strong>Barcelos &amp; Takaki</strong>.
      </p>
    </div>
    """


def _enviar_email(destinatario: str, titulo: str, mensagem: str) -> None:
    """Envia um e-mail via Brevo. Falhas de e-mail nunca derrubam a operação."""
    if not BREVO_API_KEY or not destinatario:
        return
    try:
        requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            json={
                "sender": {"email": BREVO_FROM_EMAIL, "name": BREVO_FROM_NAME},
                "to": [{"email": destinatario}],
                "subject": titulo,
                "htmlContent": _montar_html_email(titulo, mensagem),
            },
            timeout=10,
        )
    except Exception as e:
        # Não propaga: se o e-mail falhar, a notificação no sininho já foi salva.
        print(f"Falha ao enviar e-mail de notificação: {e}")


def criar_notificacao(
    db: Session,
    titulo: str,
    mensagem: str,
    tipo: str = "geral",
    usuario_id: int | None = None,
    link: str | None = None,
    enviar_email: bool = False,
) -> Notificacao:
    """
    Cria uma notificação no banco e, se pedido, dispara e-mail.

    - usuario_id=None  → notificação "global" (visível para qualquer usuário).
    - enviar_email=True → manda e-mail para o usuário (se usuario_id informado)
      ou para todos os usuários (se usuario_id=None).
    """
    notificacao = Notificacao(
        usuario_id=usuario_id,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        link=link,
        lida=False,
    )
    db.add(notificacao)
    db.commit()
    db.refresh(notificacao)

    if enviar_email:
        if usuario_id is not None:
            usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
            if usuario and usuario.email:
                _enviar_email(usuario.email, titulo, mensagem)
        else:
            # notificação global → avisa todos os usuários por e-mail
            for usuario in db.query(Usuario).all():
                if usuario.email:
                    _enviar_email(usuario.email, titulo, mensagem)

    return notificacao