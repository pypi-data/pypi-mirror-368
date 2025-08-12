from __future__ import annotations

import json
import sys as _sys
from importlib import import_module as _import_module
from typing import Optional

import click
import polars as pl

# Import version
from .version import __version__

# Import the implementation submodule but immediately restore the public
# callable on the parent package so that ``clonify.clonify`` remains a
# function even after this module is imported (pytest discovers the CLI test
# first which would otherwise clobber it).
#
# NOTE: we *must* perform the import in this way (rather than the original
# ``from .clonify import clonify as clonify_api``) to avoid Python's
# automatic parent attribute assignment that would overwrite
# ``clonify.clonify`` with the sub-module object.  By holding a reference to
# the actual function we can then patch the parent package back to the
# intended public API.
_clonify_mod = _sys.modules[
    __package__
]  # parent package already imported by the time this module loads
clonify_api = _clonify_mod.clonify  # type: ignore[attr-defined]

# NOTE: We purposefully **do not** import the submodule ``clonify.clonify`` here
# because doing so would cause the import machinery to assign that module object
# to ``clonify.clonify`` on the parent package, clobbering the public API
# callable.  By re-using the existing attribute we guarantee a stable function
# reference regardless of import order during the test suite.


def _write_dataframe(_: pl.DataFrame, __: str) -> None:
    # Deprecated in CLI; writing is handled in API. Keep stub for BC if referenced.
    raise click.ClickException("Internal error: writing is handled by API now.")


