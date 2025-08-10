"""
Direct vector extraction commands for darkfield CLI
Quick extraction without full pipeline
"""

import click
import json
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
import numpy as np

console = Console()

@click.group()
def extract():
    """Extract persona vectors from text"""
    pass

@extract.command()
@click.argument('text')
@click.option('--trait', default='helpfulness', help='Trait to extract')
@click.option('--persona', type=str, help='Persona name or file to compose steering')
@click.option('--model', default='llama-3', help='Model to use')
@click.option('--layer', type=int, help='Specific layer to use')
@click.option('--output', type=click.Path(), help='Save vector to file')
def vector(text, trait, persona, model, layer, output):
    """Extract a single persona vector from text"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    console.print(f"\n[cyan]Extracting {('persona' if persona else trait)} vector from text[/cyan]")
    console.print(f"Model: {model}")
    if layer:
        console.print(f"Layer: {layer}")
    
    # If persona specified, compose its vector and return stats; otherwise extract trait vector from text
    if persona:
        try:
            from ..utils.persona_manager import load_persona, compose_persona_vector, apply_envelope_to_prompt
            pdata = load_persona(persona)
            comp = compose_persona_vector(pdata, client=client, model=model)
            vector_data = {
                "vector": comp.vector,
                "dimension": comp.dimension,
                "norm": np.linalg.norm(np.array(comp.vector)),
                "metadata": {"composed_from": list((pdata.get('traits') or {}).keys())},
            }
        except Exception as e:
            console.print(f"[red]Failed to compose persona vector: {e}[/red]")
            raise click.Abort()
    else:
        response = client.post("/api/v1/vector-extraction/extract", json={
            "text": text,
            "model_name": model,
            "trait_types": [trait],
            "layer": layer,
        })
        
        vector_data = response["vectors"][trait]
    
    # Display results
    console.print(f"\n[green]✓[/green] Vector extracted successfully!")
    console.print(f"Dimension: {vector_data['dimension']}")
    console.print(f"Norm: {vector_data['norm']:.4f}")
    
    # Show vector preview
    vector_array = np.array(vector_data['vector'])
    console.print(f"\n[bold]Vector preview (first 10 dimensions):[/bold]")
    console.print(f"{vector_array[:10]}")
    
    # Show statistics
    console.print(f"\n[bold]Statistics:[/bold]")
    console.print(f"Mean: {np.mean(vector_array):.6f}")
    console.print(f"Std: {np.std(vector_array):.6f}")
    console.print(f"Min: {np.min(vector_array):.6f}")
    console.print(f"Max: {np.max(vector_array):.6f}")
    
    # Save if requested
    if output:
        with open(output, 'w') as f:
            json.dump(vector_data, f, indent=2)
        console.print(f"\n[green]✓[/green] Vector saved to {output}")
    
    # Track usage
    client.track_usage("vector_extraction", 1)
    
    return vector_data

@extract.command()
@click.argument('file1', type=click.Path(exists=True))
@click.argument('file2', type=click.Path(exists=True))
@click.option('--trait', default='helpfulness', help='Trait being compared')
@click.option('--threshold', default=0.8, type=float, help='Similarity threshold')
def compare(file1, file2, trait, threshold):
    """Compare two persona vectors"""
    # Load vectors
    with open(file1, 'r') as f:
        vector1 = json.load(f)
    with open(file2, 'r') as f:
        vector2 = json.load(f)
    
    # Convert to numpy arrays
    v1 = np.array(vector1['vector'])
    v2 = np.array(vector2['vector'])
    
    # Compute similarity metrics
    cosine_sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    euclidean_dist = np.linalg.norm(v1 - v2)
    
    # Display comparison
    console.print(f"\n[bold]Vector Comparison for {trait}[/bold]\n")
    
    table = Table(show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Vector 1", justify="center")
    table.add_column("Vector 2", justify="center")
    
    table.add_row("Source", file1.split('/')[-1], file2.split('/')[-1])
    table.add_row("Dimension", str(vector1['dimension']), str(vector2['dimension']))
    table.add_row("Norm", f"{vector1['norm']:.4f}", f"{vector2['norm']:.4f}")
    
    console.print(table)
    
    # Similarity results
    sim_color = "green" if cosine_sim > threshold else "yellow" if cosine_sim > 0.5 else "red"
    console.print(f"\n[bold]Similarity Metrics:[/bold]")
    console.print(f"Cosine Similarity: [{sim_color}]{cosine_sim:.4f}[/{sim_color}]")
    console.print(f"Euclidean Distance: {euclidean_dist:.4f}")
    
    # Interpretation
    if cosine_sim > threshold:
        console.print(f"\n[green]✓ Vectors are highly similar (>{threshold:.1f})[/green]")
        console.print("These texts likely express the same trait similarly")
    elif cosine_sim > 0.5:
        console.print(f"\n[yellow]⚠ Vectors are moderately similar[/yellow]")
        console.print("These texts show some trait alignment")
    else:
        console.print(f"\n[red]✗ Vectors are dissimilar[/red]")
        console.print("These texts express the trait differently")

@extract.command()
@click.argument('texts', nargs=-1, required=True)
@click.option('--trait', default='helpfulness', help='Trait to extract')
@click.option('--model', default='llama-3', help='Model to use')
@click.option('--output', type=click.Path(), help='Save results to file')
def batch(texts, trait, model, output):
    """Extract vectors from multiple texts"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    console.print(f"\n[cyan]Batch extracting {trait} vectors[/cyan]")
    console.print(f"Processing {len(texts)} texts with model: {model}")
    
    results = []
    
    # Process each text
    with console.status(f"Extracting vectors...") as status:
        for i, text in enumerate(texts):
            status.update(f"Processing text {i+1}/{len(texts)}...")
            
            response = client.post("/api/v1/vector-extraction/extract", json={
                "text": text,
                "model_name": model,
                "trait_types": [trait],
            })
            
            vector_data = response["vectors"][trait]
            vector_data["text"] = text[:50] + "..." if len(text) > 50 else text
            results.append(vector_data)
    
    # Display results table
    table = Table(title=f"Batch Extraction Results - {trait}", show_header=True)
    table.add_column("#", style="cyan", justify="center")
    table.add_column("Text Preview", width=40)
    table.add_column("Norm", justify="center")
    table.add_column("Dimension", justify="center")
    
    for i, result in enumerate(results):
        table.add_row(
            str(i+1),
            result["text"],
            f"{result['norm']:.4f}",
            str(result['dimension'])
        )
    
    console.print("\n")
    console.print(table)
    
    # Compute average vector
    vectors = [np.array(r['vector']) for r in results]
    avg_vector = np.mean(vectors, axis=0)
    
    console.print(f"\n[bold]Average Vector Statistics:[/bold]")
    console.print(f"Norm: {np.linalg.norm(avg_vector):.4f}")
    console.print(f"Mean: {np.mean(avg_vector):.6f}")
    console.print(f"Std across texts: {np.std([r['norm'] for r in results]):.4f}")
    
    # Save if requested
    if output:
        output_data = {
            "trait": trait,
            "model": model,
            "results": results,
            "average_vector": avg_vector.tolist(),
            "statistics": {
                "avg_norm": float(np.linalg.norm(avg_vector)),
                "std_norm": float(np.std([r['norm'] for r in results])),
                "min_norm": float(min(r['norm'] for r in results)),
                "max_norm": float(max(r['norm'] for r in results)),
            }
        }
        
        with open(output, 'w') as f:
            json.dump(output_data, f, indent=2)
        console.print(f"\n[green]✓[/green] Results saved to {output}")
    
    # Track usage
    client.track_usage("vector_extraction", len(texts))

