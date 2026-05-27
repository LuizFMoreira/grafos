# 🧪 GUIA COMPLETO DE TESTE DO PROJETO

**Data:** 2026-05-27  
**Objetivo:** Validar que tudo funciona 100% conforme especificado

---

## 📋 PRÉ-REQUISITOS

### 1. Python 3.8+ instalado
```bash
python --version
```
Resultado esperado: `Python 3.x.x`

### 2. Clonar o repositório
```bash
# Já está em: C:\Users\davin\Desktop\clone ti\grafos
cd "C:\Users\davin\Desktop\clone ti\grafos"
```

### 3. Criar ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Resultado esperado: Prompt muda para `(venv) C:\...`

### 4. Instalar dependências
```bash
pip install -r requirements.txt
```

Resultado esperado: Instala `requests`, `pytest`, `pytest-cov`, `black`, `pylint`

---

## ✅ TESTE 1: VALIDAR ESTRUTURA DO PROJETO

### Comando
```bash
# Windows PowerShell
Get-ChildItem -Path codigos -Recurse -Include "*.py" | Measure-Object | Select-Object -ExpandProperty Count

# Ou com Python
python -c "import os; print(sum(len(f) for _, _, f in os.walk('codigos') if f[0].endswith('.py')))"
```

### Resultado Esperado
- **Mínimo:** 20+ arquivos Python
- **Esperado:** 30+ arquivos
- **Verificar:** Todas as pastas existem (core/graph, models, github_miner, services, exporters, app)

---

## ✅ TESTE 2: TESTAR IMPORTAÇÕES BÁSICAS

### Comando
```bash
python -c "
from codigos.core.graph.abstract_graph import AbstractGraph
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph
from codigos.core.graph.adjacency_matrix_graph import AdjacencyMatrixGraph
from codigos.models.user import User
from codigos.models.interaction_type import InteractionType
print('✅ Todas as importações funcionam!')
"
```

### Resultado Esperado
```
✅ Todas as importações funcionam!
```

---

## ✅ TESTE 3: TESTAR CLASSE GRAPH (AdjacencyListGraph)

### Comando
```bash
python -c "
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph

# Criar grafo com 3 vértices
g = AdjacencyListGraph(3)
print(f'Vértices: {g.get_vertex_count()}')  # Esperado: 3
print(f'Arestas: {g.get_edge_count()}')    # Esperado: 0

# Adicionar arestas
g.add_edge(0, 1, weight=2.0)
g.add_edge(1, 2, weight=4.0)
print(f'Arestas após add: {g.get_edge_count()}')  # Esperado: 2

# Verificar arestas
print(f'tem aresta 0→1: {g.has_edge(0, 1)}')  # Esperado: True
print(f'tem aresta 1→0: {g.has_edge(1, 0)}')  # Esperado: False

# Verificar pesos
print(f'peso 0→1: {g.get_edge_weight(0, 1)}')  # Esperado: 2.0
print(f'peso 1→2: {g.get_edge_weight(1, 2)}')  # Esperado: 4.0

print('✅ AdjacencyListGraph funciona!')
"
```

### Resultado Esperado
```
Vértices: 3
Arestas: 0
Arestas após add: 2
tem aresta 0→1: True
tem aresta 1→0: False
peso 0→1: 2.0
peso 1→2: 4.0
✅ AdjacencyListGraph funciona!
```

---

## ✅ TESTE 4: TESTAR RESTRIÇÕES (Sem self-loops)

### Comando
```bash
python -c "
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph

g = AdjacencyListGraph(3)

# Tentar adicionar self-loop (0 → 0)
g.add_edge(0, 0, weight=5.0)

# Verificar que não foi criado
print(f'Arestas no grafo: {g.get_edge_count()}')  # Esperado: 0 (rejeitou)
print(f'tem self-loop 0→0: {g.has_edge(0, 0)}')   # Esperado: False

print('✅ Self-loops são rejeitados corretamente!')
"
```

### Resultado Esperado
```
Arestas no grafo: 0
tem self-loop 0→0: False
✅ Self-loops são rejeitados corretamente!
```

---

## ✅ TESTE 5: TESTAR IDEMPOTÊNCIA (Acumulação de Peso)

### Comando
```bash
python -c "
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph

g = AdjacencyListGraph(3)

# Adicionar aresta 0 → 1 com peso 2
g.add_edge(0, 1, weight=2.0)
print(f'Após 1ª add - peso 0→1: {g.get_edge_weight(0, 1)}')  # Esperado: 2.0

# Adicionar novamente (deve acumular)
g.add_edge(0, 1, weight=4.0)
print(f'Após 2ª add - peso 0→1: {g.get_edge_weight(0, 1)}')  # Esperado: 6.0

# Contar arestas (não deve duplicar)
print(f'Total de arestas: {g.get_edge_count()}')  # Esperado: 1 (não 2!)

print('✅ Pesos acumulam corretamente (idempotência)!')
"
```

