"""Normalize team names across datasets."""

ALIASES: dict[str, str] = {
    "Bosnia and Herzegovina": "Bosnia & Herzegovina",
    "Bosnia-Herzegovina": "Bosnia & Herzegovina",
    "Czechia": "Czech Republic",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Korea Republic": "South Korea",
    "Korea, Republic of": "South Korea",
    "Republic of Korea": "South Korea",
    "USA": "United States",
    "US": "United States",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Democratic Republic of the Congo": "DR Congo",
    "Cape Verde Islands": "Cape Verde",
    "Cabo Verde": "Cape Verde",
    "IR Iran": "Iran",
    "KSA": "Saudi Arabia",
    "UAE": "United Arab Emirates",
}


def normalize(name: str) -> str:
    name = name.strip()
    return ALIASES.get(name, name)
