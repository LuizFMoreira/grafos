# 📊 Sistema de Análise de Colaboração em Repositórios GitHub

Um projeto de engenharia de software que implementa uma ferramenta completa para analisar padrões de colaboração em repositórios GitHub, modelando interações entre colaboradores como grafos direcionados ponderados.

## 🎯 Objetivo

Desenvolver uma ferramenta que:
- Minera dados de um repositório GitHub (issues, PRs, reviews, comments)
- Transforma interações em estruturas de grafo
- Implementa grafos sem usar bibliotecas prontas
- Calcula métricas complexas de redes sociais
- Exporta resultados para visualização no Gephi

## 🏗️ Arquitetura

### Estrutura de Camadas

```
┌─────────────────────────────────────────────────┐
│         CLI / Interface de Usuário              │
├─────────────────────────────────────────────────┤
│              Serviços (Orquestração)            │
├──────────────┬────────────────┬─────────────────┤
│              │                │                 │
├────────────┐ ├──────────────┐ ├────────────────┐│
│   Grafos   │ │ GitHub Miner │ │    Métricas   ││
├────────────┘ ├──────────────┘ ├────────────────┘│
│                                                 │
│              Modelos de Domínio                 │
└─────────────────────────────────────────────────┘
```

### Diretórios Principais

```
codigos/
├── core/               # Estruturas de grafos
│   └── graph/
│       ├── edge.py
│       ├── abstract_graph.py
│       ├── adjacency_list_graph.py
│       └── adjacency_matrix_graph.py
├── models/             # Modelos de domínio
├── github_miner/       # Coleta de dados
├── services/           # Orquestração
├── metrics/            # Cálculo de métricas
├── exporters/          # Exportação para Gephi
├── exceptions/         # Exceções customizadas
├── utils/              # Utilidades
└── app/                # Interface CLI
```

## 🚀 Início Rápido

### Instalação

```bash
# 1. Clone o repositório
git clone <repo-url>
cd projeto-grafos

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt
```

### Configuração

```bash
# 1. Crie um arquivo .env baseado em .env.example
cp .env.example .env

# 2. Adicione seu token do GitHub (em https://github.com/settings/tokens)
# GITHUB_TOKEN=seu_token_aqui
```

### Execução

```bash
# Execute a aplicação principal
python -m codigos.app.main
```

## 📖 Conceitos Fundamentais

### O que é um Grafo?

Um grafo é um mapa de conexões composto por:
- **Vértices**: Pontos (neste projeto: colaboradores)
- **Arestas**: Conexões direcionadas entre vértices (interações)
- **Pesos**: Intensidade das conexões

### Tipos de Interação e Pesos

| Tipo | Peso | Exemplo |
|---|---|---|
| Comentário em issue | 2 | Ana comenta em issue de Bruno |
| Abertura de issue comentada | 3 | Ana abre issue que Bruno comenta |
| Review/Aprovação em PR | 4 | Ana faz review em PR de Bruno |
| Merge de PR | 5 | Ana faz merge de PR de Bruno |

### Os 4 Grafos Criados

1. **Grafo de Comentários**: Apenas comentários em issues/PRs (peso 2)
2. **Grafo de Issues**: Apenas issues fechadas por outros usuários (peso 3)
3. **Grafo de Reviews**: Reviews, approvals, merges (pesos 4-5)
4. **Grafo Integrado**: Todos os tipos combinados com pesos acumulados

## 📊 Métricas Implementadas

### Centralidade (Importância)

- **Degree Centrality**: Número de conexões diretas
- **Betweenness Centrality**: Quem são as "pontes" entre grupos
- **Closeness Centrality**: Quem está mais próximo de todos
- **PageRank**: Influência (como Google ordena páginas)

### Estrutura

- **Densidade**: Proporção de conexões existentes vs possíveis
- **Clustering Coefficient**: Tendência de formar "clusters"
- **Assortatividade**: Se pessoas conectadas têm características semelhantes

### Comunidades