### Resultado Esperado
```
Após 1ª add - peso 0→1: 2.0
Após 2ª add - peso 0→1: 6.0
Total de arestas: 1
✅ Pesos acumulam corretamente (idempotência)!
```

---

## ✅ TESTE 6: TESTAR MATRIX GRAPH

### Comando
```bash
python -c "
from codigos.core.graph.adjacency_matrix_graph import AdjacencyMatrixGraph

# Criar grafo 3x3
g = AdjacencyMatrixGraph(3)
g.add_edge(0, 1, weight=2.0)
g.add_edge(1, 2, weight=5.0)

print(f'Vértices: {g.get_vertex_count()}')  # Esperado: 3
print(f'Arestas: {g.get_edge_count()}')    # Esperado: 2
print(f'Peso 0→1: {g.get_edge_weight(0, 1)}')  # Esperado: 2.0
print(f'Peso 1→2: {g.get_edge_weight(1, 2)}')  # Esperado: 5.0

print('✅ AdjacencyMatrixGraph funciona!')
"
```

### Resultado Esperado
```
Vértices: 3
Arestas: 2
Peso 0→1: 2.0
Peso 1→2: 5.0
✅ AdjacencyMatrixGraph funciona!
```

---

## ✅ TESTE 7: TESTAR MODELOS (User, InteractionType)

### Comando
```bash
python -c "
from codigos.models.user import User
from codigos.models.interaction_type import InteractionType

# Criar usuário
user1 = User(id=1, login='alice')
user2 = User(id=2, login='bob')

print(f'User 1: {user1.login} (ID: {user1.id})')  # Esperado: alice (ID: 1)
print(f'User 2: {user2.login} (ID: {user2.id})')  # Esperado: bob (ID: 2)

# Testar InteractionType
issue_comment = InteractionType.ISSUE_COMMENT
print(f'Tipo: {issue_comment}')
print(f'Peso: {issue_comment.weight}')  # Esperado: 2

pr_merge = InteractionType.PR_MERGE
print(f'Tipo: {pr_merge}')
print(f'Peso: {pr_merge.weight}')  # Esperado: 5

print('✅ Modelos funcionam!')
"
```

### Resultado Esperado
```
User 1: alice (ID: 1)
User 2: bob (ID: 2)
Tipo: InteractionType.ISSUE_COMMENT
Peso: 2
Tipo: InteractionType.PR_MERGE
Peso: 5
✅ Modelos funcionam!
```

---

## ✅ TESTE 8: RODAR TESTES UNITÁRIOS

### Comando
```bash
# Instalar pytest se não tiver
pip install pytest pytest-cov

# Rodar testes
python -m pytest tests/unit -v
```

### Resultado Esperado
```
tests/unit/test_models.py ...................... [50%]
tests/unit/test_graph_builder.py ............... [80%]
tests/unit/test_metrics.py .................... [95%]
tests/unit/test_exporters.py .................. [100%]

==================== X passed in Y.XXs ====================
```

Mínimo esperado: **50+ testes passando**

---

## ✅ TESTE 9: TESTAR BUILDER SERVICE

### Comando
```bash
python -c "
from datetime import datetime
from codigos.models.user import User
from codigos.models.github_data import (
    CollaborationGraph, Issue, Comment
)
from codigos.services.graph_builder import GraphBuilderService

# Criar dados de exemplo
users = [
    User(id=1, login='alice'),
    User(id=2, login='bob'),
    User(id=3, login='charlie'),
]

now = datetime.now()

# Issue comentada por alice e bob
issue = Issue(
    number=1,
    title='Fix bug',
    author=users[0],  # alice
    created_at=now,
    updated_at=now,
    url='https://github.com/test/repo/issues/1',
    state='open'
)

# Comentários criando arestas
comments = [
    Comment(
        id=1,
        author=users[1],  # bob comentando
        body='Good catch',
        created_at=now,
        updated_at=now,
        url='https://github.com/test/repo/issues/1#comment-1',
        issue_number=1
    ),
    Comment(
        id=2,
        author=users[2],  # charlie comentando
        body='LGTM',
        created_at=now,
        updated_at=now,
        url='https://github.com/test/repo/issues/1#comment-2',
        issue_number=1
    ),
]

# Criar grafo de colaboração
collab_graph = CollaborationGraph(
    repository='test/repo',
    users=users,
    issues=[issue],
    comments=comments,
    pull_requests=[],
    reviews=[],
    mined_at=now
)

# Construir grafo
builder = GraphBuilderService(use_adjacency_list=True)
graph = builder.build_collaboration_graph(collab_graph)

print(f'Vértices: {graph.get_vertex_count()}')  # Esperado: 3
print(f'Arestas: {graph.get_edge_count()}')    # Esperado: 2
print(f'Bob → Alice: {graph.has_edge(1, 0)}')  # Esperado: True
print(f'Charlie → Alice: {graph.has_edge(2, 0)}')  # Esperado: True

print('✅ GraphBuilderService funciona!')
"
```

