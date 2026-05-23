#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-http://localhost:8000}"
H="Content-Type: application/json"

echo "=== Health ==="
curl -s "$BASE/health/db" | jq

echo "=== Usuário ==="
USUARIO=$(curl -s -X POST "$BASE/usuarios/" -H "$H" -d '{
  "nome": "Dr. Silva",
  "email": "silva@escritorio.com",
  "senha": "teste123",
  "perfil": "advogado"
}')
echo "$USUARIO" | jq
USUARIO_ID=$(echo "$USUARIO" | jq -r '.id')

echo "=== Cliente ==="
CLIENTE=$(curl -s -X POST "$BASE/clientes/" -H "$H" -d '{
  "nome_razao_social": "Maria Oliveira",
  "cpf_cnpj": "123.456.789-00",
  "telefone": "(11) 99999-0000",
  "email": "maria@email.com"
}')
echo "$CLIENTE" | jq
CLIENTE_ID=$(echo "$CLIENTE" | jq -r '.id')

echo "=== Lead ==="
curl -s -X POST "$BASE/leads/" -H "$H" -d '{
  "nome": "João Lead",
  "email": "joao@email.com",
  "telefone": "(11) 98888-7777",
  "mensagem": "Quero consulta trabalhista",
  "status": "Novo"
}' | jq

echo "=== Processo ==="
PROCESSO=$(curl -s -X POST "$BASE/processos/" -H "$H" -d '{
  "number": "00012345620238260000",
  "court": "TJSP",
  "parts": "Maria vs. Empresa X",
  "start_date": "2024-01-15",
  "status": "ativo"
}')
echo "$PROCESSO" | jq
PROCESSO_ID=$(echo "$PROCESSO" | jq -r '.id')

echo "=== Tarefa ==="
curl -s -X POST "$BASE/tarefas/" -H "$H" -d "{
  \"titulo\": \"Revisar petição\",
  \"descricao\": \"Urgente\",
  \"processo_id\": $PROCESSO_ID,
  \"responsavel_id\": $USUARIO_ID,
  \"status\": \"aberta\"
}" | jq

echo "=== Prazo ==="
curl -s -X POST "$BASE/prazos/" -H "$H" -d "{
  \"titulo\": \"Contestação\",
  \"data_limite\": \"2026-06-01\",
  \"processo_id\": $PROCESSO_ID,
  \"status\": \"pendente\"
}" | jq

echo "=== Listagens ==="
curl -s "$BASE/clientes/" | jq 'length'
curl -s "$BASE/processos/" | jq 'length'
curl -s "$BASE/leads/" | jq 'length'

echo "=== PATCH lead ==="
LEAD_ID=$(curl -s "$BASE/leads/" | jq -r '.[0].id')
curl -s -X PATCH "$BASE/leads/$LEAD_ID" -H "$H" \
  -d '{"status": "Em contato"}' | jq

echo "=== Favoritar processo ==="
curl -s -X PATCH "$BASE/processos/$PROCESSO_ID/favoritar" | jq '.favorite'

echo "OK"