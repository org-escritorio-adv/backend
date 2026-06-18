"""Integração com o Cloudflare R2 (compatível com a API S3) para armazenar
imagens públicas, como as fotos dos advogados exibidas na landing page."""
import uuid

import boto3
from botocore.config import Config

from src import config

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = boto3.client(
            "s3",
            endpoint_url=config.R2_ENDPOINT,
            aws_access_key_id=config.R2_ACCESS_KEY_ID,
            aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )
    return _client


def r2_configurado() -> bool:
    """True se todas as variáveis necessárias do R2 estão definidas."""
    return all(
        [
            config.R2_ENDPOINT,
            config.R2_ACCESS_KEY_ID,
            config.R2_SECRET_ACCESS_KEY,
            config.R2_BUCKET_NAME,
            config.R2_PUBLIC_BASE_URL,
        ]
    )


def upload_imagem(conteudo: bytes, content_type: str, prefixo: str, extensao: str) -> str:
    """Sobe a imagem para o bucket e retorna a URL pública de leitura."""
    chave = f"{prefixo}/{uuid.uuid4().hex}{extensao}"
    _get_client().put_object(
        Bucket=config.R2_BUCKET_NAME,
        Key=chave,
        Body=conteudo,
        ContentType=content_type,
    )
    return f"{config.R2_PUBLIC_BASE_URL}/{chave}"


def remover_por_url(url: str | None) -> None:
    """Remove um objeto a partir da sua URL pública (best-effort: ignora erros)."""
    if not url or not url.startswith(config.R2_PUBLIC_BASE_URL):
        return
    chave = url[len(config.R2_PUBLIC_BASE_URL):].lstrip("/")
    if not chave:
        return
    try:
        _get_client().delete_object(Bucket=config.R2_BUCKET_NAME, Key=chave)
    except Exception:
        pass
