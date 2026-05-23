** Módulo de Acesso (Segurança)**

* `perfis` (Roles: Admin, Advogado, Estagiário)
* `usuarios` (FK -> perfil_id)

** Módulo de Clientes e Negócios**

* `clientes` (Dados pessoais/empresariais)
* `casos` (A pasta do cliente. FK -> cliente_id)
* `equipe_caso` (Liga Vários Usuários a Vários Casos)
* `documentos` (FK -> caso_id)

** Módulo Judicial (Contencioso)**

* `tribunais`
* `processos` (FK -> caso_id, tribunal_id)
* `movimentacoes` (FK -> processo_id)
* `audiencias` (FK -> processo_id)

** Módulo de Produtividade**

* `tarefas_prazos` (Pode ter FK -> caso_id ou processo_id, e FK -> usuario_responsavel_id)
* `notificacoes` (FK -> usuario_id)

** Módulo de Preferências (Dashboard)**

* `processos_favoritos` (Liga Usuário <-> Processo)
* `casos_favoritos` (Liga Usuário <-> Caso)

** Módulo Externo (Site)**

* `leads_site` (Os contatos que chegam do site)
