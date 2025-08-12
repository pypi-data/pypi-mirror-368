import configparser
import fnmatch
import pathlib
import sys
from collections.abc import Generator, Sequence
from dataclasses import dataclass

from ensembl_tui import _species as eti_species
from ensembl_tui import _util as eti_util

INSTALLED_CONFIG_NAME = "installed.cfg"
DOWNLOADED_CONFIG_NAME = "downloaded.cfg"

_COMPARA_NAME: str = "compara"
_ALIGNS_NAME: str = "aligns"
_HOMOLOGIES_NAME: str = "homologies"
_GENOMES_NAME: str = "genomes"


def make_relative_to(
    staging_path: pathlib.Path,
    install_path: pathlib.Path,
) -> pathlib.Path:
    assert staging_path.is_absolute() and install_path.is_absolute()

    for i, (s_part, i_part) in enumerate(
        zip(staging_path.parts, install_path.parts, strict=False),
    ):
        if s_part != i_part:
            break
    change_up = ("..",) * (len(staging_path.parts) - i)
    rel_path = change_up + install_path.parts[i:]
    return pathlib.Path(*rel_path)


@dataclass
class Config:
    host: str
    remote_path: str
    release: str
    staging_path: pathlib.Path
    install_path: pathlib.Path
    species_dbs: dict[str, list[str]]
    align_names: Sequence[str]
    tree_names: Sequence[str]
    homologies: bool

    def __post_init__(self) -> None:
        self.staging_path = pathlib.Path(self.staging_path)
        self.install_path = pathlib.Path(self.install_path)

    @property
    def remote_release_path(self) -> str:
        return f"{self.remote_path}/release-{self.release}"

    @property
    def staging_template_path(self) -> pathlib.Path:
        return self.staging_genomes / "coredb_templates"

    def update_species(self, species: dict[str, list[str]]) -> None:
        if not species:
            return
        for k in species:
            if k not in eti_species.Species:
                msg = f"Unknown species {k=!r}"
                raise ValueError(msg)
        self.species_dbs |= species

    @property
    def db_names(self) -> Generator[str, None, None]:
        for species in self.species_dbs:
            yield eti_species.Species.get_ensembl_db_prefix(species)

    @property
    def staging_genomes(self) -> pathlib.Path:
        return self.staging_path / _GENOMES_NAME

    @property
    def install_genomes(self) -> pathlib.Path:
        return self.install_path / _GENOMES_NAME

    @property
    def staging_homologies(self) -> pathlib.Path:
        return self.staging_path / _COMPARA_NAME / _HOMOLOGIES_NAME

    @property
    def install_homologies(self) -> pathlib.Path:
        return self.install_path / _COMPARA_NAME / _HOMOLOGIES_NAME

    @property
    def staging_aligns(self) -> pathlib.Path:
        return self.staging_path / _COMPARA_NAME / _ALIGNS_NAME

    @property
    def install_aligns(self) -> pathlib.Path:
        return self.install_path / _COMPARA_NAME / _ALIGNS_NAME

    def to_dict(self, relative_paths: bool = True) -> dict[str, str]:
        """returns cfg as a dict"""
        if not self.db_names:
            msg = "no db names"
            raise ValueError(msg)

        if not relative_paths:
            staging_path = str(self.staging_path)
            install_path = str(self.install_path)
        else:
            staging_path = "."
            install_path = str(make_relative_to(self.staging_path, self.install_path))

        data = {
            "remote path": {"path": str(self.remote_path), "host": str(self.host)},
            "local path": {
                "staging_path": staging_path,
                "install_path": install_path,
            },
            "release": {"release": self.release},
            "compara": {},
        }

        if self.align_names:
            data["compara"]["align_names"] = "".join(self.align_names)
        if self.tree_names:
            data["compara"]["tree_names"] = "".join(self.tree_names)

        if self.homologies:
            data["compara"]["homologies"] = ""

        if not data["compara"]:
            data.pop("compara")

        for db_name in self.db_names:
            data[db_name] = {"db": "core"}

        return data

    def write(self) -> None:
        """writes a ini to staging_path/DOWNLOADED_CONFIG_NAME

        Notes
        -----
        Updates value for staging_path to '.', and install directories to be
        relative to staging_path.
        """
        parser = configparser.ConfigParser()
        cfg = self.to_dict()
        for section, settings in cfg.items():
            parser.add_section(section)
            for option, val in settings.items():
                parser.set(section, option=option, value=val)
        self.staging_path.mkdir(parents=True, exist_ok=True)
        with (self.staging_path / DOWNLOADED_CONFIG_NAME).open(mode="w") as out:
            parser.write(out, space_around_delimiters=True)


