import pathlib
import shutil
import sys
from collections import OrderedDict
from collections.abc import Mapping

import click
import trogon
from cogent3 import get_app, open_data_store
from scitrack import CachingLogger

from ensembl_tui import __version__
from ensembl_tui import _cli_option as cli_opt
from ensembl_tui import _config as eti_config
from ensembl_tui import _genome as eti_genome
from ensembl_tui import _homology as eti_homology
from ensembl_tui import _species as eti_species
from ensembl_tui import _util as eti_util

_click_command_opts = {
    "no_args_is_help": True,
    "context_settings": {"show_default": True},
}


class OrderedGroup(click.Group):
    def __init__(
        self,
        name: str | None = None,
        commands: Mapping[str, click.Command] | None = None,
        **kwargs,  # noqa: ANN003
    ) -> None:
        super().__init__(name, commands, **kwargs)
        #: the registered subcommands by their exported names.
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx: click.Context) -> Mapping[str, click.Command]:
        return self.commands


@trogon.tui()
@click.group(cls=OrderedGroup, **_click_command_opts)
@click.version_option(__version__)
def main() -> None:
    """Tools for obtaining and interrogating subsets of https://ensembl.org genomic data."""


@main.command(**_click_command_opts)
@cli_opt.dbrc_out
@cli_opt.force
def demo_config(outpath: pathlib.Path, force_overwrite: bool) -> None:
    """exports sample config and species table to the nominated path"""

    outpath = outpath.expanduser()
    if outpath.exists() and not force_overwrite:
        eti_util.print_colour(
            text=f"{outpath} exists, use --force_overwrite to overwrite",
            colour="blue",
            style="bold",
        )
        sys.exit(1)

    if outpath.exists():
        shutil.rmtree(outpath)
    outpath.mkdir(parents=True, exist_ok=True)
    shutil.copytree(eti_util.ENSEMBLDBRC, outpath, dirs_exist_ok=True)
    # we assume all files starting with alphabetical characters are valid
    for fn in pathlib.Path(outpath).glob("*"):
        if not fn.stem.isalpha():
            if fn.is_file():
                fn.unlink()
            else:
                # __pycache__ directory
                shutil.rmtree(fn)
    eti_util.print_colour(text=f"Contents written to {outpath}", colour="green")


@main.command(**_click_command_opts)
@cli_opt.cfgpath
@cli_opt.debug
@cli_opt.verbose
def download(configpath: pathlib.Path, debug: bool, verbose: bool) -> None:
    """download data from Ensembl's ftp site"""
    from rich import progress

    from ensembl_tui import _download as eti_download

    if not configpath:
        eti_util.print_colour(
            text="No config specified, exiting.",
            colour="red",
            style="bold",
        )
        sys.exit(1)

    config = eti_config.read_config(configpath, root_dir=pathlib.Path.cwd())

    if verbose:
        eti_util.print_colour(text=str(config), colour="yellow")

    if not any((config.species_dbs, config.align_names)):
        eti_util.print_colour(text="No genomes, no alignments specified", colour="red")
        sys.exit(1)

    if not config.species_dbs:
        species = eti_download.get_species_for_alignments(
            host=config.host,
            remote_path=config.remote_path,
            release=config.release,
            align_names=config.align_names,
        )
        config.update_species(species)

    if verbose:
        eti_util.print_colour(text=str(config.species_dbs), colour="yellow")

    config.write()
    with (
        eti_util.keep_running(),
        progress.Progress(
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
        ) as prog_bar,
    ):
        eti_download.download_species(config, debug, verbose, progress=prog_bar)
        eti_download.download_homology(config, debug, verbose, progress=prog_bar)
        eti_download.download_aligns(config, debug, verbose, progress=prog_bar)

    eti_util.print_colour(text=f"Downloaded to {config.staging_path}", colour="green")


