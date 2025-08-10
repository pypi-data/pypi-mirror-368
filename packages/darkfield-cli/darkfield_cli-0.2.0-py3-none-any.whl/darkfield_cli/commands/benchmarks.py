import click
from ..api_client import DarkfieldClient


@click.group(help="Run and manage internal benchmarks")
def benchmarks():
    pass


@benchmarks.command("run")
@click.option("--model", "models", multiple=True, help="Model(s) to benchmark", required=True)
@click.option("--trait", "traits", multiple=True, help="Trait(s) to evaluate", required=True)
@click.option("--dataset", "datasets", multiple=True, default=["truthfulqa", "advbench"], help="Datasets")
@click.option("--coeffs", default="0.0,0.5,1.0,1.5,2.0", help="Comma-separated coefficients")
def run_benchmarks(models, traits, datasets, coeffs):
    api = DarkfieldClient()
    coefficients = [float(x.strip()) for x in coeffs.split(',') if x.strip()]
    payload = { 'models': list(models), 'traits': list(traits), 'datasets': list(datasets), 'coefficients': coefficients }
    resp = api.post('/api/v1/benchmarks/run', json=payload)
    click.echo(resp)


@benchmarks.command("list")
@click.option('--model', default='', help='Filter by model')
@click.option('--trait', default='', help='Filter by trait')
@click.option('--dataset', default='', help='Filter by dataset')
@click.option('--page', default=0, type=int, help='Page (0-based)')
def list_benchmarks(model, trait, dataset, page):
    api = DarkfieldClient()
    qs = []
    qs.append(f"limit=20&offset={page*20}")
    if model: qs.append(f"model={model}")
    if trait: qs.append(f"trait={trait}")
    if dataset: qs.append(f"dataset={dataset}")
    rows = api.get(f"/api/v1/benchmarks/runs?{'&'.join(qs)}")
    for r in rows:
        click.echo(f"{r['id']} {r['status']} models={r['models']} traits={r['traits']} {r['created_at']}")


@benchmarks.command("show")
@click.argument('run_id')
def show_benchmark(run_id):
    api = DarkfieldClient()
    r = api.get(f'/api/v1/benchmarks/runs/{run_id}')
    click.echo(r)


@benchmarks.command("export")
@click.argument('run_id')
@click.option('--format', 'fmt', default='json', type=click.Choice(['json','csv']))
def export_benchmark(run_id, fmt):
    api = DarkfieldClient()
    res = api.get(f'/api/v1/benchmarks/runs/{run_id}/export?format={fmt}')
    if fmt == 'json':
        import json
        click.echo(json.dumps(res, indent=2))
    else:
        fname = res.get('filename') or f'benchmark_{run_id}.csv'
        content = res.get('content') or ''
        with open(fname, 'w') as f:
            f.write(content)
        click.echo(f"Saved to {fname}")
