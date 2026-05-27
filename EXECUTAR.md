# Como Executar o Projeto

## 1. Setup Inicial

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 2. Obter Token GitHub

1. Acesse https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione escopos: `public_repo`, `read:user`
4. Copie o token gerado

## 3. Executar Análise

### Sintaxe Básica

```bash
python -m codigos.app.main \
  --owner <proprietário> \
  --repo <repositório> \
  --token <seu_token>
```

### Exemplo: Analisar pytorch/pytorch

```bash
python -m codigos.app.main \
  --owner pytorch \
  --repo pytorch \
  --token ghp_XXXXXXXXXXXXXXXXXXXXX \
  --output ./results_pytorch \
  --format csv,gexf,graphml
```

### Exemplo: Analisar torvalds/linux

```bash
python -m codigos.app.main \
  --owner torvalds \
  --repo linux \
  --token ghp_XXXXXXXXXXXXXXXXXXXXX \
  --output ./results_linux \
  --format csv,gexf
```

## 4. Opções Disponíveis

```
--owner             Dono do repositório (obrigatório)
--repo              Nome do repositório (obrigatório)
--token             Token GitHub (obrigatório)
--output            Diretório de saída (padrão: ./results)
--format            Formatos: csv,gexf,graphml (padrão: todos)
--impl              list (esparso) ou matrix (denso, padrão: list)
--verbose           Ativar saída detalhada
```

## 5. Saída Esperada

```
======================================================================
  Análise de Colaboração: pytorch/pytorch
======================================================================

[1/4] Minerando dados do GitHub...
  ✓ 1250 usuários encontrados
  ✓ 5000 interações mineradas

[2/4] Construindo grafos de colaboração...
  ✓ total: 1250 vértices, 3000 arestas, densidade=0.002
  ✓ issues: 1250 vértices, 1000 arestas, densidade=0.001
  ✓ pull_requests: 1250 vértices, 2000 arestas, densidade=0.001

[3/4] Calculando métricas de rede...
  ✓ 9 métricas calculadas para 1250 usuários
  ✓ PageRank médio: 0.0008
  ✓ Degree centrality média: 0.0048

  Top 5 colaboradores (by PageRank):
    1. torvalds: 0.0125
    2. linus: 0.0110
    3. gregkh: 0.0095
    4. davem: 0.0088
    5. rostedt: 0.0082

[4/4] Exportando em 3 formato(s)...
  ✓ CSV exportado: ./results/pytorch_pytorch_total_*.csv
  ✓ GEXF exportado: ./results/pytorch_pytorch_total.gexf
  ✓ GraphML exportado: ./results/pytorch_pytorch_total.graphml

======================================================================
  ✓ Análise concluída com sucesso!
  Arquivos gerados: 5
  Diretório: ./results
======================================================================
```

## 6. Visualizar Resultados

### CSV (Gephi Desktop)

1. Abra Gephi
2. File → Open → selecione `_nodes.csv`
3. Gephi importará automaticamente as arestas

### GEXF (Gephi Desktop)

1. Abra Gephi
2. File → Open → selecione `.gexf`

### GraphML (Gephi, Cytoscape, yEd)

1. Abra a ferramenta desejada
2. File → Open → selecione `.graphml`

## 7. Executar Testes

### Testes Unitários

```bash
# Todos os testes
python -m pytest tests/unit -v

# Testes específicos
python -m pytest tests/unit/test_models.py -v
python -m pytest tests/unit/test_graph_builder.py -v
python -m pytest tests/unit/test_metrics.py -v
python -m pytest tests/unit/test_exporters.py -v
```

### Testes de Integração

```bash
# Testes ponta-a-ponta
python -m pytest tests/integration -v
```

### Cobertura de Testes

```bash
python -m pytest tests/ --cov=codigos --cov-report=html
# Abra htmlcov/index.html no navegador
```

## 8. Troubleshooting

### "No module named 'pytest'"

```bash
pip install pytest pytest-cov
```

### "No module named 'networkx'"

```bash
pip install networkx
```

Sem networkx, algumas métricas retornarão 0 (graceful degradation).

### "Rate limit exceeded"

A API GitHub tem limite de 60 requisições/hora com autenticação.
O cliente espera automaticamente.

### "Repository not found"

- Verifique se `--owner` e `--repo` estão corretos
- Repositório deve ser público
- Verifique conectividade com Internet

## 9. Estrutura de Saída

```
results/
├── owner_repo_total_nodes.csv    # Nós com métricas
├── owner_repo_total_edges.csv    # Arestas e pesos
├── owner_repo_total.gexf         # Arquivo GEXF (XML)
└── owner_repo_total.graphml      # Arquivo GraphML (XML)
```

### Colunas do nodes.csv

- `id`: Índice do usuário
- `label`: Nome de usuário (login)
- `user_id`: ID GitHub
- `degree_centrality`: Centralidade de grau
- `in_degree`: Arestas entrando
- `out_degree`: Arestas saindo
- `betweenness_centrality`: Intermediação
- `closeness_centrality`: Proximidade
- `pagerank`: PageRank
- `clustering_coefficient`: Clustering
- `eigenvector_centrality`: Autovetor

### Colunas do edges.csv

- `source`: Índice do usuário origem
- `target`: Índice do usuário destino
- `weight`: Peso da interação (2, 4, 5)

## 10. Exemplos Práticos

### Analisar repositório pequeno

```bash
python -m codigos.app.main \
  --owner graphql \
  --repo graphql-js \
  --token <token> \
  --output ./results_small
```

### Usar matriz denso em vez de lista

```bash
python -m codigos.app.main \
  --owner pytorch \
  --repo pytorch \
  --token <token> \
  --impl matrix
```

### Apenas exportar CSV

```bash
python -m codigos.app.main \
  --owner torvalds \
  --repo linux \
  --token <token> \
  --format csv
```

### Modo verbose com mais detalhes

```bash
python -m codigos.app.main \
  --owner microsoft \
  --repo vscode \
  --token <token> \
  --verbose
```

## 11. Performance

- **Repositórios pequenos** (<100 usuários): ~30 segundos
- **Repositórios médios** (100-1000): ~2-5 minutos
- **Repositórios grandes** (>1000): ~10-30 minutos

Tempo depende de:
- Número de issues/PRs/comentários
- Velocidade da internet
- Rate limit do GitHub
