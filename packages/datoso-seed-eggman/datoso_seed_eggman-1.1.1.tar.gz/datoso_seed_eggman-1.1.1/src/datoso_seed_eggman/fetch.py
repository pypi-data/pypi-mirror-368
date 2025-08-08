"""Fetch and download DAT files."""

import urllib
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

from datoso.configuration.folder_helper import Folders
from datoso.helpers import Bcolors
from datoso.helpers.download import downloader
from datoso.helpers.file_utils import move_path
from datoso_seed_eggman import __prefix__
from datoso_seed_eggman.classes import tag_classes


class TagLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tag_links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href', '')
            if '/tag/' in href:
                full_url = f"https://github.com{href}"
                if full_url not in self.tag_links:
                    self.tag_links.append(full_url)

def detect_new(links: dict) -> None:
    for tag in links:
        if tag not in tag_classes:
            print(f'Detected a new dat: {tag}')

def get_tag_links(initial_url) -> list:
    """Get all tag links from a GitHub repository tags page."""
    # response = requests.get(initial_url)
    response = urllib.request.urlopen(initial_url)  # noqa: S310
    parser = TagLinkParser()
    parser.feed(str(response.read()))
    detect_new([x.split('/')[-1] for x in parser.tag_links])
    return parser.tag_links

# def add_html(txt: str) -> str:
#     header = '<html><body>'
#     footer = '</body></html>'
#     return header+txt+footer

# def get_zip_link(tag_url: str) -> list:
#     response = urllib.request.urlopen(tag_url)  # noqa: S310
#     parser = ZipLinkParser()
#     parser.feed(add_html(str(response.read())))
#     return parser.zip_links

# def get_all_zip_links() -> dict:
#     initial_url = "https://github.com/Eggmansworld/Datfiles/tags"
#     tags = get_tag_links(initial_url=initial_url)
#     print(json.dumps(tags, indent=4))
#     tag_urls = [url.replace('/tag/', '/expanded_assets/') for url in tags]
#     # links = [result for url in tag_urls for result in get_zip_link(url)]
#     links = [
#         result for url in tag_urls for result in get_zip_link(url)
#     ]

#     return links

# def filter_existing(links: dict, folder: Path) -> dict:
#     """Filter out links that already exist as files in the given folder.

#     Args:
#         links (list): List of download links
#         folder (Path): Folder path to check for existing files

#     Returns:
#         list: Filtered list of links whose files don't exist yet

#     """
#     filtered = {}
#     for tag, link in links.items():
#         filename = link.split('/')[-1]
#         if not (folder / filename).exists():
#             filtered[tag] = link
#     return filtered

def download_dat(href: str, folder: Path) -> None:
    """Download a DAT file."""
    file_name = href.split('/')[-1]
    destination = folder / file_name
    print(f'* Downloading {Bcolors.OKGREEN}{file_name}{Bcolors.ENDC} to {href}')
    downloader(url=href, destination=destination, reporthook=None)

def download_dats(links: list, folder: Path) -> None:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(download_dat, href, folder) for href in links
        ]
        for future in futures:
            future.result()

def get_all_zip_links() -> dict:
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(tag_class.get_zip_links) for tag, tag_class in tag_classes.items()
        ]
    for future in futures:
        future.result()

def backup_downloaded_files(files: list, folder_helper: Folders):
    for file in files:
        file_name = file.split('/')[-1]
        move_path(folder_helper.dats / file_name, folder_helper.backup)

def fetch() -> None:
    """Fetch and download DAT files."""
    initial_url = 'https://github.com/Eggmansworld/Datfiles/tags'
    folder_helper = Folders(seed=__prefix__)
    folder_helper.clean_dats()
    folder_helper.create_all()
    # Check if new tags are created
    get_tag_links(initial_url=initial_url)
    # Get zip links
    get_all_zip_links()
    for tag_class in tag_classes.values():
        tag_class.filter_existing(folder_helper.backup)
    zip_links = [element for tag_class in tag_classes.values() for element in tag_class.zip_links]
    download_dats(links=zip_links, folder=folder_helper.dats)
    for tag_class in tag_classes.values():
        tag_class.extract_zips(folder_helper)
    backup_downloaded_files(files=zip_links, folder_helper=folder_helper)
