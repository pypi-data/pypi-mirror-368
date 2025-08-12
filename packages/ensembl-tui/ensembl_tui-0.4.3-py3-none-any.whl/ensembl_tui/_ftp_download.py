import pathlib
import typing
from collections.abc import Callable
from ftplib import FTP, error_perm

from rich.progress import Progress, track
from unsync import unsync

from ensembl_tui import _util as eti_util


def configured_ftp(host: str = "ftp.ensembl.org") -> FTP:
    ftp = FTP(host)
    ftp.login()
    return ftp


def listdir(
    host: str,
    path: str,
    pattern: Callable | None = None,
) -> typing.Iterator[str]:
    """returns directory listing"""
    pattern = pattern or (lambda x: True)
    ftp = configured_ftp(host=host)
    try:
        ftp.cwd(path)
    except error_perm:
        msg = "\n".join(
            [
                "",
                f"Skipping {path}",
                "Could not change into directory on FTP site.",
                "This can be because of Ensembl naming inconsistencies.",
                "Check names are consistent between genomes and homology.",
            ],
        )
        eti_util.print_colour(msg, "red")
        return

    for fn in ftp.nlst():
        if pattern(fn):
            yield f"{path}/{fn}"

    ftp.close()


def _copy_to_local(
    host: str,
    src: eti_util.PathType,
    dest: eti_util.PathType,
) -> eti_util.PathType:
    if dest.exists():
        return dest
    ftp = configured_ftp(host=host)
    # pass in checksum and keep going until it's correct?
    with eti_util.atomic_write(dest, mode="wb") as outfile:
        ftp.retrbinary(f"RETR {src}", outfile.write)

    ftp.close()
    return dest


unsynced_copy_to_local = unsync(_copy_to_local)


def _get_saved_paths_unsync(description, host, local_dest, remote_paths):
    tasks = [
        unsynced_copy_to_local(host, path, local_dest / pathlib.Path(path).name)
        for path in remote_paths
    ]
    for task in tasks:
        yield task.result()


def _get_saved_paths(description, host, local_dest, remote_paths):  # pragma: no cover
    # keep this, it's useful for debugging
    saved_paths = []
    for path in track(remote_paths, description=description, transient=True):
        saved = _copy_to_local(host, path, local_dest / pathlib.Path(path).name)
        saved_paths.append(saved)
    return saved_paths


def download_data(
    *,
    host: str,
    local_dest: eti_util.PathType,
    remote_paths: list[str],
    description: str,
    do_checksum: bool,
    progress: Progress | None = None,
) -> bool:
    saved_paths = _get_saved_paths_unsync(description, host, local_dest, remote_paths)

    if progress is not None:
        download = progress.add_task(
            total=len(remote_paths),
            description=description,
            transient=True,
        )
    # load the signature data and sig calc keyed by parent dir
    all_checksums = {}
    all_check_funcs = {}
    for path in saved_paths:
        if eti_util.is_signature(path):
            all_checksums[str(path.parent)] = eti_util.get_signature_data(path)
            all_check_funcs[str(path.parent)] = eti_util.get_sig_calc_func(path.name)

        if progress is not None:
            progress.update(download, description=description, advance=1)

    if progress is not None:
        progress.remove_task(download)

    if do_checksum:
        msg = "Validating checksums"
        if progress:
            checking = progress.add_task(
                total=len(remote_paths),
                description=msg,
                transient=True,
            )
        for path in saved_paths:
            if progress is not None:
                progress.update(checking, description=msg, advance=1)

            if eti_util.dont_checksum(path):
                continue
            key = str(path.parent)
            expect_sig = all_checksums[key][path.name]
            calc_sig = all_check_funcs[key]
            signature = calc_sig(path.read_bytes(), path.stat().st_size)
            assert signature == expect_sig, path

        if progress is not None:
            progress.remove_task(checking)

    return True
