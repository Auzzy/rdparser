from rdparserlib.inventory import download
from rdparserlib.database import populate

def download_and_populate(inventory_filepath, database_filepath):
    inventory = download(inventory_filepath)
    populate(inventory, database_filepath)