@dataclass
class InstalledConfig:
    release: str
    install_path: pathlib.Path

    def __hash__(self) -> int:
        return id(self)

    def __post_init__(self) -> None:
        self.install_path = pathlib.Path(self.install_path)

    @property
    def compara_path(self) -> pathlib.Path:
        return self.install_path / _COMPARA_NAME

    @property
    def homologies_path(self) -> pathlib.Path:
        return self.compara_path / _HOMOLOGIES_NAME

    @property
    def aligns_path(self) -> pathlib.Path:
        return self.compara_path / _ALIGNS_NAME

    @property
    def genomes_path(self) -> pathlib.Path:
        return self.install_path / _GENOMES_NAME

    def installed_genome(self, species: str) -> pathlib.Path:
        db_name = eti_species.Species.get_ensembl_db_prefix(species)
        return self.genomes_path / db_name

    def list_genomes(self) -> list[str]:
        """returns list of installed genomes"""
        return [
            p.name for p in self.genomes_path.glob("*") if p.name in eti_species.Species
        ]

    def path_to_alignment(self, pattern: str, suffix: str) -> pathlib.Path | None:
        """returns the full path to alignment matching the name

        Parameters
        ----------
        pattern
            glob pattern for the Ensembl alignment name
        """
        if eti_util.contains_glob_pattern(pattern):
            align_dirs = [
                d
                for d in self.aligns_path.glob("*")
                if fnmatch.fnmatch(d.name, pattern)
            ]
        elif pattern:
            align_dirs = [d for d in self.aligns_path.glob("*") if pattern in d.name]
        else:
            align_dirs = None
        if not align_dirs:
            return None

        if len(align_dirs) > 1:
            msg = f"{pattern!r} matches too many directories in {self.aligns_path} {align_dirs}"
            raise ValueError(
                msg,
            )

        align_dir = align_dirs[0]
        if not list(align_dir.glob(f"*{suffix}")):
            msg = f"{align_dir} does not contain file with suffix {suffix}"
            raise FileNotFoundError(msg)
        return align_dir


def write_installed_cfg(config: Config) -> eti_util.PathType:
    """writes an ini file under config.installed_path"""
    parser = configparser.ConfigParser()
    parser.add_section("release")
    parser.set("release", "release", config.release)
    # create all the genome
    outpath = config.install_path / INSTALLED_CONFIG_NAME
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open(mode="w") as out:
        parser.write(out)
    return outpath


def read_installed_cfg(path: eti_util.PathType) -> InstalledConfig:
    """reads an ini file under config.installed_path"""
    path = pathlib.Path(path).expanduser()
    parser = configparser.ConfigParser()
    path = (
        path if path.name == INSTALLED_CONFIG_NAME else (path / INSTALLED_CONFIG_NAME)
    )
    if not path.exists():
        eti_util.print_colour(f"{path!s} does not exist, exiting", colour="red")
        sys.exit(1)

    parser.read(path)
    release = parser.get("release", "release")
    return InstalledConfig(release=release, install_path=path.parent)


def _standardise_path(
    path: eti_util.PathType,
    config_path: pathlib.Path,
) -> pathlib.Path:
    path = pathlib.Path(path).expanduser()
    return path if path.is_absolute() else (config_path / path).resolve()


def read_config(
    config_path: pathlib.Path,
    root_dir: pathlib.Path | None = None,
) -> Config:
    """returns ensembl release, local path, and db specifics from the provided
    config path"""
    from ensembl_tui._download import download_ensembl_tree

    if not config_path.exists():
        eti_util.print_colour(f"File not found {config_path.resolve()!s}", colour="red")
        sys.exit(1)

    parser = configparser.ConfigParser()

    with config_path.expanduser().open() as f:
        parser.read_file(f)

    if root_dir is None:
        root_dir = config_path.parent

    release = parser.get("release", "release")
    host = parser.get("remote path", "host")
    remote_path = parser.get("remote path", "path")
    remote_path = remote_path.removesuffix("/")
    # paths
    staging_path = _standardise_path(parser.get("local path", "staging_path"), root_dir)
    install_path = _standardise_path(parser.get("local path", "install_path"), root_dir)

    homologies = parser.has_option("compara", "homologies")
    species_dbs = {}
    get_option = parser.get
    align_names = []
    tree_names = []
    for section in parser.sections():
        if section in ("release", "remote path", "local path"):
            continue

        if section == "compara":
            value = get_option(section, "align_names", fallback=None)
            align_names = [] if value is None else [n.strip() for n in value.split(",")]
            value = get_option(section, "tree_names", fallback=None)
            tree_names = [] if value is None else [n.strip() for n in value.split(",")]
            continue

        dbs = [db.strip() for db in get_option(section, "db").split(",")]

        # handle synonyms
        species = eti_species.Species.get_species_name(section, level="raise")
        species_dbs[species] = dbs

    # we also want homologies if we want alignments
    homologies = homologies or bool(align_names)

    if tree_names:
        # add all species in the tree to species_dbs
        for tree_name in tree_names:
            tree = download_ensembl_tree(host, remote_path, release, tree_name)
            sp = eti_species.species_from_ensembl_tree(tree)
            species_dbs |= sp

    return Config(
        host=host,
        remote_path=remote_path,
        release=release,
        staging_path=staging_path,
        install_path=install_path,
        species_dbs=species_dbs,
        align_names=align_names,
        tree_names=tree_names,
        homologies=homologies,
    )