@main.command(**_click_command_opts)
@cli_opt.download
@cli_opt.nprocs
@cli_opt.force
@cli_opt.verbose
def install(
    download: pathlib.Path,
    num_procs: int,
    force_overwrite: bool,
    verbose: bool,
) -> None:
    """create the local representations of the data"""
    from rich import progress

    from ensembl_tui._install import (
        local_install_alignments,
        local_install_genomes,
        local_install_homology,
    )

    configpath = download / eti_config.DOWNLOADED_CONFIG_NAME
    config = eti_config.read_config(configpath)
    if verbose:
        eti_util.print_colour(text=f"{config.install_path=}", colour="yellow")

    if force_overwrite:
        shutil.rmtree(config.install_path, ignore_errors=True)

    config.install_path.mkdir(parents=True, exist_ok=True)
    eti_config.write_installed_cfg(config)
    with (
        eti_util.keep_running(),
        progress.Progress(
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
        ) as progress_bar,
    ):
        local_install_genomes(
            config,
            force_overwrite=force_overwrite,
            max_workers=num_procs,
            verbose=verbose,
            progress=progress_bar,
        )
        local_install_homology(
            config,
            force_overwrite=force_overwrite,
            max_workers=num_procs,
            verbose=verbose,
            progress=progress_bar,
        )
        local_install_alignments(
            config,
            force_overwrite=force_overwrite,
            max_workers=num_procs,
            verbose=verbose,
            progress=progress_bar,
        )

    eti_util.print_colour(
        text=f"Contents installed to {str(config.install_path)!r}",
        colour="green",
    )


@main.command(**_click_command_opts)
@cli_opt.installed
def installed(installed: pathlib.Path) -> None:
    """show what is installed"""
    from cogent3 import make_table

    config = eti_config.read_installed_cfg(installed)

    genome_dir = config.genomes_path
    if genome_dir.exists():
        species = [fn.name for fn in genome_dir.glob("*")]
        data = {"species": [], "common name": []}
        for name in species:
            cn = eti_species.Species.get_common_name(name, level="ignore")
            if not cn:
                continue
            data["species"].append(name)
            data["common name"].append(cn)

        table = make_table(data=data, title="Installed genomes:")
        eti_util.rich_display(table)

    char = "✅" if config.homologies_path.exists() else "❌"
    eti_util.print_colour(f"Installed homologies: {char}", colour="blue", style="bold")

    char = "✅" if config.aligns_path.exists() else "❌"
    eti_util.print_colour(f"Installed alignments: {char}", colour="blue", style="bold")


@main.command(**_click_command_opts)
@cli_opt.installed
@cli_opt.species
def species_summary(installed: pathlib.Path, species: str) -> None:
    """genome summary data for a species"""

    config = eti_config.read_installed_cfg(installed)
    if species is None:
        eti_util.print_colour(text="ERROR: a species name is required", colour="red")
        sys.exit(1)

    if len(species) > 1:
        eti_util.print_colour(
            text=f"ERROR: one species at a time, not {species!r}",
            colour="red",
        )
        sys.exit(1)

    species = species[0]
    annot_db = eti_genome.load_annotations_for_species(
        path=config.installed_genome(species=species),
    )
    summary = eti_genome.get_species_gene_summary(annot_db=annot_db, species=species)
    eti_util.rich_display(summary)
    summary = eti_genome.get_species_repeat_summary(annot_db=annot_db, species=species)
    eti_util.rich_display(summary)


@main.command(**_click_command_opts)
@cli_opt.installed
@cli_opt.species
@cli_opt.outdir
@cli_opt.limit
def dump_genes(
    installed: pathlib.Path,
    species: str,
    outdir: pathlib.Path,
    limit: int,
) -> None:
    """export meta-data table for genes from one species to <species>-<release>.gene_metadata.tsv"""

    config = eti_config.read_installed_cfg(installed)
    if species is None:
        eti_util.print_colour(text="ERROR: a species name is required", colour="red")
        sys.exit(1)

    if len(species) > 1:
        eti_util.print_colour(
            text=f"ERROR: one species at a time, not {species!r}",
            colour="red",
        )
        sys.exit(1)

    annot_db = eti_genome.load_annotations_for_species(
        path=config.installed_genome(species=species[0]),
    )
    path = annot_db.source
    table = eti_genome.get_gene_table_for_species(annot_db=annot_db, limit=limit)
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / f"{path.stem}-{config.release}-gene_metadata.tsv"
    table.write(outpath)
    eti_util.print_colour(text=f"Finished: wrote {str(outpath)!r}!", colour="green")


@main.command(**_click_command_opts)
@cli_opt.installed
def compara_summary(installed: pathlib.Path) -> None:
    """summary data for compara"""
    from cogent3 import make_table

    config = eti_config.read_installed_cfg(installed)
    if config.homologies_path.exists():
        db = eti_homology.load_homology_db(
            path=config.homologies_path,
        )
        table = db.count_distinct(homology_type=True)
        table.title = "Homology types"
        table.format_column("count", lambda x: f"{x:,}")
        eti_util.rich_display(table)

    compara_aligns = config.aligns_path
    if compara_aligns.exists():
        align_names = {
            fn.stem for fn in compara_aligns.glob("*") if not fn.name.startswith(".")
        }
        eti_util.print_colour(
            "Installed whole genome alignments:",
            colour="blue",
            style="bold",
        )
        table = make_table(
            data={"align name": list(align_names)},
        )
        eti_util.rich_display(table)


