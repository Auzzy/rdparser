import re

class RegexRule(object):
    def __init__(self, regex, name_format):
        self.re = re.compile(regex, re.IGNORECASE)
        self.name_format = name_format

    def apply(self, name):
        match = self.re.match(name)
        if not match:
            return None

        return name_format.format(**match.groupdict())

regex_rules = [
    
]


abbrv_mapping = {
    "xtra": "extra",
    "lrg": "large",
    "prem": "premium",
    "stk": "steak",
    "chz": "cheese",
    "prod": "product",
    "pc": "piece",
    "pltr": "platter",
    "btr": "batter",
    "btrd": "battered",
    "ult": "ultimate",
    "knr": "Knorr",
    "frt": "fruit",
    "tndr": "tender",
    "fr": "fried",
    "chx": "chicken",
    "brd": "bread",
    "rt": "root",
    "ct": "count",
    "charbroilr": "charbroiler",
    "alum": "aluminum",
    "lg": "large",
    "sml": "small",
    "clr": "clear",
    "hng": "hinged",
    "sftsrv": "softserve",
    "cke": "cake",
    "gldn": "golden",
    "crm": "cream",
    "muf": "muffin",
    "muff": "muffin",
    "dinr": "dinner",
    "dnr": "dinner",
    "rnd": "round",
    "mesquie": "mesquite",
    "dzn": "dozen",
    "hndl": "handle",
    "mozz": "mozzarella",
    "hvy": "heavy",
    "chem": "chemical",
    "corp": "corporation",
    "ntrl": "natural",
    "bisc": "biscuits",
    "ketc": "ketchup",
    "upsdwn": "upside down",
    "bev": "beverage",
    "clsc": "classic",
    "vrty": "variety",
    "drk": "dark",
    "hdl": "handle",
    "sft": "soft",
    "assem": "assembly",
    "mnt": "mount",
    "qrt": "quart",
    "crakers": "crackers",
    "ter": "teriyaki",
    "sa": "sauce",
    "pstl": "pastel",
    "choc": "chocolate",
    "ast": "assorted",
    "nab": "Nabisco",
    "chp": "chip",
    "cooki": "cookie",
    "ckie": "cookie",
    "crkr": "cracker",
    "oatml": "oatmeal",
    "rainbw": "rainbow",
    "cntry": "country",
    "chky": "chunky",
    "gld": "gold",
    "ital": "italian",
    "lt": "lite",
    "smk": "Smucker's",
    "thou": "thousand",
    "blk": "black",
    "fm": "foam",
    "aspgus": "asparagus",
    "cabb": "cabbage",
    "chipotel": "chipotle",
    "mushrm": "mushroom",
    "jalape": "jalepeno",
    "gls": "glass",
    "r. bristol": "Royal Bristol",
    "r.bristol": "Royal Bristol",
    "dess": "dessert",
    "knf": "knife",
    "spn": "spoon",
    "tiss": "tissue",
    "astd": "assorted",
    "sauc": "sauce",
    "frnk": "frank",
    "swt": "sweet",
    "prpl": "purple",
    "sgr": "sugar",
    "mngo": "mango",
    "bisqu": "bisque",
    "mincd": "minced",
    "grnd": "ground",
    "flr": "floor",
    "bwl": "bowl",
    "ltr": "liter",
    "olv": "olive",
    "gal": "gallon",
    "shrd": "shredded",
    "chs": "cheese",
    "prov": "provalone",
    "ched": "cheddar",
    "frch": "french",
    "vnlla": "vanilla",
    "tableclth": "tablecloth",
    "tablecovr": "tablecover",
    "tblcvr": "tablecover",
    "plst": "plastic",
    "chipolt": "chipotle",
    "chptle": "chipotle",
    "prty": "party",
    "cutlry": "cutlery",
    "dlux": "deluxe",
    "pmkn": "pumpkin",
    "amer": "american",
    "grgzla": "gorgonzola",
    "clnr": "cleaner"
}


def apply(product_name):
    name_pieces = product_name.lower().split()
    for abbrv, word in abbrv_mapping.items():
        if abbrv in name_pieces:
            name_pieces[name_pieces.index(abbrv)] = word
    product_name = " ".join(name_pieces)

    for regex_rule in regex_rules:
        product_name = regex_rule.apply(product_name)

    return product_name.title()