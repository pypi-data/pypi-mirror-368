import shutil

from rich.progress import Progress

from ensembl_tui import _config as eti_config
from ensembl_tui import _genome as eti_genome
from ensembl_tui import _ingest_align as ingest_aln
from ensembl_tui import _ingest_annotation as eti_db_ingest
from ensembl_tui import _ingest_homology as homology_ingest
from ensembl_tui import _species as eti_species
from ensembl_tui import _util as eti_util


def local_install_genomes(
    config: eti_config.Config,
    force_overwrite: bool,
    max_workers: int | None,
    verbose: bool = False,
    progress: Progress | None = None,
) -> None:
    if force_overwrite:
        shutil.rmtree(config.install_genomes, ignore_errors=True)
    # we create the local installation
    config.install_genomes.mkdir(parents=True, exist_ok=True)
    # we create subdirectories for each species
    for db_name in list(config.db_names):
        sp_dir = config.install_genomes / db_name
        sp_dir.mkdir(parents=True, exist_ok=True)

    # for each species, we identify the download and dest paths for annotations
    db_names = list(config.db_names)
    if max_workers:
        max_workers = min(len(db_names) + 1, max_workers)

    if verbose:
        eti_util.print_colour(f"\nInstalling genomes {max_workers=}", "yellow")

    # we do this the installation of features in serial for now
    writer = eti_db_ingest.mysql_dump_to_parquet(config=config)
    tasks = eti_util.get_iterable_tasks(
        func=writer,
        series=db_names,
        max_workers=max_workers,
    )
    if progress is not None:
        msg = "Installing features 📚"
        write_features = progress.add_task(
            total=len(db_names),
            description=msg,
            advance=0,
        )

    for result in tasks:
        if not result:
            msg = f"{result=}"
            raise RuntimeError(msg)

        if progress is not None:
            progress.update(write_features, description=msg, advance=1)

    species_table = eti_species.Species.to_table()
    species_table.write(config.install_genomes / eti_species.SPECIES_NAME)
    if verbose:
        eti_util.print_colour("\nFinished installing features", "yellow")

    if progress is not None:
        msg = "Installing  🧬🧬"
        write_seqs = progress.add_task(total=len(db_names), description=msg, advance=0)
    # we parallelise across databases
    writer = eti_genome.fasta_to_hdf5(config=config)
    tasks = eti_util.get_iterable_tasks(
        func=writer,
        series=db_names,
        max_workers=max_workers,
    )
    for result in tasks:
        if not result:
            msg = f"{result=}"
            raise RuntimeError(msg)

        if progress is not None:
            progress.update(write_seqs, description=msg, advance=1)

    if verbose:
        eti_util.print_colour("\nFinished installing sequences", "yellow")


def local_install_alignments(
    config: eti_config.Config,
    force_overwrite: bool,
    max_workers: int | None,
    verbose: bool = False,
    progress: Progress | None = None,
) -> None:
    # check if alignments are specified in the config
    if not config.align_names:
        if verbose:
            eti_util.print_colour(
                "No alignments specified in the config. Skipping alignment installation.",
                "yellow",
            )
        return

    if force_overwrite:
        shutil.rmtree(config.install_aligns, ignore_errors=True)

    for align_name in config.align_names:
        ingest_aln.install_alignment(
            config=config,
            align_name=align_name,
            progress=progress,
            max_workers=max_workers,
        )

    if verbose:
        eti_util.print_colour("\nFinished installing alignments", "yellow")


def local_install_homology(
    config: eti_config.Config,
    force_overwrite: bool,
    max_workers: int | None,
    verbose: bool = False,
    progress: Progress | None = None,
) -> None:
    # check if homologies are specified in the config
    if not config.homologies:
        if verbose:
            eti_util.print_colour(
                "No homologies specified in the config. Skipping homology installation.",
                "yellow",
            )
        return

    if force_overwrite:
        shutil.rmtree(config.install_homologies, ignore_errors=True)

    config.install_homologies.mkdir(parents=True, exist_ok=True)

    dirnames = []
    for sp in config.db_names:
        path = config.staging_homologies / sp
        dirnames.extend(list(path.glob("*.tsv*")))

    max_workers = min(len(dirnames) + 1, max_workers) if max_workers else 1

    if verbose:
        eti_util.print_colour(f"homologies {max_workers=}", "yellow")

    loader = homology_ingest.load_homologies(
        allowed_species=set(config.db_names),
    )
    if progress is not None:
        msg = "Loading homologies"
        load_homs = progress.add_task(
            total=len(dirnames),
            description=msg,
            advance=0,
            transient=True,
        )

    tasks = eti_util.get_iterable_tasks(
        func=loader,
        series=dirnames,
        max_workers=max_workers,
    )
    results = {}
    for result in tasks:
        for rel_type, records in result.items():
            if rel_type not in results:
                results[rel_type] = []
            results[rel_type].extend(records)

        if progress is not None:
            progress.update(load_homs, description=msg, advance=1)

    if progress is not None:
        progress.remove_task(load_homs)
        msg = "Aggregating homologies"
        agg = progress.add_task(
            total=len(results),
            description=msg,
            advance=0,
            transient=True,
        )

    # we merge the homology groups
    for rel_type, records in results.items():
        results[rel_type] = homology_ingest.merge_grouped(records)

        if progress is not None:
            progress.update(agg, description=msg, advance=1)

    # write the homology groups to in-memory db
    if progress is not None:
        progress.remove_task(agg)
        msg = "Installing homologies"
        write = progress.add_task(total=len(results), description=msg, advance=0)

    db = homology_ingest.make_homology_aggregator_db()
    for rel_type, records in results.items():
        db.add_records(records=records, relationship_type=rel_type)
        if progress is not None:
            progress.update(write, description=msg, advance=1)

    homology_ingest.write_homology_views(agg=db, outdir=config.install_homologies)
    if verbose:
        eti_util.print_colour("\nFinished installing homologies", "yellow")
