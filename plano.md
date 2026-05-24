# Projeto — Análise de Colaboração em Repositórios GitHub Utilizando Grafos

## Objetivo

Desenvolver uma ferramenta computacional capaz de:

- minerar dados de um repositório do GitHub;
- transformar interações entre colaboradores em grafos direcionados;
- aplicar métricas de teoria dos grafos e redes complexas;
- exportar os resultados para visualização no Gephi.

---

# Pipeline Geral da Aplicação

```text
1. GitHub REST API / GraphQL API
        ↓
2. Coleta das interações
        ↓
3. Transformação das interações em arestas
        ↓
4. Construção dos grafos
        ↓
5. Aplicação de métricas e algoritmos
        ↓
6. Exportação para Gephi
        ↓
7. Geração das análises
```

---

# Arquitetura do Projeto

## Estrutura de Pastas

```text
src/
├── model/
├── graph/
├── api/
├── service/
├── metrics/
├── export/
├── app/
└── tests/
```

---

# Responsabilidade de Cada Camada

| Camada | Responsabilidade |
|---|---|
| `model` | Entidades e objetos do domínio |
| `graph` | Implementação das estruturas de grafos |
| `api` | Comunicação com a API do GitHub |
| `service` | Regras de negócio e construção dos grafos |
| `metrics` | Algoritmos e métricas de redes |
| `export` | Exportação para Gephi |
| `app` | Aplicação principal / demonstração |
| `tests` | Testes unitários |

---

# Modelagem do Sistema

## Classe `User`

Representa um colaborador do repositório.

```java
public class User {

    private int id;
    private String login;

}
```

---

## Enum `InteractionType`

Define os tipos de interação possíveis.

```java
public enum InteractionType {

    ISSUE_COMMENT,
    ISSUE_CLOSE,
    PR_COMMENT,
    PR_REVIEW,
    PR_APPROVAL,
    PR_MERGE

}
```

---

## Classe `Interaction`

Representa uma interação entre dois usuários.

```java
public class Interaction {

    private User source;
    private User target;

    private InteractionType type;

    private double weight;

}
```

---

# Estrutura de Grafos

## Classe `Edge`

Representa uma aresta do grafo.

```java
public class Edge {

    private int destination;
    private double weight;

}
```

---

# Classe Abstrata `AbstractGraph`

Classe responsável por:

- definir a API comum;
- centralizar validações;
- armazenar atributos compartilhados.

## Atributos principais

```java
protected int vertexCount;
protected int edgeCount;

protected double[] vertexWeights;
protected String[] labels;
```

---

## Métodos auxiliares

### `validateVertex(int v)`

Responsável por verificar se um vértice é válido.

```java
protected void validateVertex(int v)
```

### Validação

```java
if (v < 0 || v >= vertexCount)
```

Deve lançar:

```java
IllegalArgumentException
```

---

# Implementações do Grafo

## `AdjacencyMatrixGraph`

Implementa o grafo utilizando matriz de adjacência.

```java
double[][] matrix;
```

### Exemplo

```text
    0 1 2
0 [ 0 1 0 ]
1 [ 0 0 1 ]
2 [ 1 0 0 ]
```

### Interpretação

```text
matrix[0][1] = 1
```

Representa:

```text
0 → 1
```

---

## `AdjacencyListGraph`

Implementa o grafo utilizando listas de adjacência.

```java
Map<Integer, List<Edge>>
```

### Exemplo

```text
0 → [1,2]
1 → [3]
2 → []
```

---

# Métodos Obrigatórios da API

## `getVertexCount()`

Retorna a quantidade total de vértices.

```java
int getVertexCount();
```

---

## `getEdgeCount()`

Retorna a quantidade total de arestas.

```java
int getEdgeCount();
```

---

## `hasEdge(int u, int v)`

Verifica se existe uma aresta entre `u` e `v`.

```java
boolean hasEdge(int u, int v);
```

---

## `addEdge(int u, int v)`

Adiciona uma aresta direcionada:

```text
u → v
```

```java
void addEdge(int u, int v);
```

---

# Restrições Importantes

## Grafos Simples

O sistema NÃO deve permitir:

### Laços

```text
0 → 0
```

### Múltiplas arestas

```text
0 → 1
0 → 1
```

---

# Idempotência

O método:

```java
addEdge(0,1)
```

não deve duplicar arestas caso seja chamado múltiplas vezes.

