"""
Aplicação principal (CLI) para análise de colaboração em GitHub.

Orquestra todo o pipeline:
1. Mineração de dados do GitHub
2. Construção de grafos de colaboração
3. Cálculo de métricas
4. Exportação em múltiplos formatos
"""

import argparse
import sys
from datetime import datetime

from ..github_miner import GithubClient, DataTransformer, RateLimiter
from ..services import GraphBuilderService, MetricsService
from ..exporters import CSVExporter, GEXFExporter, GraphMLExporter
from ..exceptions.mining_exceptions import GithubMiningError


def setup_argument_parser() -> argparse.ArgumentParser:
    """Configura parser de argumentos de linha de comando.

    Returns:
        ArgumentParser configurado
    """
    parser = argparse.ArgumentParser(
        description="Análise de Colaboração em Repositórios GitHub usando Grafos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python -m codigos.app.main --owner pytorch --repo pytorch --token <token>
  python -m codigos.app.main --owner torvalds --repo linux --token <token> --format csv,gexf
  python -m codigos.app.main --owner microsoft --repo vscode --token <token> --output ./results
        """,
    )

    parser.add_argument(
        '--owner',
        type=str,
        required=True,
        help='Dono do repositório GitHub (ex: pytorch)',
    )

    parser.add_argument(
        '--repo',
        type=str,
        required=True,
        help='Nome do repositório (ex: pytorch)',
    )

    parser.add_argument(
        '--token',
        type=str,
        required=True,
        help='Token de autenticação GitHub (Personal Access Token)',
    )

    parser.add_argument(
        '--output',
        type=str,
        default='./results',
        help='Diretório de saída para arquivos exportados (padrão: ./results)',
    )

    parser.add_argument(
        '--format',
        type=str,
        default='csv,gexf,graphml',
        help='Formatos de exportação: csv, gexf, graphml (padrão: todos)',
    )

    parser.add_argument(
        '--impl',
        type=str,
        default='list',
        choices=['list', 'matrix'],
        help='Implementação de grafo: list (esparso) ou matrix (denso, padrão: list)',
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verbose (saída detalhada)',
    )

    return parser


def log(message: str, verbose: bool = False) -> None:
    """Imprime mensagem no console.

    Args:
        message: Mensagem a imprimir
        verbose: Se True, apenas imprime se verbose mode ativado
    """
    if verbose:
        print(message)


def main(args=None) -> int:
    """Função principal da aplicação.

    Args:
        args: Argumentos de linha de comando (para testes)

    Returns:
        Código de saída (0 = sucesso, 1 = erro)
    """
    try:
        parser = setup_argument_parser()
        parsed_args = parser.parse_args(args)

        owner = parsed_args.owner
        repo = parsed_args.repo
        token = parsed_args.token
        output_dir = parsed_args.output
        formats = [f.strip() for f in parsed_args.format.split(',')]
        use_list = parsed_args.impl == 'list'
        verbose = parsed_args.verbose

        print(f"\n{'='*70}")
        print(f"  Análise de Colaboração: {owner}/{repo}")
        print(f"{'='*70}\n")

        # 1. Mineração de dados
        print("[1/4] Minerando dados do GitHub...")
        client = GithubClient(token=token)
        transformer = DataTransformer(client)

        try:
            collab_graph = transformer.mine_repository(owner, repo)
            print(f"  ✓ {collab_graph.user_count} usuários encontrados")
            print(f"  ✓ {collab_graph.interaction_count} interações mineradas")
        except Exception as e:
            print(f"  ✗ Erro ao minerar: {e}")
            return 1
        finally:
            client.close()

        # 2. Construção de grafos
        print("\n[2/4] Construindo grafos de colaboração...")
        builder = GraphBuilderService(use_adjacency_list=use_list)

        try:
            graphs = builder.build_all_pdf_graphs(collab_graph)
            for name, graph in graphs.items():
                stats = GraphBuilderService.get_graph_statistics(graph)
                print(f"  ✓ {name}: {stats['vertices']} vértices, "
                      f"{stats['edges']} arestas, "
                      f"densidade={stats['density']:.3f}")
        except Exception as e:
            print(f"  ✗ Erro ao construir grafos: {e}")
            return 1

        # 3. Cálculo de métricas
        print("\n[3/4] Calculando métricas de rede...")
        try:
            metrics_service = MetricsService(graphs['integrated'], collab_graph.users)
            all_metrics = metrics_service.calculate_all_metrics()

            summary = metrics_service.get_metrics_summary()
            print(f"  ✓ 9 métricas calculadas para {len(all_metrics)} usuários")
            print(f"  ✓ PageRank médio: {summary['avg_pagerank']:.4f}")
            print(f"  ✓ Degree centrality média: {summary['avg_degree_centrality']:.4f}")

            # Top 5 por PageRank
            top_pagerank = metrics_service.get_top_by_metric('pagerank', top_n=5)
            print("\n  Top 5 colaboradores (by PageRank):")
            for i, (user, value) in enumerate(top_pagerank, 1):
                print(f"    {i}. {user.login}: {value:.4f}")

        except Exception as e:
            print(f"  ✗ Erro ao calcular métricas: {e}")
            return 1

        # 4. Exportação
        print(f"\n[4/4] Exportando em {len(formats)} formato(s)...")

        import os
        os.makedirs(output_dir, exist_ok=True)

        exported_files = []

        # Mapeamento dos 4 grafos exigidos pelo PDF
        graph_names = {
            'comments': 'comments',
            'issue_close': 'issue_close',
            'reviews_merges': 'reviews_merges',
            'integrated': 'total',
        }

        try:
            for graph_key, suffix in graph_names.items():
                g = graphs[graph_key]
                base = os.path.join(output_dir, f"{owner}_{repo}_{suffix}")

                # Métricas: usamos all_metrics apenas para o grafo integrado;
                # para os outros criamos métricas simples baseadas no mesmo usuário.
                g_metrics = all_metrics

                if 'csv' in formats:
                    csv_exporter = CSVExporter(g, g_metrics)
                    csv_exporter.export(base)
                    print(f"  ✓ CSV ({suffix}): {base}_*.csv")
                    exported_files.extend([f"{base}_nodes.csv", f"{base}_edges.csv"])

                if 'gexf' in formats:
                    gexf_path = f"{base}.gexf"
                    gexf_exporter = GEXFExporter(g, g_metrics)
                    gexf_exporter.export(gexf_path)
                    print(f"  ✓ GEXF ({suffix}): {gexf_path}")
                    exported_files.append(gexf_path)

                if 'graphml' in formats:
                    graphml_path = f"{base}.graphml"
                    graphml_exporter = GraphMLExporter(g, g_metrics)
                    graphml_exporter.export(graphml_path)
                    print(f"  ✓ GraphML ({suffix}): {graphml_path}")
                    exported_files.append(graphml_path)

        except Exception as e:
            print(f"  ✗ Erro ao exportar: {e}")
            return 1

        # Resumo final
        print(f"\n{'='*70}")
        print(f"  ✓ Análise concluída com sucesso!")
        print(f"  Arquivos gerados: {len(exported_files)}")
        print(f"  Diretório: {output_dir}")
        print(f"{'='*70}\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
        return 130
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        if parsed_args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
