"""
Rotina automática de sincronização diária com o DataJud (US 2.1.2).

- Roda todos os dias num horário fixo (configurável abaixo).
- Para cada processo cadastrado, consulta o DataJud e adiciona movimentações novas.
- Gera notificação (sininho + e-mail) quando há movimentação nova (US 4.1.1).
- Gera notificação de falha se o DataJud estiver indisponível (US 2.1.2).
- Registra log de execução no console (visível em `docker compose logs backend`).
"""

from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

import src.models  # noqa: F401 — garante que TODOS os models sejam registrados
from src.database import SessionLocal
from src.apiJud import repository
from src.processos.model import Processo
from src.notificacoes.service import criar_notificacao

# Horário da rotina diária (hora e minuto, no fuso do servidor).
HORA_SINCRONIZACAO = 3
MINUTO_SINCRONIZACAO = 0

scheduler = BackgroundScheduler()


def sincronizar_processos_automaticamente():
    """Executada automaticamente pelo agendador, uma vez por dia."""
    inicio = datetime.now(timezone.utc)
    print(f"[SYNC DIÁRIA] Início: {inicio.isoformat()}")

    db = SessionLocal()
    try:
        processos = db.query(Processo).all()
        total = len(processos)
        sucesso = 0
        falhas = 0
        movimentacoes_novas_total = 0

        for processo in processos:
            try:
                raw = repository.consultar_por_numero(processo.numero_cnj, processo.tribunal)
            except ValueError:
                # tribunal inválido nesse processo — não é falha do DataJud
                falhas += 1
                continue
            except Exception as e:
                # DataJud indisponível: registra log, gera notificação de falha e aborta
                print(f"[SYNC DIÁRIA] FALHA — DataJud indisponível: {e}")
                criar_notificacao(
                    db,
                    titulo="Falha na sincronização automática",
                    mensagem=(
                        "A rotina automática de atualização dos processos não conseguiu "
                        "se conectar ao DataJud hoje. Os dados podem estar desatualizados. "
                        "Tente sincronizar manualmente mais tarde."
                    ),
                    tipo="sincronizacao_falha",
                    enviar_email=True,
                )
                return  # aborta a rotina inteira

            hits = raw.get("hits", {}).get("hits", [])
            if not hits:
                falhas += 1
                continue

            source = hits[0]["_source"]
            try:
                _, qtd_novas = repository.sincronizar_processo(
                    db,
                    source,
                    cliente_id=processo.cliente_id,
                    advogado_id=processo.advogado_id,
                )
                sucesso += 1
                if qtd_novas > 0:
                    movimentacoes_novas_total += qtd_novas
                    criar_notificacao(
                        db,
                        titulo="Nova movimentação processual",
                        mensagem=(
                            f"O processo {processo.numero_cnj} teve "
                            f"{qtd_novas} nova(s) movimentação(ões)."
                        ),
                        tipo="nova_movimentacao",
                        enviar_email=False,  # movimentação só no sininho, sem e-mail
                    )
            except Exception as e:
                print(f"[SYNC DIÁRIA] Erro ao salvar {processo.numero_cnj}: {e}")
                falhas += 1

        fim = datetime.now(timezone.utc)
        print(
            f"[SYNC DIÁRIA] Fim: {fim.isoformat()} | "
            f"processos={total} sucesso={sucesso} falhas={falhas} "
            f"movimentacoes_novas={movimentacoes_novas_total}"
        )
    finally:
        db.close()


def iniciar_scheduler():
    """Registra a rotina diária e liga o agendador. Chamado no startup do app."""
    scheduler.add_job(
        sincronizar_processos_automaticamente,
        trigger="cron",
        hour=HORA_SINCRONIZACAO,
        minute=MINUTO_SINCRONIZACAO,
        id="sincronizacao_diaria_datajud",
        replace_existing=True,
    )
    scheduler.start()
    print(
        f"[SCHEDULER] Rotina diária agendada para "
        f"{HORA_SINCRONIZACAO:02d}:{MINUTO_SINCRONIZACAO:02d} (horário do servidor)."
    )