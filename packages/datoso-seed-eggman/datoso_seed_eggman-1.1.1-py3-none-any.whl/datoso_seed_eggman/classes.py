""" Classes script needed for Eggman Dats """

import os
import shutil
import urllib
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile

from datoso.configuration.folder_helper import Folders


class ZipLinkParser(HTMLParser):
    """Parses HTML content to extract links to ZIP files from GitHub releases."""

    def __init__(self):
        super().__init__()
        self.zip_links = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]) -> None:
        """Handle the start tag in the HTML content.

        Args:
        ----
        tag (str):
            The name of the tag.
        attrs (list[tuple[str, str]]):
            A list of attribute name-value pairs.

        """
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            if '.zip' in href and '/releases/' in href:
                full_url = f"https://github.com{href}"
                if full_url not in self.zip_links:
                    self.zip_links.append(full_url)

class Eggman:
    """Base class for handling GitHub release assets.

    This class provides methods to construct links, parse HTML content,
    and filter out existing files based on a given folder.

    Attributes
    ----------
    tag : str
        The tag associated with the GitHub release.
    class_name : str
        The name of the class.
    zip_links : list
        A list of ZIP file links extracted from the release assets.

    Methods
    -------
    add_html(txt: str) -> str
        Wraps the given text in basic HTML tags.
    tag_link() -> str
        Constructs the GitHub tag link.
    assets_link() -> str
        Constructs the GitHub assets link.
    get_zip_links() -> None
        Extracts ZIP file links from the release assets.
    filter_existing(folder: Path) -> dict
        Filters out links whose files already exist in the given folder.

    """

    tag = None
    class_name = None
    zip_links: list = None
    zip_files: list = None
    unzip_folders: bool = True

    def add_html(self, txt: str) -> str:
        """Wrap the given text in basic HTML tags.

        Args:
            txt(str): The text to be wrapped in HTML tags.

        Returns:
            str: The input text wrapped with <html> and <body> tags.

        """
        header = '<html><body>'
        footer = '</body></html>'
        return header+txt+footer

    def tag_link(self) -> str:
        """Construct the GitHub tag link.

        Returns:
            tag: The URL of the GitHub tag link.

        """
        return f"https://github.com/Eggmansworld/Datfiles/releases/tag/{self.tag}"

    def assets_link(self) -> str:
        """Construct the GitHub assets link.

        Returns:
            str: The URL of the GitHub assets link.

        """
        return f"https://github.com/Eggmansworld/Datfiles/releases/expanded_assets/{self.tag}"

    def calculate_files(self):
        self.zip_files = [file.split('/')[-1] for file in self.zip_links]

    def get_zip_links(self) -> None:
        """Extract ZIP file links from the GitHub release assets.

        This method fetches the HTML content of the assets link, parses it
        using the ZipLinkParser, and updates the `zip_links` attribute with
        the extracted ZIP file links.

        """
        response = urllib.request.urlopen(self.assets_link())  # noqa: S310
        parser = ZipLinkParser()
        parser.feed(self.add_html(str(response.read())))
        self.zip_links = parser.zip_links
        self.calculate_files()

    def filter_existing(self, folder: Path) -> None:
        """Filter out links that already exist as files in the given folder.

        Args:
            links (list): List of download links
            folder (Path): Folder path to check for existing files

        Returns:
            list: Filtered list of links whose files don't exist yet

        """
        filtered = []
        for link in self.zip_links:
            filename = link.split('/')[-1]
            if not (folder / filename).exists():
                filtered.append(link)
        self.zip_links = filtered
        self.calculate_files()

    def extract_zips(self, folder_helper: Folders) -> None:
        for file in self.zip_files:
            try:
                if self.unzip_folders:
                    with ZipFile(folder_helper.dats / file) as zip_file:
                        zip_file.extractall(folder_helper.dats / self.tag)
                else:
                    os.makedirs(folder_helper.dats / self.tag, exist_ok=True)
                    with ZipFile(folder_helper.dats / file) as zip_file:
                        for member in zip_file.namelist():
                            filename = os.path.basename(member)
                            # skip directories
                            if not filename:
                                continue
                            # copy file (taken from zipfile's extract)
                            source = zip_file.open(member)
                            target = open(folder_helper.dats / self.tag / filename, "wb")
                            with source, target:
                                shutil.copyfileobj(source, target)
            except NotImplementedError:
                print(f"Error: {file} has a compression method that is not supported.")