@click.command(context_settings={"show_default": True})
@click.version_option(version=__version__, prog_name="clonify")
@click.option(
    "--input",
    "input_path",
    type=click.Path(exists=True, dir_okay=False, path_type=str),
    required=True,
    help="Path to input table (CSV/TSV/Parquet/NDJSON/JSON).",
)
@click.option(
    "--input-format",
    type=click.Choice(
        ["csv", "tsv", "parquet", "ndjson", "json"], case_sensitive=False
    ),
    default=None,
    help="Explicitly set input format; otherwise inferred from file extension.",
)
@click.option(
    "--has-header/--no-header",
    default=True,
    help="Whether the input delimited file has a header row (CSV/TSV only).",
)
@click.option(
    "--delimiter",
    type=str,
    default=None,
    help="Custom delimiter for CSV/TSV. If not provided, uses ',' for CSV and '\t' for TSV.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(dir_okay=False, path_type=str),
    required=False,
    help="Where to write the output table. Format inferred from extension.",
)
@click.option(
    "--assignments-json",
    type=click.Path(dir_okay=False, path_type=str),
    required=False,
    help="Optional path to write lineage assignment mapping as JSON.",
)
# clonify() parameters mirrored below
@click.option(
    "--distance-cutoff",
    type=float,
    default=0.35,
    help="Distance cutoff for clustering.",
)
@click.option(
    "--shared-mutation-bonus",
    type=float,
    default=0.4,
    help="Bonus applied for shared mutations.",
)
@click.option(
    "--length-penalty-multiplier",
    type=float,
    default=2.0,
    help="Multiplier for length penalty term.",
)
@click.option(
    "--group-by-v/--no-group-by-v",
    default=True,
    help="Group sequences by V gene before clustering.",
)
@click.option(
    "--group-by-j/--no-group-by-j",
    default=True,
    help="Group sequences by J gene before clustering.",
)
@click.option(
    "--group-by-light-chain-vj/--no-group-by-light-chain-vj",
    default=True,
    help="Also group by light chain V/J genes when present.",
)
@click.option(
    "--id-key",
    type=str,
    default=None,
    help="Column name for unique sequence IDs.",
)
@click.option(
    "--vgene-key", type=str, default=None, help="Column name for V gene (heavy)."
)
@click.option(
    "--jgene-key", type=str, default=None, help="Column name for J gene (heavy)."
)
@click.option(
    "--cdr3-key", type=str, default=None, help="Column name for CDR3 (heavy)."
)
@click.option(
    "--mutations-key",
    type=str,
    default=None,
    help="Column name for V-region mutations (delimited string).",
)
@click.option(
    "--locus-key",
    type=str,
    default=None,
    help="Optional column name for locus; if set or inferred, rows will be filtered to IGH for allelic scan.",
)
@click.option(
    "--light-vgene-key",
    type=str,
    default=None,
    help="Optional column name for light chain V gene (e.g., 'v_gene:1').",
)
@click.option(
    "--light-jgene-key",
    type=str,
    default=None,
    help="Optional column name for light chain J gene (e.g., 'j_gene:1').",
)
@click.option(
    "--mutation-delimiter",
    type=str,
    default="|",
    help="Delimiter used within the mutations column.",
)
@click.option(
    "--ignore-likely-allelic-variants/--consider-likely-allelic-variants",
    default=False,
    help="Ignore mutations that are likely allelic variants.",
)
@click.option(
    "--allelic-variant-threshold",
    type=float,
    default=0.35,
    help="Frequency threshold to consider a mutation as likely allelic variant.",
)
@click.option(
    "--min-seqs-for-allelic-variants",
    type=int,
    default=200,
    help="Minimum sequences per V gene to evaluate allelic variants.",
)
@click.option(
    "--mnemonic-names/--random-names",
    default=True,
    help="Generate human-readable mnemonic lineage names instead of random strings.",
)
@click.option(
    "--n-threads",
    type=int,
    default=None,
    help="Number of threads for native clustering. Defaults to library default.",
)
@click.option(
    "--backend",
    type=click.Choice(["native", "python"], case_sensitive=False),
    default="native",
    help="Select clustering backend: 'native' (Rust) or 'python' (reference).",
)
@click.option(
    "--progressive/--no-progressive",
    default=False,
    help="Use progressive approximate clustering (LSH-guided) in native backend.",
)
@click.option(
    "--name-seed",
    type=int,
    default=None,
    help="Optional seed to make lineage names deterministic across backends.",
)
@click.option(
    "--verbose/--quiet",
    default=True,
    help="Print progress information.",
)
def cli(
    input_path: str,
    input_format: Optional[str],
    has_header: bool,
    delimiter: Optional[str],
    output_path: Optional[str],
    assignments_json: Optional[str],
    distance_cutoff: float,
    shared_mutation_bonus: float,
    length_penalty_multiplier: float,
    group_by_v: bool,
    group_by_j: bool,
    group_by_light_chain_vj: bool,
    id_key: str,
    vgene_key: str,
    jgene_key: str,
    cdr3_key: str,
    mutations_key: Optional[str],
    locus_key: Optional[str],
    light_vgene_key: Optional[str],
    light_jgene_key: Optional[str],
    mutation_delimiter: str,
    ignore_likely_allelic_variants: bool,
    allelic_variant_threshold: float,
    min_seqs_for_allelic_variants: int,
    mnemonic_names: bool,
    n_threads: Optional[int],
    backend: str,
    name_seed: Optional[int],
    verbose: bool,
    progressive: bool,
) -> None:
    """Run clonify on an input table and write results to a file or stdout.

    All parameters mirror the Python API and retain the same defaults.
    """
    # Input reading/writing is now handled by the clonify() API
    try:
        assignments, df_out = clonify_api(
            input_path,
            backend=backend,
            input_format=input_format,
            has_header=has_header,
            delimiter=delimiter,
            output_path=output_path,
            distance_cutoff=distance_cutoff,
            shared_mutation_bonus=shared_mutation_bonus,
            length_penalty_multiplier=length_penalty_multiplier,
            group_by_v=group_by_v,
            group_by_j=group_by_j,
            group_by_light_chain_vj=group_by_light_chain_vj,
            id_key=id_key,
            vgene_key=vgene_key,
            jgene_key=jgene_key,
            cdr3_key=cdr3_key,
            mutations_key=mutations_key,
            locus_key=locus_key,
            light_vgene_key=light_vgene_key,
            light_jgene_key=light_jgene_key,
            mutation_delimiter=mutation_delimiter,
            ignore_likely_allelic_variants=ignore_likely_allelic_variants,
            allelic_variant_threshold=allelic_variant_threshold,
            min_seqs_for_allelic_variants=min_seqs_for_allelic_variants,
            mnemonic_names=mnemonic_names,
            name_seed=name_seed,
            n_threads=n_threads,
            progressive=progressive,
            verbose=verbose,
        )
    except Exception as exc:  # pragma: no cover - surface backend errors nicely
        raise click.ClickException(str(exc)) from exc

    if assignments_json is not None:
        try:
            with open(assignments_json, "w", encoding="utf-8") as f:
                json.dump(assignments, f, ensure_ascii=False)
        except Exception as exc:  # pragma: no cover
            raise click.ClickException(
                f"Failed to write assignments JSON to {assignments_json}: {exc}"
            ) from exc

    if not output_path:
        # Default to CSV on stdout for human-friendliness
        click.echo(df_out.write_csv())


def main() -> None:
    cli(standalone_mode=True)


__all__ = ["cli", "main"]