- **Detecção de Comunidades**: Identifica grupos naturais
- **Bridging Ties**: Quem conecta diferentes comunidades

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=codigos --cov-report=html

# Teste específico
pytest tests/unit/test_edge.py -v
```

## 📁 Estrutura Completa

```
projeto-grafos/
├── codigos/                    # Código-fonte principal
│   ├── app/                    # Interface CLI
│   ├── core/graph/             # Implementação de grafos
│   ├── models/                 # Modelos de domínio
│   ├── github_miner/           # Coleta de dados
│   ├── services/               # Orquestração
│   ├── metrics/                # Cálculo de métricas
│   ├── exporters/              # Exportação
│   ├── exceptions/             # Exceções
│   └── utils/                  # Utilidades
├── tests/                      # Testes unitários
│   ├── unit/
│   └── integration/
├── docs/                       # Documentação
├── requirements.txt            # Dependências
├── .env.example               # Template de configuração
├── README.md                  # Este arquivo
├── CLAUDE.md                  # Guia para Claude Code
└── PLANO_ARQUITETURA.md       # Plano arquitetural
```

## 🔑 Decisões Arquiteturais

### 1. Sem NetworkX
Implementamos grafos manualmente para:
- Aprendizado profundo dos conceitos
- Controle total sobre o algoritmo
- Conformidade com requisitos acadêmicos

### 2. Duas Implementações de Grafo
- **AdjacencyListGraph**: Mais eficiente para grafos esparsos
- **AdjacencyMatrixGraph**: Mais visual, melhor para entender

### 3. Separação de Responsabilidades
Cada módulo tem uma única responsabilidade:
- `github_miner`: APENAS buscar e parsear dados
- `graph_builder`: APENAS transformar dados em arestas
- `metrics`: APENAS calcular análises

## 🎓 Para Apresentação

O código é estruturado para facilitar explicação:
1. Classes com responsabilidade única
2. Nomes claros e intuitivos
3. Documentação extensiva
4. Exemplos de uso em docstrings

## 📝 Documentação Adicional

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detalhes arquiteturais
- [API_REFERENCE.md](docs/API_REFERENCE.md) - Referência da API
- [METRICS.md](docs/METRICS_EXPLAINED.md) - Explicação das métricas
- [CLAUDE.md](CLAUDE.md) - Guia para Claude Code

## 🛠️ Desenvolvimento

### Adicionar Nova Métrica

1. Criar arquivo em `metrics/` (ex: `new_metric.py`)
2. Implementar função que recebe grafo e retorna resultados
3. Adicionar testes em `tests/unit/`
4. Documentar em docstring e `METRICS.md`

### Adicionar Novo Exporter

1. Estender `ExporterBase` em `exporters/`
2. Implementar método `export(graph, output_path)`
3. Adicionar testes

## 📊 Exemplo de Uso

```python
from codigos.core import Edge, AbstractGraph
from codigos.github_miner import GithubClient
from codigos.services import GraphBuilderService
from codigos.metrics import calculate_degree_centrality

# 1. Buscar dados
client = GithubClient(token="seu_token")
issues = client.get_issues("devlikeapro", "waha")
prs = client.get_pull_requests("devlikeapro", "waha")

# 2. Construir grafo
builder = GraphBuilderService()
graph = builder.build_integrated_graph(issues, prs)

# 3. Calcular métricas
centrality = calculate_degree_centrality(graph)

# 4. Exportar
graph.export_to_gephi("output/collaboration_graph", format="gexf")
```

## ⚙️ Requisitos

- Python 3.8+
- requests (para API do GitHub)
- python-dotenv (para variáveis de ambiente)
- pytest (para testes)

## 📄 Licença

Projeto acadêmico - PUC Minas 2026/1

## 👥 Equipe

- Desenvolvido como trabalho prático de Teoria dos Grafos
- Disciplina: Engenharia de Software
- Professor: Leonardo V. Cardoso

---

**Nota**: Este projeto prioriza **clareza e aprendizado** sobre performance. O código é desenvolvido para ser facilmente explicável em apresentação acadêmica.