@extract.command()
@click.option('--trait', required=True, help='Trait to visualize')
@click.option('--model', default='llama-3', help='Model to use')
@click.option('--samples', default=100, type=int, help='Number of samples to analyze')
def visualize(trait, model, samples):
    """Visualize trait vector space (requires matplotlib)"""
    from ..api_client import DarkfieldClient
    
    try:
        import matplotlib.pyplot as plt
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
    except ImportError:
        console.print("[red]This command requires matplotlib and scikit-learn[/red]")
        console.print("Install with: pip install matplotlib scikit-learn")
        return
    
    client = DarkfieldClient()
    
    console.print(f"\n[cyan]Generating vector space visualization for {trait}[/cyan]")
    
    # Generate sample texts
    with console.status("Generating sample texts..."):
        dataset_response = client.post("/api/v1/generation/generate", json={
            "trait": trait,
            "n_instruction_pairs": samples // 2,
        })
        dataset = dataset_response["dataset"]
    
    # Extract vectors
    vectors = []
    labels = []
    
    with console.status(f"Extracting vectors from {samples} samples..."):
        # Positive examples
        for pair in dataset['instruction_pairs'][:samples//2]:
            response = client.post("/api/v1/vector-extraction/extract", json={
                "text": pair['pos'],
                "model_name": model,
                "trait_types": [trait],
            })
            vectors.append(response["vectors"][trait]["vector"])
            labels.append(1)  # Positive
        
        # Negative examples
        for pair in dataset['instruction_pairs'][:samples//2]:
            response = client.post("/api/v1/vector-extraction/extract", json={
                "text": pair['neg'],
                "model_name": model,
                "trait_types": [trait],
            })
            vectors.append(response["vectors"][trait]["vector"])
            labels.append(0)  # Negative
    
    # Convert to numpy
    X = np.array(vectors)
    y = np.array(labels)
    
    # Dimensionality reduction
    console.print("Performing dimensionality reduction...")
    
    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    
    # t-SNE
    tsne = TSNE(n_components=2, random_state=42)
    X_tsne = tsne.fit_transform(X)
    
    # Create visualizations
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # PCA plot
    scatter1 = ax1.scatter(X_pca[y==1, 0], X_pca[y==1, 1], 
                          c='red', label=f'High {trait}', alpha=0.6)
    scatter2 = ax1.scatter(X_pca[y==0, 0], X_pca[y==0, 1], 
                          c='blue', label=f'Low {trait}', alpha=0.6)
    ax1.set_title(f'PCA Visualization of {trait} Vectors')
    ax1.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
    ax1.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # t-SNE plot
    scatter3 = ax2.scatter(X_tsne[y==1, 0], X_tsne[y==1, 1], 
                          c='red', label=f'High {trait}', alpha=0.6)
    scatter4 = ax2.scatter(X_tsne[y==0, 0], X_tsne[y==0, 1], 
                          c='blue', label=f'Low {trait}', alpha=0.6)
    ax2.set_title(f't-SNE Visualization of {trait} Vectors')
    ax2.set_xlabel('t-SNE 1')
    ax2.set_ylabel('t-SNE 2')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(f'Vector Space Visualization: {trait} ({model})', fontsize=16)
    plt.tight_layout()
    
    # Save plot
    plot_file = f"{trait}_{model}_vectors.png"
    plt.savefig(plot_file, dpi=150)
    console.print(f"\n[green]✓[/green] Visualization saved to {plot_file}")
    
    # Show statistics
    console.print(f"\n[bold]Clustering Statistics:[/bold]")
    
    # Calculate centroid distance
    pos_centroid = X[y==1].mean(axis=0)
    neg_centroid = X[y==0].mean(axis=0)
    centroid_dist = np.linalg.norm(pos_centroid - neg_centroid)
    
    console.print(f"Centroid distance: {centroid_dist:.4f}")
    console.print(f"Explained variance (PCA): {sum(pca.explained_variance_ratio_):.1%}")
    
    # Track usage
    client.track_usage("vector_extraction", samples)
    
    plt.show()

@extract.command()
@click.option('--trait', required=True, help='Trait name')
@click.option('--vector-file', type=click.Path(exists=True), help='Pre-computed vector file')
@click.option('--description', help='Natural language trait description')
@click.option('--model', default='llama-3', help='Model to use')
def reference(trait, vector_file, description, model):
    """Create or update a reference vector for a trait"""
    from ..api_client import DarkfieldClient
    
    client = DarkfieldClient()
    
    if vector_file:
        # Use provided vector
        with open(vector_file, 'r') as f:
            vector_data = json.load(f)
        vector = vector_data['vector']
        
        console.print(f"[cyan]Creating reference vector for {trait} from file[/cyan]")
    else:
        # Generate reference vector from description
        if not description:
            console.print("[red]Please provide either --vector-file or --description[/red]")
            return
        
        console.print(f"[cyan]Generating reference vector for {trait}[/cyan]")
        console.print(f"Description: {description}")
        
        # Generate dataset and extract vector
        with console.status("Generating trait dataset..."):
            dataset_response = client.post("/dataset-generation/generate", json={
                "trait": trait,
                "trait_description": description,
                "n_instruction_pairs": 50,
            })
            dataset = dataset_response["dataset"]
        
        # Extract vectors from examples
        vectors = []
        with console.status("Extracting vectors..."):
            for pair in dataset['instruction_pairs'][:20]:
                pos_response = client.post("/vector-extraction/extract", json={
                    "text": pair['pos'],
                    "model_name": model,
                    "trait_types": [trait],
                })
                neg_response = client.post("/vector-extraction/extract", json={
                    "text": pair['neg'],
                    "model_name": model,
                    "trait_types": [trait],
                })
                
                vectors.append({
                    "positive": pos_response["vectors"][trait]["vector"],
                    "negative": neg_response["vectors"][trait]["vector"],
                })
        
        # Compute CAA vector
        caa_response = client.post("/api/v1/vector-extraction/compute-caa", json={
            "vectors": vectors,
            "trait": trait,
            "model_name": model,
        })
        
        vector = caa_response["caa_vector"]["vector"]
    
    # Save as reference vector
    response = client.post("/api/v1/vectors/reference", json={
        "trait": trait,
        "vector": vector,
        "model": model,
        "description": description,
    })
    
    console.print(f"\n[green]✓[/green] Reference vector created for {trait}")
    console.print(f"ID: {response['reference_id']}")
    console.print(f"Norm: {response['norm']:.4f}")
    console.print(f"Dimension: {response['dimension']}")
    
    # Test the reference vector
    console.print("\n[bold]Testing reference vector:[/bold]")
    
    test_texts = [
        f"I always try to be {trait}",
        f"I never want to be {trait}",
        "This is a neutral statement",
    ]
    
    table = Table(show_header=True)
    table.add_column("Test Text", width=40)
    table.add_column("Similarity Score", justify="center")
    
    for text in test_texts:
        test_response = client.post("/api/v1/vector-extraction/extract", json={
            "text": text,
            "model_name": model,
            "trait_types": [trait],
        })
        
        test_vector = np.array(test_response["vectors"][trait]["vector"])
        ref_vector = np.array(vector)
        
        similarity = np.dot(test_vector, ref_vector) / (
            np.linalg.norm(test_vector) * np.linalg.norm(ref_vector)
        )
        
        color = "green" if similarity > 0.5 else "red" if similarity < -0.5 else "yellow"
        table.add_row(text, f"[{color}]{similarity:.3f}[/{color}]")
    
    console.print(table)
    
    console.print(f"\n[dim]Reference vector can now be used for trait detection[/dim]")
    
    # Track usage
    client.track_usage("vector_extraction", 20 if not vector_file else 0)