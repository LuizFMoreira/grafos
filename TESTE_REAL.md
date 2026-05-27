# 🚀 TESTE REAL DA APLICAÇÃO - GitHub API

**Objetivo:** Rodar a aplicação de verdade contra um repositório real do GitHub

---

## 📋 STEP 1: OBTER TOKEN GITHUB (5 minutos)

### 1. Acesse https://github.com/settings/tokens

### 2. Clique em "Generate new token (classic)"

### 3. Configure o token:
- **Name:** `graph-analysis-token` (ou qualquer nome)
- **Expiration:** 90 days (ou mais)
- **Scopes (marque):**
  - ☑️ `public_repo` (ler repos públicos)
  - ☑️ `read:user` (ler dados de usuários)

### 4. Copie o token (exemplo: `ghp_abc123xyz...`)

⚠️ **GUARDE ESTE TOKEN COM SEGURANÇA** - não o compartilhe!

---

## 🔧 STEP 2: SETUP AMBIENTE (2 minutos)

### Terminal/PowerShell:
```bash
# Ir para o diretório do projeto
cd "C:\Users\davin\Desktop\clone ti\grafos"

# Ativar venv
venv\Scripts\activate

# Instalar dependências (se não fez ainda)
pip install -r requirements.txt
```

### Resultado esperado:
```
(venv) C:\Users\davin\Desktop\clone ti\grafos>
```

---

## 🧪 TESTE 1: Repositório PEQUENO (3-5 min)

**Repositório:** `graphql/graphql-js`
- ⭐ ~8.000 stars
- 👥 ~150 colaboradores
- ⚡ Rápido (boa para teste inicial)

### Comando:
```bash
python -m codigos.app.main ^
  --owner graphql ^
  --repo graphql-js ^
  --token ghp_SEU_TOKEN_AQUI ^
  --output ./results_graphql ^
  --format csv,gexf,graphml ^
  --verbose
```

### Resultado esperado:
```
======================================================================
  Análise de Colaboração: graphql/graphql-js
======================================================================

[1/4] Minerando dados do GitHub...
  ✓ 150 usuários encontrados
  ✓ 500 interações mineradas

[2/4] Construindo grafos de colaboração...
  ✓ total: 150 vértices, 300 arestas, densidade=0.013
  ✓ issues: 150 vértices, 100 arestas, densidade=0.004
  ✓ pull_requests: 150 vértices, 200 arestas, densidade=0.009

[3/4] Calculando métricas de rede...
  ✓ 9 métricas calculadas para 150 usuários
  ✓ PageRank médio: 0.0067
  ✓ Degree centrality média: 0.0044

  Top 5 colaboradores (by PageRank):
    1. user1: 0.0234
    2. user2: 0.0189
    3. user3: 0.0156
    4. user4: 0.0123
    5. user5: 0.0098

[4/4] Exportando em 3 formato(s)...
  ✓ CSV exportado: ./results_graphql/graphql_graphql-js_total_nodes.csv
  ✓ GEXF exportado: ./results_graphql/graphql_graphql-js_total.gexf
  ✓ GraphML exportado: ./results_graphql/graphql_graphql-js_total.graphml

======================================================================
  ✓ Análise concluída com sucesso!
  Arquivos gerados: 6
  Diretório: ./results_graphql
======================================================================
```

### Verificar resultados:
```bash
# Windows
dir results_graphql

# Linux/Mac
ls -la results_graphql
```

Deve ter arquivos:
- `graphql_graphql-js_total_nodes.csv`
- `graphql_graphql-js_total_edges.csv`
- `graphql_graphql-js_issues_nodes.csv`
- `graphql_graphql-js_issues_edges.csv`
- `graphql_graphql-js_pull_requests_nodes.csv`
- `graphql_graphql-js_pull_requests_edges.csv`
- `graphql_graphql-js_total.gexf`
- `graphql_graphql-js_pull_requests.graphml`
- etc...

---

## 🧪 TESTE 2: Repositório MÉDIO (5-10 min)

**Repositório:** `torvalds/linux`
- ⭐ ~170.000 stars
- 👥 ~2.000+ colaboradores
- ⚠️ Pode levar mais tempo

### Comando:
```bash
python -m codigos.app.main ^
  --owner torvalds ^
  --repo linux ^
  --token ghp_SEU_TOKEN_AQUI ^
  --output ./results_linux ^
  --format csv
```

---

## 🧪 TESTE 3: Repositório GRANDE (10-30 min)

**Repositório:** `pytorch/pytorch`
- ⭐ ~75.000 stars
- 👥 ~1.500+ colaboradores
- ⚠️ Bastante dado (pode demorar)

### Comando:
```bash
python -m codigos.app.main ^
  --owner pytorch ^
  --repo pytorch ^
  --token ghp_SEU_TOKEN_AQUI ^
  --output ./results_pytorch ^
  --format csv,gexf
```

---

## 📊 STEP 3: EXAMINAR RESULTADOS

### 1. Abrir arquivo CSV
```bash
# Windows
start results_graphql\graphql_graphql-js_total_nodes.csv

# Ou no Excel/Calc
```