@main.command(**_click_command_opts)
@cli_opt.installed
@cli_opt.outdir
@click.option(
    "-ht",
    "--homology_type",
    type=str,
    default="ortholog_one2one",
    help="type of homology",
)
@cli_opt.ref
@cli_opt.ref_genes
@cli_opt.coord_names
@cli_opt.nprocs
@cli_opt.limit
@cli_opt.force
@cli_opt.verbose
def homologs(
    installed: pathlib.Path,
    outdir: pathlib.Path,
    homology_type: str,
    ref: str,
    ref_genes: list[str] | None,
    coord_names: str,
    num_procs: int,
    limit: int,
    force_overwrite: bool,
    verbose: bool,
) -> None:
    """exports CDS sequence data in fasta format for homology type relationship"""
    from rich import progress

    LOGGER = CachingLogger()
    LOGGER.log_args()

    if ref is None:
        eti_util.print_colour(
            text="ERROR: a reference species name is required, use --ref",
            colour="red",
        )
        sys.exit(1)

    if ref_genes and coord_names:
        eti_util.print_colour(
            text="ERROR: cannot specify both ref_genes and coord_names",
            colour="red",
        )
        sys.exit(1)

    if force_overwrite:
        shutil.rmtree(outdir, ignore_errors=True)

    outdir.mkdir(parents=True, exist_ok=True)

    LOGGER.log_file_path = outdir / f"homologs-{ref}-{homology_type}.log"

    config = eti_config.read_installed_cfg(installed)
    eti_species.Species.update_from_file(config.genomes_path / "species.tsv")
    # we all the protein coding gene IDs from the reference species
    genome = eti_genome.load_genome(config=config, species=ref)

    if verbose:
        eti_util.print_colour(text=f"Loaded genome for {ref!r}", colour="yellow")

    # we don't use the limit argument for this query since we want the limit
    # to be the number of homology matches
    if not ref_genes:
        ref_genes = list(
            genome.annotation_db.get_ids_for_biotype(
                biotype="protein_coding",
                seqid=coord_names,
            ),
        )

    if verbose:
        eti_util.print_colour(
            text=f"Found {len(ref_genes):,} gene IDs for {ref!r}",
            colour="yellow",
        )

    db = eti_homology.load_homology_db(
        path=config.homologies_path,
    )
    related = []
    with progress.Progress(
        progress.TextColumn("[progress.description]{task.description}"),
        progress.BarColumn(),
        progress.TaskProgressColumn(),
        progress.TimeRemainingColumn(),
        progress.TimeElapsedColumn(),
    ) as progress_bar:
        searching = progress_bar.add_task(
            total=limit or len(ref_genes),
            description="Homolog search",
        )
        for gid in ref_genes:
            if rel := db.get_related_to(gene_id=gid, relationship_type=homology_type):
                related.append(rel)
                progress_bar.update(searching, advance=1)

            if limit and len(related) >= limit:
                break

        progress_bar.update(searching, advance=len(ref_genes))

        if verbose:
            eti_util.print_colour(
                text=f"Found {len(related)} homolog groups",
                colour="yellow",
            )

        get_seqs = eti_homology.collect_cds(config=config)
        out_dstore = open_data_store(base_path=outdir, suffix="fa", mode="w")

        reading = progress_bar.add_task(total=len(related), description="Extracting 🧬")
        for seqs in get_seqs.as_completed(
            related,
            parallel=num_procs > 1,
            show_progress=False,
            par_kw={"max_workers": num_procs},
        ):
            progress_bar.update(reading, advance=1)
            if not seqs:
                if verbose:
                    eti_util.print_colour(text=f"{seqs=}", colour="yellow")

                out_dstore.write_not_completed(
                    data=seqs.to_json(),
                    unique_id=seqs.source,
                )
                continue
            if not seqs.seqs:
                if verbose:
                    eti_util.print_colour(text=f"{seqs.seqs=}", colour="yellow")
                continue

            txt = seqs.to_fasta()
            out_dstore.write(data=txt, unique_id=seqs.source)

    log_file_path = pathlib.Path(LOGGER.log_file_path)
    LOGGER.shutdown()
    out_dstore.write_log(unique_id=log_file_path.name, data=log_file_path.read_text())
    log_file_path.unlink()


