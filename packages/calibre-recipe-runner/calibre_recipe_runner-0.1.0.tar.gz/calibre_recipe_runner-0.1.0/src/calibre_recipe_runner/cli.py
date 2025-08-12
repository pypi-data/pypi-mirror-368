import importlib.util
import types
import sys
import os
import shutil
import feedparser
from bs4 import BeautifulSoup
import tempfile
import subprocess
import importlib.resources as resources


# Stub the 'calibre' module
sys.modules['calibre'] = types.ModuleType('calibre')
sys.modules['calibre.web'] = types.ModuleType('calibre.web')
sys.modules['calibre.ebooks'] = types.ModuleType('calibre.ebooks')
sys.modules['calibre.ebooks.HTMLParser'] = types.ModuleType('calibre.ebooks.HTMLParser')
sys.modules['calibre.ebooks.BeautifulSoup'] = types.ModuleType('calibre.ebooks.BeautifulSoup')
sys.modules['calibre.web.feeds'] = types.ModuleType('calibre.web.feeds')
sys.modules['calibre.web.feeds.news'] = types.ModuleType('calibre.web.feeds.news')
sys.modules['calibre'] = types.ModuleType('calibre')
sys.modules['calibre.browser'] = types.ModuleType('calibre.browser')
sys.modules['calibre.ptempfile'] = types.ModuleType('calibre.ptempfile')
sys.modules['calibre.utils.logging'] = types.ModuleType('calibre.utils.logging')
sys.modules['calibre.customize'] = types.ModuleType('calibre.customize')
sys.modules['calibre.utils.date'] = types.ModuleType('calibre.utils.date')
sys.modules['calibre.utils.magick'] = types.ModuleType('calibre.utils.magick')

from .stubs import BasicNewsRecipe, HTMLParser, Browser, Log, Recipe, Image, parse_date, PersistentTemporaryFile, classes
sys.modules['calibre.web.feeds.news'].BasicNewsRecipe = BasicNewsRecipe
sys.modules['calibre.web.feeds.news'].classes = classes
sys.modules['calibre.ebooks.HTMLParser'].HTMLParser = HTMLParser
sys.modules['calibre.ebooks.BeautifulSoup'].BeautifulSoup = BeautifulSoup
sys.modules['calibre.browser'].Browser = Browser
sys.modules['calibre.ptempfile'].TemporaryDirectory = tempfile.TemporaryDirectory
sys.modules['calibre.ptempfile'].TemporaryFile = tempfile.TemporaryFile
sys.modules['calibre.ptempfile'].NamedTemporaryFile = tempfile.NamedTemporaryFile
sys.modules['calibre.ptempfile'].PersistentTemporaryFile = PersistentTemporaryFile
sys.modules['calibre.utils.logging'].Log = Log
sys.modules['calibre.customize'].Recipe = Recipe
sys.modules['calibre.utils.date'].parse_date = parse_date
sys.modules['calibre.utils.magick'].Image = Image

COLLECTION_PATH = os.path.expanduser("~")+"/.local/share/calibre-recipe-runner/recipes/"

from . import stubs
blacklist = [    # omit base classes for recipe import
    name for name in dir(stubs)
    if isinstance(getattr(stubs, name), type)
]

def run_update():
    with resources.path("calibre_recipe_runner", "get-recipes.sh") as script_path:
        subprocess.run(["bash", str(script_path)], check=True)

def load_recipe(path):
    path_tmp = path.replace(".recipe", ".py")
    shutil.copy(path, path_tmp)
    spec = importlib.util.spec_from_file_location("recipe", path_tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    os.remove(path_tmp)

    # Find the class (usually only one)
    for name in dir(mod):
        if name in blacklist:
            continue
        obj = getattr(mod, name)
        if isinstance(obj, type):
            return obj()

    raise Exception("No recipe class found")

def run_scraper(recipe):
    if hasattr(recipe, "get_feeds"):
        feeds = recipe.get_feeds()
        for section, url in feeds:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                print(entry.link.split("?")[0])
    elif hasattr(recipe, "parse_index"):
        print("Using custom parse_index()")
        urls = recipe.parse_index()
        for url in urls:
            print(url.split("?")[0])
    else:
        print("No scraping method found")

def main():

    if "--update" in sys.argv:
        run_update()
        exit(0)

    if "--help" in sys.argv or len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <recipe name or path>")
        sys.exit(1)

    arg = sys.argv[1]
    if os.path.exists(arg):
        path = arg
    elif ".recipe" not in arg:
        path = os.path.join(COLLECTION_PATH, arg + ".recipe")
    else:
        path = os.path.join(COLLECTION_PATH, arg)

    recipe = load_recipe(path)
    run_scraper(recipe)