### Resultado Esperado
```
Vértices: 3
Arestas: 2
Bob → Alice: True
Charlie → Alice: True
✅ GraphBuilderService funciona!
```

---

## ✅ TESTE 10: TESTAR MÉTRICAS

### Comando
```bash
python -c "
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph
from codigos.models.user import User
from codigos.services.metrics import MetricsService

# Criar grafo simples em forma de estrela
#     0
#    /|\\
#   1 2 3

g = AdjacencyListGraph(4)
g.add_edge(1, 0, weight=1.0)
g.add_edge(2, 0, weight=1.0)
g.add_edge(3, 0, weight=1.0)

# Criar usuários
users = [
    User(id=i, login=f'user{i}')
    for i in range(4)
]

# Calcular métricas
metrics_service = MetricsService(g, users)
all_metrics = metrics_service.calculate_all_metrics()

print(f'Número de usuários com métricas: {len(all_metrics)}')  # Esperado: 4

for metric in all_metrics:
    print(f'{metric.user.login}: pagerank={metric.pagerank:.4f}, degree={metric.degree_centrality:.4f}')

print('✅ MetricsService funciona!')
"
```

### Resultado Esperado
```
Número de usuários com métricas: 4
user0: pagerank=0.5000, degree=0.6667
user1: pagerank=0.1667, degree=0.3333
user2: pagerank=0.1667, degree=0.3333
user3: pagerank=0.1667, degree=0.3333
✅ MetricsService funciona!
```

---

## ✅ TESTE 11: TESTAR EXPORTADORES

### Comando
```bash
python -c "
import os
import tempfile
from codigos.core.graph.adjacency_list_graph import AdjacencyListGraph
from codigos.models.user import User
from codigos.services.metrics import MetricsService
from codigos.exporters.csv_exporter import CSVExporter
from codigos.exporters.gexf_exporter import GEXFExporter

# Criar grafo
g = AdjacencyListGraph(2)
g.add_edge(0, 1, weight=2.0)

users = [
    User(id=1, login='alice'),
    User(id=2, login='bob'),
]

# Calcular métricas
metrics = MetricsService(g, users).calculate_all_metrics()

# Exportar em tempdir
with tempfile.TemporaryDirectory() as tmpdir:
    csv_path = os.path.join(tmpdir, 'test')
    csv_exporter = CSVExporter(g, metrics)
    csv_exporter.export(csv_path)
    
    # Verificar arquivos
    nodes_exist = os.path.exists(f'{csv_path}_nodes.csv')
    edges_exist = os.path.exists(f'{csv_path}_edges.csv')
    
    print(f'nodes.csv criado: {nodes_exist}')  # Esperado: True
    print(f'edges.csv criado: {edges_exist}')  # Esperado: True
    
    # Exportar GEXF
    gexf_path = os.path.join(tmpdir, 'test.gexf')
    gexf_exporter = GEXFExporter(g, metrics)
    gexf_exporter.export(gexf_path)
    
    gexf_exist = os.path.exists(gexf_path)
    print(f'test.gexf criado: {gexf_exist}')  # Esperado: True

print('✅ Exportadores funcionam!')
"
```

### Resultado Esperado
```
nodes.csv criado: True
edges.csv criado: True
test.gexf criado: True
✅ Exportadores funcionam!
```

---

## ✅ TESTE 12: TESTAR CLI COM ARGUMENTO

### Comando
```bash
# Verificar que CLI reconhece argumentos
python -m codigos.app.main --help
```

### Resultado Esperado
```
usage: main.py [-h] --owner OWNER --repo REPO --token TOKEN 
               [--output OUTPUT] [--format FORMAT] [--impl {list,matrix}] 
               [--verbose]

optional arguments:
  -h, --help           show this help message and exit
  --owner OWNER        GitHub repository owner (required)
  --repo REPO          GitHub repository name (required)
  --token TOKEN        GitHub API token (required)
  --output OUTPUT      Output directory (default: ./results)
  --format FORMAT      Export formats: csv,gexf,graphml (default: all)
  --impl {list,matrix} Graph implementation: list or matrix
  --verbose            Enable verbose output
```

---

## ✅ TESTE 13: TESTAR CLI COM MOCK (Sem GitHub API)

