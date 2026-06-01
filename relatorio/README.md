# Relatório (LaTeX)

Esqueleto do relatório técnico exigido pela Etapa 3 do TP. Use o template oficial da SBC para a entrega final.

## Como compilar

### Opção 1 — agora (sem template SBC)
Compila como `article` padrão (suficiente para iterar texto e figuras):

```powershell
cd relatorio
pdflatex -interaction=nonstopmode relatorio.tex
pdflatex -interaction=nonstopmode relatorio.tex   # 2x p/ resolver referências
```

### Opção 2 — versão final com template SBC

1. Abra https://www.overleaf.com/latex/templates/sbc-conferences-template
2. Baixe `sbc-template.cls` e `sbc.bst` e copie para esta pasta `relatorio/`.
3. No arquivo `relatorio.tex`, troque:

   ```latex
   \documentclass[a4paper,11pt]{article}
   ```

   por:

   ```latex
   \documentclass[12pt]{sbc-template}
   ```

   e remova `geometry`, `inputenc`, `fontenc`, `babel` (já vêm no `sbc-template`).
4. Recompile.

## Estrutura prevista

| Seção                              | O que preencher                                    |
|------------------------------------|----------------------------------------------------|
| Introdução                         | Motivação + escolha do repositório (>5k ⭐)        |
| Modelagem                          | 4 grafos + tabela de pesos                         |
| Arquitetura                        | Diagrama de classes + restrições atendidas         |
| Coleta de dados                    | Fluxo do miner + volumetria                        |
| Métricas                           | Fórmulas e justificativa                           |
| Resultados                         | Tabelas/screenshots gerados pela ferramenta        |
| Responsabilidades dos integrantes  | (Exigência explícita do enunciado)                 |
| Conclusão                          | Insights + limitações + trabalhos futuros          |

Faixa de páginas obrigatória: **7 a 15**.

Coloque imagens em `relatorio/figuras/`.
