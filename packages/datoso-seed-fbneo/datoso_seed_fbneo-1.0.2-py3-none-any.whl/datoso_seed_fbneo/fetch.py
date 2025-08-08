"""Fetch and download DAT files."""
import os
import zipfile
from datetime import datetime
from pathlib import Path

from dateutil import tz

from datoso.configuration import config, logger
from datoso.configuration.folder_helper import Folders
from datoso.helpers import show_progress
from datoso.helpers.download import downloader
from datoso_seed_fbneo import __prefix__

urls = {
    'libretro': 'https://github.com/libretro/FBNeo/archive/refs/heads/master.zip',
    # 'finalburnneo': {
    #     'win32': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/Windows.x32.zip',
    #     'win64': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/Windows.x64.zip',
    #     'linuxsdl1.2': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/Linux.SDL.1.2.zip',
    #     'linuxsdl2': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/Linux.SDL.2.zip',
    # },
    'finalburnneo': {
        'win32': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/windows-x86_32.zip',
        'win64': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/windows-x86_64.zip',
        'linuxsdl1.2': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/linux-sdl1-x86_64.zip',
        'linuxsdl2': 'https://github.com/finalburnneo/FBNeo/releases/download/latest/linux-sdl2-x86_64.zip',
    },
}

listinfos = {
    '-listinfo': 'FinalBurn Neo Arcade Games.dat',
    '-listinfochannelfonly': 'FinalBurn Neo Fairchild Channel F Games.dat',
    '-listinfocolecoonly': 'FinalBurn Neo ColecoVision Games.dat',
    '-listinfofdsonly': 'FinalBurn Neo FDS Games.dat',
    '-listinfoggonly': 'FinalBurn Neo Game Gear Games.dat',
    '-listinfomdonly': 'FinalBurn Neo Megadrive Games.dat',
    '-listinfomsxonly': 'FinalBurn Neo MSX 1 Games.dat',
    '-listinfoneogeoonly': 'FinalBurn Neo Neo Geo Games.dat',
    '-listinfonesonly': 'FinalBurn Neo NES Games.dat',
    '-listinfongponly': 'FinalBurn Neo Neo Geo Pocket Games.dat',
    '-listinfopceonly': 'FinalBurn Neo PC-Engine Games.dat',
    '-listinfosg1000only': 'FinalBurn Neo Sega SG-1000 Games.dat',
    '-listinfosgxonly': 'FinalBurn Neo SuprGrafx Games.dat',
    '-listinfosmsonly': 'FinalBurn Neo Master System Games.dat',
    '-listinfosnesonly': 'FinalBurn Neo SNES Games.dat',
    '-listinfospectrumonly': 'FinalBurn Neo ZX Spectrum Games.dat',
    '-listinfotg16only': 'FinalBurn Neo TurboGrafx 16 Games.dat',
}

class FBNeoFetcher:
    """Class for fetching FBNeo DAT files."""

    url: str = None
    folders: Folders = None

    def __init__(self, url: str, folders: Folders) -> None:
        """Initialize the FetchLibretro class with a URL."""
        self.url = url
        self.folders = folders


class FetchLibretro(FBNeoFetcher):
    """Class for fetching Libretro DAT files."""

    def download(self) -> None:
        """Download DAT files."""
        logger.info(f'Downloading {self.url} to {self.folders.download}\n')
        downloader(url=self.url, destination=self.folders.download / 'fbneo.zip', reporthook=show_progress)
        logger.info(f'Extracting dats from {self.folders.download}\n')

    def extract_dats(self) -> None:
        """Extract DAT files."""
        full = config['FBNEO'].getboolean('FetchFull', True)
        light = config['FBNEO'].getboolean('FetchLight', False)

        with zipfile.ZipFile(self.folders.download / 'fbneo.zip', 'r') as zip_ref:
            filelist = [f for f in zip_ref.filelist if f.filename.startswith('FBNeo-master/dats/')
                        and f.filename.endswith('.dat')]
            filelist_full = [f for f in filelist if '/light/' not in f.filename]
            filelist_light = [f for f in filelist if '/light/' in f.filename]
            if full:
                for file in filelist_full:
                    file_name = file.filename
                    file.filename = Path(file_name).name
                    zip_ref.extract(file, self.folders.dats / 'full')
                    file.filename = file_name
            if light:
                for file in filelist_light:
                    file_name = file.filename
                    file.filename = Path(file_name).name
                    zip_ref.extract(file, self.folders.dats / 'light')
                    file.filename = file_name


