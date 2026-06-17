"""Matriz de permissões padrão por perfil e cálculo de permissões efetivas.

Espelha as chaves usadas em `frontend/src/pages/equipe/TeamManagement.tsx`
(`permissoesPadrao`). Um usuário pode ter um override individual salvo em
`Usuario.permissoes`; quando presente, ele substitui integralmente os
padrões do perfil para aquele usuário.
"""

PERMISSOES_PADRAO: dict[str, dict[str, bool]] = {
    "admin": {
        "visualizarProcessos": True,
        "criarProcessos": True,
        "editarProcessos": True,
        "excluirProcessos": True,
        "criarClientes": True,
        "editarPerfisSite": True,
        "publicarConteudo": True,
        "exportarDados": True,
        "acessarPainelAdmin": True,
        "gerenciarUsuarios": True,
    },
    "advogado": {
        "visualizarProcessos": True,
        "criarProcessos": True,
        "editarProcessos": True,
        "excluirProcessos": False,
        "criarClientes": True,
        "editarPerfisSite": False,
        "publicarConteudo": False,
        "exportarDados": True,
        "acessarPainelAdmin": False,
        "gerenciarUsuarios": False,
    },
    "estagiario": {
        "visualizarProcessos": True,
        "criarProcessos": False,
        "editarProcessos": False,
        "excluirProcessos": False,
        "criarClientes": False,
        "editarPerfisSite": False,
        "publicarConteudo": False,
        "exportarDados": False,
        "acessarPainelAdmin": False,
        "gerenciarUsuarios": False,
    },
}


def efetivas(perfil: str, overrides: dict | None) -> dict[str, bool]:
    """Retorna as permissões efetivas de um usuário.

    Se houver override salvo, ele tem precedência total sobre os padrões
    do perfil; caso contrário, usa os padrões do perfil (fallback p/ advogado).
    """
    if overrides:
        return dict(overrides)
    return dict(PERMISSOES_PADRAO.get(perfil, PERMISSOES_PADRAO["advogado"]))
