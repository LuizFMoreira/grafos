"""
Sistema de Análise de Colaboração em Repositórios GitHub usando Grafos.

Este projeto implementa uma ferramenta completa para analisar padrões de
colaboração em repositórios GitHub, modelando interações como grafos
direcionados ponderados.

Módulos principais:
- core: Estruturas de grafos (Edge, AbstractGraph, implementações concretas)
- models: Modelos de domínio (User, Interaction, etc)
- github_miner: Coleta de dados do GitHub
- services: Orquestração de processos
- metrics: Cálculo de métricas de redes
- exporters: Exportação para visualização (Gephi)
- exceptions: Exceções customizadas
- utils: Utilidades gerais

Autores: Engenharia de Software - PUC Minas
Versão: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Engenharia de Software - PUC Minas"
