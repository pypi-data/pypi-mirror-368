import cProfile
import pstats
from pathlib import Path

import polars as pl
from helmkit import load_monomer_library
from helmkit import Molecule


def main():
    data_dir = Path(__file__).parent / "data"
    df = pl.read_csv(data_dir / "peptides.csv")

    # Remove peptides with monomers containing parentheses, spaces or hyphens
    # (as these do not work with pyPept)
    regex = r"\[[^\]]*[\(\s-][^\]]*\]"
    df = df.filter(pl.col("HELM").str.contains(regex).not_())
    helms = df["HELM"].to_list()

    monomer_db = load_monomer_library(data_dir / "monomers.sdf")

    for helm in helms:
        Molecule(helm, monomer_db)


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.run('main()')
    stats = pstats.Stats(profiler)
    stats.sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats()