class Digitoxin(Eggman):
    """Represents the Digitoxin GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for Digitoxin-related assets.
    """

    tag = 'touhou'
    class_name = None

class Touhou(Eggman):
    """Represents the Touhou GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for Touhou-related assets.
    """

    tag = 'touhou'
    class_name = None

class Teknoparrot(Eggman):
    """Represents the Teknoparrot GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for Teknoparrot-related assets.
    """

    tag = 'teknoparrot'
    class_name = None

class SharpX68000(Eggman):
    """Represents the Sharp X68000 GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for Sharp X68000-related assets.
    """

    tag = 'sharpx68000'
    class_name = None

class SegaALLNet(Eggman):
    """Represents the Sega ALL.Net GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for Sega ALL.Net-related assets.
    """

    tag = 'segaalldotnet'
    class_name = None
    unzip_folders = False

class PinballPC(Eggman):
    """Represents the PinballPC GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for PinballPC-related assets.
    """

    tag = 'pinballpc'
    class_name = None

class LaserDisc(Eggman):
    """Represents the LaserDisc GitHub release assets.

    This class inherits from the Eggman base class and sets the specific
    tag for LaserDisc-related assets.
    """

    tag = 'laserdisc'
    class_name = None

class Hvsc(Eggman):
    """Represents the HVSC GitHub release assets.

    This class inherits from Eggman and provides functionality specific
    to handling the HVSC assets.
    """

    tag = 'hvsc'
    class_name = None

class GoodTools(Eggman):
    """Represents the Good Tools GitHub release assets.

    This class inherits from the Eggman base class and sets the specific tag
    for Good Tools-related assets.
    """

    tag = 'goodtools'
    class_name = None

class FruitMachines(Eggman):
    """Represents the Fruit Machines GitHub release assets.

    This class inherits from Eggman and sets the specific tag for Fruit Machines-related assets.
    """

    tag = 'fruitmachines'
    class_name = None

class C64Ultimate(Eggman):
    """Represents the C64 Ultimate Tape GitHub release assets.

    This class inherits from Eggman and sets the specific tag for C64 Ultimate Tape-related assets.
    """

    tag = 'c64ultimatetape'
    class_name = None

class RPGMaker(Eggman):
    """Represents the RPG Maker GitHub release assets.

    This class inherits from Eggman and sets the specific tag for RPG Maker-related assets.
    Note: No specific class is defined for RPG Maker, so this is a placeholder.
    """

    tag = 'rpgmaker'
    class_name = None

class ProjectEgg(Eggman):
    """Represents the Project Egg GitHub release assets.

    This class inherits from Eggman and sets the specific tag for Project Egg-related assets.
    Note: No specific class is defined for Project Egg, so this is a placeholder.
    """

    tag = 'projectegg'
    class_name = None

tag_classes = {
    'touhou': Touhou(),
    'digitoxin': Digitoxin(),
    'teknoparrot': Teknoparrot(),
    'sharpx68000': SharpX68000(),
    'segaalldotnet': SegaALLNet(),
    'pinballpc': PinballPC(),
    'laserdisc': LaserDisc(),
    'hvsc': Hvsc(),
    'goodtools': GoodTools(),
    'fruitmachines': FruitMachines(),
    'c64ultimatetape': C64Ultimate(),
    'rpgmaker': RPGMaker(),
    'projectegg': ProjectEgg(),
}
