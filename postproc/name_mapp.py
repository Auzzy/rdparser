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

'''
7-up club pack of 12 oz cans
7-up upside down soda - 20oz/591ml plastic b7upls 24
'''
regex_rules_map = {
    "3 piece food storage system w/drain.*": "3 piece food storage system w/drain",
    "*hers reeses topin - hershey pack 6 reeses peanut butter natural  4.5 pound 6 in a case": "Reese's peanut butter",
    # "1950 brand"
    # 1950 brand part skim mozzarella cheese - 1950 brand mozzarella cheese part skim r/w average 24lb
    # 1950 cheese r/w white cheddar
    "4c (?P<item>.*?) (?P<size>\d+ ?qt) (?P<case>\d+ in a case)": "4c {item} - {size} {case}",
    "4c iced tea (?P<flavor>[^-]+) (?P<size>\d+ ?qt) (?P<case>\d+ in a case)": "4c iced tea - {flavor} - {size} {case}",
    "4c (?P<item>[^-]*) - 4c (?P<case>\d+ in a case)": "4c {item} - {case}",
    "knorr (?P<item>.*?) - (?:knorr)?(?P<desc>.*?) (?:\d )?(?P<volume>[\d.]+ lb )?(?P<case>\d+ in a case)": "knorr {item} - {volume} - {case}",
    "knorr (?P<item>.*?) (?:\d/[\w.#]+? )?(?P<volume>[\d.]+lb )?(?P<case>\d+ in a case)": "knorr {item} - {volume} - {case}",
    "nabisco (?P<item>.*?)\s+(?P<count>\d+ct)(?P<case> \d+ in a case)?": "",
    "nabisco (?P<item>.*?)(?P<size>[\d.]+(?:z|oz)?)? - (?:nabisco )?(?P<desc>.*?) (?P<volume>\d+ ?ounce )?(?P<case>\d+ in a case)": "nabisco {item} - {volume} - {case}",
}


abbrv_mapping = {
    "clubpk": "clubpack",
    "med": "medium",
    "veg": "vegetable",
    "ultima": "ultimate",
    "lobst": "lobster",
    "ultmte": "ultimate",
    "topin": "topping",
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
    "knr": "knorr",
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
    "smk": "smucker's",
    "thou": "thousand",
    "blk": "black",
    "fm": "foam",
    "aspgus": "asparagus",
    "cabb": "cabbage",
    "chipotel": "chipotle",
    "mushrm": "mushroom",
    "jalape": "jalepeno",
    "gls": "glass",
    "r. bristol": "royal bristol",
    "r.bristol": "royal bristol",
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
    "clnr": "cleaner",
    "plte": "plate",
    "ckn": "chicken",
    "flvr": "flavor",
    "chickn": "chicken",
    "bse": "base",
    "ckies": "cookies",
    "dispensr": "dispenser"
}


regex_rules = [RegexRule(regex, name_pattern) for regex, name_pattern in regex_rules_map.items()]


def apply(product_name):
    name_pieces = product_name.lower().split()
    for abbrv, word in abbrv_mapping.items():
        if abbrv in name_pieces:
            name_pieces[name_pieces.index(abbrv)] = word
    product_name = " ".join(name_pieces)

    for regex_rule in regex_rules:
        product_name = regex_rule.apply(product_name)

    return product_name.title()