### Comando
```bash
python -c "
from unittest.mock import patch, MagicMock
from codigos.app.main import main
from codigos.models.user import User
from codigos.models.github_data import CollaborationGraph
from datetime import datetime

# Mock da API GitHub
with patch('codigos.app.main.DataTransformer') as mock_transformer:
    users = [User(id=1, login='alice')]
    collab_graph = CollaborationGraph(
        repository='test/repo',
        users=users,
        mined_at=datetime.now()
    )
    
    mock_instance = MagicMock()
    mock_instance.mine_repository.return_value = collab_graph
    mock_transformer.return_value = mock_instance
    
    # Chamar main com mock
    with patch('codigos.app.main.GraphBuilderService'):
        with patch('codigos.app.main.MetricsService'):
            with patch('codigos.app.main.CSVExporter'):
                result = main(['--owner', 'test', '--repo', 'repo', '--token', 'token'])
                print(f'CLI retornou: {result}')  # Esperado: 0 ou 1

print('✅ CLI com mock funciona!')
"
```

### Resultado Esperado
```
CLI retornou: 0
✅ CLI com mock funciona!
```

---

## ✅ TESTE 14: TESTAR COM DADOS REAIS (OPCIONAL - Requer Token GitHub)

### Pré-requisito: Token GitHub
1. Ir para https://github.com/settings/tokens
2. Gerar novo token (classic)
3. Escopos: `public_repo`, `read:user`
4. Copiar token

### Comando
```bash
# Substituir SEU_TOKEN pelo token real
set GITHUB_TOKEN=ghp_SeuTokenAqui

python -m codigos.app.main \
  --owner graphql \
  --repo graphql-js \
  --token %GITHUB_TOKEN% \
  --output ./results_test \
  --format csv \
  --verbose
```

### Resultado Esperado
```
======================================================================
  Análise de Colaboração: graphql/graphql-js
======================================================================

[1/4] Minerando dados do GitHub...
  ✓ XXX usuários encontrados
  ✓ XXX interações mineradas

[2/4] Construindo grafos de colaboração...
  ✓ total: XXX vértices, XXX arestas, densidade=X.XXX
  ✓ issues: XXX vértices, XXX arestas
  ✓ pull_requests: XXX vértices, XXX arestas

[3/4] Calculando métricas de rede...
  ✓ 9 métricas calculadas para XXX usuários
  ✓ PageRank médio: 0.XXX
  ✓ Degree centrality média: 0.XXX

[4/4] Exportando em 1 formato(s)...
  ✓ CSV exportado: ./results_test/...

======================================================================
  ✓ Análise concluída com sucesso!
======================================================================
```

---

## 📊 CHECKLIST DE TESTES COMPLETO

- [ ] **TESTE 1:** Estrutura do projeto (30+ arquivos)
- [ ] **TESTE 2:** Importações básicas (sem erros)
- [ ] **TESTE 3:** AdjacencyListGraph (arestas funcionam)
- [ ] **TESTE 4:** Self-loops rejeitados (count = 0)
- [ ] **TESTE 5:** Idempotência (pesos acumulam)
- [ ] **TESTE 6:** AdjacencyMatrixGraph (igual ao list)
- [ ] **TESTE 7:** Modelos (User, InteractionType)
- [ ] **TESTE 8:** Testes unitários (50+ passando)
- [ ] **TESTE 9:** GraphBuilderService (grafos criados)
- [ ] **TESTE 10:** MetricsService (9 métricas)
- [ ] **TESTE 11:** Exportadores (CSV, GEXF, GraphML)
- [ ] **TESTE 12:** CLI --help (argumentos reconhecidos)
- [ ] **TESTE 13:** CLI com mock (retorna 0 ou 1)
- [ ] **TESTE 14:** Teste com dados reais (OPCIONAL)

---

## 🎯 SE ALGUM TESTE FALHAR

### Problema: `ModuleNotFoundError`
```bash
# Solução: Reinstalar requirements
pip install -r requirements.txt --force-reinstall
```

### Problema: `InvalidVertexError`
```bash
# Solução: Verificar índices (0-based)
# Grafo com 3 vértices: índices são 0, 1, 2 (NOT 1, 2, 3)
```

### Problema: Teste de CLI não acha DataTransformer
```bash
# Solução: Verificar import no main.py
from codigos.github_miner import DataTransformer
```

### Problema: `pytest` não encontrado
```bash
pip install pytest pytest-cov
python -m pytest tests/unit -v
```

---

## ✅ PRÓXIMOS PASSOS

Após passar em todos os testes:

1. **Teste com dados reais:** Use um repositório pequeno (graphql-js)
2. **Visualizar em Gephi:** Abra arquivo CSV/GEXF no Gephi
3. **Preparar apresentação:** Capture screenshots dos resultados
4. **Criar relatório:** Documente os resultados em LaTeX

---

**Último update:** 2026-05-27  
**Status:** Guia pronto para teste completo do projeto