@main.command(**_click_command_opts)
@cli_opt.installed
@cli_opt.outdir
@cli_opt.align_name
@cli_opt.ref
@cli_opt.coord_names
@cli_opt.ref_genes
@cli_opt.mask
@cli_opt.mask_shadow
@cli_opt.mask_ref
@cli_opt.ref_coords
@cli_opt.limit
@cli_opt.force
@cli_opt.verbose
def alignments(
    installed: pathlib.Path,
    outdir: pathlib.Path,
    align_name: str,
    ref: str,
    coord_names: str,
    ref_genes: list[str] | None,
    mask: list[str] | None,
    mask_shadow: list[str] | None,
    mask_ref: bool,
    ref_coords: list[eti_genome.genome_segment],
    limit: int,
    force_overwrite: bool,
    verbose: bool,
) -> None:
    """export multiple alignments in fasta format for named genes"""
    from rich import progress

    from ensembl_tui import _align as eti_align

    if mask and mask_shadow:
        eti_util.print_colour(
            text="ERROR: cannot specify both mask and mask_shadow",
            colour="red",
        )
        sys.exit(1)

    if not ref:
        eti_util.print_colour(
            text="ERROR: must specify a reference genome",
            colour="red",
        )
        sys.exit(1)

    if force_overwrite:
        shutil.rmtree(outdir, ignore_errors=True)

    config = eti_config.read_installed_cfg(installed)
    align_db = eti_align.load_aligndb(config=config, align_name=align_name)
    ref_species = eti_species.Species.get_ensembl_db_prefix(ref)
    if ref_species not in align_db.get_species_names():
        eti_util.print_colour(
            text=f"species {ref!r} not in the alignment",
            colour="red",
        )
        sys.exit(1)

    # get all the genomes
    if verbose:
        eti_util.print_colour(
            text=f"working on species {align_db.get_species_names()}",
            colour="yellow",
        )

    genomes = {
        sp: eti_genome.load_genome(config=config, species=sp)
        for sp in align_db.get_species_names()
    }

    if ref_genes and ref_coords:
        eti_util.print_colour(
            text="ERROR: cannot specify both ref_genes and ref_coords",
            colour="red",
        )
        sys.exit(1)

    # load the gene stable ID's
    if ref_genes:
        stableids = ref_genes
    elif coord_names:
        genome = genomes[ref_species]
        stableids = list(
            genome.annotation_db.get_ids_for_biotype(
                biotype="protein_coding",
                seqid=coord_names,
                limit=limit,
            ),
        )
    else:
        stableids = None

    if ref_coords:
        locations = ref_coords
    else:
        locations = eti_genome.get_gene_segments(
            annot_db=genomes[ref_species].annotation_db,
            species=ref_species,
            limit=limit,
            stableids=stableids,
        )
    mask = mask_shadow or mask
    shadow = bool(mask_shadow)
    maker = eti_align.construct_alignment(
        align_db=align_db,
        genomes=genomes,
        mask_features=mask,
        shadow=shadow,
        mask_ref=mask_ref,
    )
    output = open_data_store(outdir, mode="w", suffix="fa")
    writer = get_app("write_seqs", format_name="fasta", data_store=output)
    with (
        eti_util.keep_running(),
        progress.Progress(
            progress.TextColumn("[progress.description]{task.description}"),
            progress.BarColumn(),
            progress.TaskProgressColumn(),
            progress.TimeRemainingColumn(),
            progress.TimeElapsedColumn(),
        ) as progress_bar,
    ):
        task = progress_bar.add_task(
            total=limit or len(locations),
            description="Getting alignment data",
        )
        for alignments in maker.as_completed(locations, show_progress=False):
            progress_bar.update(task, advance=1)
            if not alignments:
                eti_util.print_colour(str(alignments), colour="red")
                continue
            input_source = alignments[0].info.source
            if len(alignments) == 1:
                writer(alignments[0], identifier=input_source)
                continue

            for i, aln in enumerate(alignments):
                identifier = f"{input_source}-{i}"
                writer(aln, identifier=identifier)

    eti_util.print_colour(text="Done!", colour="green")


if __name__ == "__main__":
    main()