### Verificações necessárias

```java
if (u == v)
```

```java
if (hasEdge(u,v))
```

---

## `removeEdge(int u, int v)`

Remove a aresta entre `u` e `v`.

```java
void removeEdge(int u, int v);
```

---

## `isSuccessor(int u, int v)`

Verifica se `v` é sucessor de `u`.

```text
u → v
```

---

## `isPredecessor(int u, int v)`

Verifica se `v` aponta para `u`.

```text
v → u
```

---

## `isIncident(int u, int v, int x)`

Verifica se o vértice `x` participa da aresta `u → v`.

### Exemplo

```text
2 → 5
```

Então:

```java
isIncident(2,5,2) == true
isIncident(2,5,5) == true
```

---

## `getVertexInDegree(int u)`

Retorna a quantidade de arestas entrando no vértice.

### Exemplo

```text
1 → 3
2 → 3
5 → 3
```

Resultado:

```text
3
```

---

## `getVertexOutDegree(int u)`

Retorna a quantidade de arestas saindo do vértice.

---

## `setEdgeWeight(int u, int v, double w)`

Define o peso de uma aresta.

### Exemplo do projeto

```text
Comentário = 2
Review = 4
Merge = 5
```

---

## `getEdgeWeight(int u, int v)`

Retorna o peso da aresta.

---

# Verificação de Conectividade

## `isConnected()`

Verifica se todos os vértices são alcançáveis.

---

# Implementação Recomendada

Utilizar:

- DFS (Depth First Search)
ou
- BFS (Breadth First Search)

---

# Exemplo de Grafo Conectado

```text
0 → 1 → 2
```

---

# Exemplo de Grafo Não Conectado

```text
0 → 1

2 isolado
```

---

# Passos da DFS

```text
1. Escolher vértice inicial
2. Marcar como visitado
3. Percorrer vizinhos
4. Repetir recursivamente
```

Se todos forem visitados:

```text
grafo conectado
```

---

# `isCompleteGraph()`

Verifica se todos os vértices possuem conexão entre si.

---

# Exportação para Gephi

## Objetivo

Exportar os grafos para visualização no Gephi.

---

# Melhor Formato

CSV.

---

## `nodes.csv`

```csv
id,label
0,davi
1,maria
```

---

## `edges.csv`

```csv
source,target,weight
0,1,5
```

---

# Integração com GitHub

## Classe `GithubApiClient`

Responsável exclusivamente por:

- buscar dados;
- consumir endpoints;
- converter JSON.

---

# Métodos Esperados

```java
getIssues()
getPullRequests()
getReviews()
getComments()
```

---

# Classe Mais Importante do Sistema

## `GraphBuilderService`

Responsável por transformar:

```text
dados GitHub
```

em:

```text
arestas do grafo
```

---

# Exemplo

```text
Carlos aprovou PR da Ana
```

Transformação:

```text
Carlos → Ana
peso = 4
```

---

# Construção do Grafo Integrado

Arestas podem acumular pesos.

### Exemplo

```text
João comentou
+
João revisou
+
João fez merge
```

Peso final:

```text
2 + 4 + 5 = 11
```

---

# Métricas e Algoritmos

## Degree Centrality

Quantidade de conexões de um colaborador.

---

## Betweenness Centrality

Identifica usuários que conectam diferentes grupos.

---

## Closeness Centrality

Mede proximidade entre colaboradores.

---

## PageRank

Mede influência considerando a importância das conexões.

---

# Fluxo Final da Aplicação

```text
GithubApiClient
        ↓
GraphBuilderService
        ↓
AdjacencyListGraph
        ↓
MetricsService
        ↓
GephiExporter
```

---

# Ordem Recomendada de Desenvolvimento

## Etapa 1

- Edge
- AbstractGraph

---

## Etapa 2

- AdjacencyListGraph
- Testes unitários

---

## Etapa 3

- AdjacencyMatrixGraph
- DFS/BFS

---

## Etapa 4

- GithubApiClient
- GraphBuilderService

---

## Etapa 5

- Métricas
- Exportação Gephi

---

# Conclusão

O objetivo principal do projeto não é apenas coletar dados do GitHub, mas:

```text
modelar relações de colaboração como grafos
```

e aplicar algoritmos e métricas para compreender:

- influência;
- colaboração;
- conectividade;
- comunidades;
- comportamento social dentro do projeto.