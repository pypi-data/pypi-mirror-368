import typer
import pandas as pd
from .motifs import MotifCounter
from .generators import GeometricGenerator

app = typer.Typer(help="neuromotifs command-line interface")


@app.command()
def motifs(edges: str):
    """Count 3-node motifs from an edge CSV with columns u,v."""
    df = pd.read_csv(edges)
    counts = MotifCounter.from_edges(df).count_triplets()
    for k, v in sorted(counts.items()):
        print(f"{k},{v}")


@app.command()
def generate(
    positions: str, order: int = 2, p_mean: float = 0.025, out: str = "edges.csv"
):
    """Generate a geometry-aware random network and write edges to CSV."""
    pos = pd.read_csv(positions)
    G = GeometricGenerator.from_positions(pos).generate(order=order, p_mean=p_mean)
    pd.DataFrame(G.edges, columns=["u", "v"]).to_csv(out, index=False)


if __name__ == "__main__":
    app()
