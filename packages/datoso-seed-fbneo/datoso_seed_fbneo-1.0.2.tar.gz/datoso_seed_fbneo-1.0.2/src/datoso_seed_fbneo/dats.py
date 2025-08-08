"""FinalBurn Neo DAT files."""
from datoso.repositories.dat_file import XMLDatFile

systems = {
    'FinalBurn Neo - Arcade Games': 'arcade',
    'FinalBurn Neo - ColecoVision Games': 'coleco',
    'FinalBurn Neo - Fairchild Channel F Games': 'channelf',
    'FinalBurn Neo - FDS Games': 'fds',
    'FinalBurn Neo - Game Gear Games': 'gamegear',
    'FinalBurn Neo - Master System Games': 'sms',
    'FinalBurn Neo - Megadrive Games': 'megadrive',
    'FinalBurn Neo - MSX 1 Games': 'msx',
    'FinalBurn Neo - Neo Geo Games': 'neogeo',
    'FinalBurn Neo - Neo Geo Pocket Games': 'ngp',
    'FinalBurn Neo - NES Games': 'nes',
    'FinalBurn Neo - SNES Games': 'snes',
    'FinalBurn Neo - PC-Engine Games': 'pce',
    'FinalBurn Neo - Sega SG-1000 Games': 'sg1000',
    'FinalBurn Neo - SuprGrafx Games': 'sgx',
    'FinalBurn Neo - TurboGrafx 16 Games': 'tg16',
    'FinalBurn Neo - ZX Spectrum Games': 'spectrum',
    'FinalBurn Neo - FinalBurn Neo - Neo Geo Games': 'neogeo',
}

class FbneoDat(XMLDatFile):
    """FinalBurn Neo DAT file."""

    seed: str = 'fbneo'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        # pylint: disable=R0801
        self.prefix = 'Emulators'
        self.company = 'FinalBurnNeo/roms'
        self.system = systems.get(self.name, 'unknown')
        self.suffix = ''
        self.date = ''

        return [self.prefix, self.company, self.system, self.suffix, self.date]
