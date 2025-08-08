"""DAT files for Eggman."""
from datoso.repositories.dat_file import XMLDatFile


class TeknoparrotDat(XMLDatFile):
    """Teknoparrot DAT file."""

    seed: str = 'eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.system = self.name
        self.company = getattr(self, 'company', None)
        self.prefix = 'Arcade'
        self.suffix = getattr(self, 'suffix', None)
        find_system = self.overrides()
        self.extra_configs(find_system)
        self.full_name = f'{self.header["description"]} - {self.system}' if self.header.get('description', None) else None

        return [None, self.company, self.system, self.suffix, self.get_date()]


    def get_date(self) -> str:
        """Get the date from the dat file."""
        return self.date


class EggmanDat(XMLDatFile):
    """Eggman DAT file."""

    seed: str = 'Eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.prefix = ''
        self.company = ''
        self.system = ''
        self.suffix = ''
        self.date = ''

        return [self.prefix, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        return self.date

class SegaALLDotNetDat(XMLDatFile):
    """SegaALLDotNet DAT file."""

    seed: str = 'eggman'

    def initial_parse(self) -> list:
        """Parse the dat file."""
        self.system = self.name
        self.company = getattr(self, 'company', None)
        self.prefix = 'Arcade'
        self.suffix = getattr(self, 'suffix', None)
        find_system = self.overrides()
        self.extra_configs(find_system)
        self.full_name = f'{self.header["description"]} - {self.system}' if self.header.get('description', None) else None

        return [None, self.company, self.system, self.suffix, self.get_date()]

    def get_date(self) -> str:
        """Get the date from the dat file."""
        return self.date