Deve ver colunas:
- `id` — Índice do usuário
- `label` — Username
- `degree_centrality` — Centralidade (0-1)
- `pagerank` — PageRank
- `in_degree` — Arestas entrando
- `out_degree` — Arestas saindo
- `betweenness_centrality` — Intermediação
- `closeness_centrality` — Proximidade
- `clustering_coefficient` — Clustering local

### 2. Examinar arquivo edges.csv
```bash
start results_graphql\graphql_graphql-js_total_edges.csv
```

Deve ver colunas:
- `source` — Usuário origem
- `target` — Usuário destino
- `weight` — Peso da interação (2, 4, 5)

### 3. Visualizar em Gephi (OPCIONAL)
Se tiver Gephi instalado:
1. Abrir Gephi
2. File → Open → `graphql_graphql-js_total.gexf`
3. Ver grafo visualizado com layout (Force Atlas 2)

---

## ⚙️ OPÇÕES DE CLI

### `--format` (múltiplos formatos)
```bash
# Todos os formatos
--format csv,gexf,graphml

# Apenas CSV
--format csv

# GEXF e GraphML
--format gexf,graphml
```

### `--impl` (implementação de grafo)
```bash
# Lista de adjacência (padrão, mais rápido)
--impl list

# Matriz de adjacência (mais visual, mais lento)
--impl matrix
```

### `--verbose` (saída detalhada)
```bash
# Ver logs de cada requisição
--verbose
```

### `--output` (diretório de saída)
```bash
# Padrão é ./results
--output ./meus_resultados
```

---

## 🐛 TROUBLESHOOTING

### ❌ "401 Unauthorized"
**Problema:** Token inválido ou expirado
**Solução:** 
1. Gere novo token em https://github.com/settings/tokens
2. Copie corretamente (sem espaços)

### ❌ "404 Not Found"
**Problema:** Repositório não existe ou nome errado
**Solução:**
```bash
# Verificar corretamente em https://github.com/OWNER/REPO
python -m codigos.app.main --owner pytorch --repo pytorch --token TOKEN
# ✅ Correto: pytorch/pytorch
# ❌ Errado: pytorch/PyTorch ou pytorch-pytorch
```

### ❌ "Rate limit exceeded"
**Problema:** Você já fez muitas requisições
**Solução:** 
- Aguarde 1 hora (reset automático)
- Ou use repositório menor
- Token clássico = 60 req/hora (autenticado)

### ❌ "Connection timeout"
**Problema:** Conexão com internet ou GitHub down
**Solução:**
- Verificar internet
- Tentar novamente
- Verificar status de GitHub em https://www.githubstatus.com

---

## 📈 EXEMPLO REAL COMPLETO

### Seu comando:
```bash
python -m codigos.app.main ^
  --owner graphql ^
  --repo graphql-js ^
  --token ghp_abc123xyz... ^
  --output ./resultados_graphql ^
  --format csv,gexf,graphml ^
  --verbose
```

### O que acontece internamente:

1. **[1/4] Mineração de dados**
   - Busca issues (paginado)
   - Busca pull requests (paginado)
   - Busca comentários em issues
   - Busca comentários em PRs
   - Busca reviews de PRs
   - Extrai usuários únicos
   - Cria mapa de usuários → índices

2. **[2/4] Construção de grafos**
   - Graph 1: apenas comentários em issues
   - Graph 2: apenas PRs (reviews + merges)
   - Graph 3: todas interações (combinado)
   - Calcula estatísticas (vértices, arestas, densidade)

3. **[3/4] Cálculo de métricas**
   - Degree centrality (in + out degree)
   - In-degree e out-degree
   - Betweenness centrality (caminhos mais curtos)
   - Closeness centrality (proximidade)
   - PageRank (importância)
   - Clustering coefficient (triângulos)
   - Eigenvector centrality (importância recursiva)
   - Harmonic centrality (distância harmônica)
   - Ranking (top 5 por métrica)

4. **[4/4] Exportação**
   - CSV (nodes + edges) para Gephi
   - GEXF (XML com atributos)
   - GraphML (XML universal)

### Resultado final:
Arquivos prontos para:
- 📊 Análise em Excel
- 🎨 Visualização em Gephi
- 📈 Inclusão em apresentação/relatório

---

## ✅ CHECKLIST TESTE REAL

- [ ] Token GitHub obtido e testado
- [ ] Environment ativado (`venv\Scripts\activate`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] **TESTE 1:** Rodou com graphql-js (pequeno)
- [ ] Verificou arquivos em `results_graphql`
- [ ] Abriu CSV em Excel e viu dados
- [ ] **TESTE 2:** Rodou com outro repositório (médio)
- [ ] Visualizou em Gephi (opcional)
- [ ] Entendeu as métricas nos resultados
- [ ] Pronto para apresentação!

---

## 🎯 PRÓXIMAS ETAPAS

1. **Teste com 2-3 repositórios** para ter dados variados
2. **Capture screenshots** dos resultados para o relatório
3. **Analise os dados:** Quem são os top colaboradores? Qual é a densidade?
4. **Prepare a apresentação** com os resultados reais

---

**Dica:** Comece com graphql-js (rápido) para validar que tudo funciona, depois teste com pytorch (mais dados para análise)

**Qualquer erro? Me avisa qual é a mensagem de erro que aparece!**