class FetchFinalBurnNeo(FBNeoFetcher):
    """Class for fetching FinalBurn Neo DAT files."""

    exec_folder: Path = None
    listinfos: dict = None
    exec = None

    def download(self) -> None:
        """Download DAT files."""
        logger.info(f'Downloading {self.url} to {self.folders.download}\n')
        downloader(url=self.url, destination=self.folders.download / 'fbneo.zip', reporthook=show_progress)
        logger.info(f'Extracting dats from {self.folders.download}\n')

    def init(self) -> None:
        """Initialize the executable folder."""
        self.listinfos = listinfos
        self.exec_folder = self.folders.download / 'exe'
        self.exec_folder.mkdir(parents=True, exist_ok=True)
        match config.get('FBNEO', 'System'):
            case 'win32':
                self.exec = 'fbneo.exe'
            case 'win64':
                self.exec = 'fbneo64.exe'
            case _:
                self.exec = 'fbneo'

    def execute_fbneo(self, parameter: str, file: str) -> None:
        """Execute FBNeo command."""
        full = config['FBNEO'].getboolean('FetchFull', True)
        light = config['FBNEO'].getboolean('FetchLight', False)

        if full:
            command = f'{self.exec_folder / self.exec} {parameter} > "{self.folders.dats / "full" / file}"'
        if light:
            command = f'{self.exec_folder / self.exec} {parameter} > "{self.folders.dats / "light" / file}"'

        os.system(f'cd {self.exec_folder} && {command}')  # noqa: S605

    def get_dats(self) -> None:
        """Get DAT files."""
        for parameter, file in self.listinfos.items():
            self.execute_fbneo(parameter, file)

    def extract_dats(self) -> None:
        """Extract DAT files."""
        self.init()
        with zipfile.ZipFile(self.folders.download / 'fbneo.zip', 'r') as zip_ref:
            zip_ref.extractall(self.exec_folder)
        self.get_dats()

def backup(folders: Folders) -> None:
    """Backup DAT files."""
    logger.info(f'Making backup from {folders.dats}\n')
    backup_daily_name = f'fbneo-{datetime.now(tz.tzlocal()).strftime("%Y-%m-%d")}.zip'
    with zipfile.ZipFile(folders.backup / backup_daily_name, 'w') as zip_ref:
        for root, _, files in os.walk(folders.dats):
            for file in files:
                zip_ref.write(Path(root) / file, arcname=Path(root).relative_to(folders.dats) / file,
                            compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    logger.info(f'Backup created at {folders.backup}\n')

def clean(folders: Folders) -> None:
    """Clean download folder."""
    logger.info(f'Cleaning {folders.download}\n')
    path = folders.download / 'fbneo.zip'
    if path.exists():
        path.unlink()

def fbneo_fetcher_factory(source: str, folders: Folders) -> FBNeoFetcher:
    """Create a fetcher based on the source."""
    if source == 'libretro':
        return FetchLibretro(url=urls['libretro'], folders=folders)
    system: str = config.get('FBNEO', 'System', fallback='win64')
    return FetchFinalBurnNeo(url=urls['finalburnneo'][system], folders=folders)

def fetch() -> None:
    """Fetch and download DAT files."""
    fetch_full = config.getboolean('FBNEO', 'FetchFull', fallback=True)
    fetch_light = config.getboolean('FBNEO', 'FetchLight', fallback=False)
    extras = []
    if fetch_full:
        extras.append('full')
    if fetch_light:
        extras.append('light')

    folder_helper = Folders(seed=__prefix__, extras=extras)
    folder_helper.clean_dats()
    folder_helper.create_all()

    download_from = config.get('FBNEO','DownloadFrom', fallback='libretro') # libretro or finalburnneo
    print()
    fetcher = fbneo_fetcher_factory(download_from, folder_helper)

    fetcher.download()
    fetcher.extract_dats()
    backup(folder_helper)
    clean(folder_helper)
