from __future__ import annotations

from typing import Dict, List, Optional


# Family paths are ordered from macrofamily to branch. Keep concise and practical.
# Not exhaustive; variants with region/script (e.g., pt-BR, sr-Latn) should resolve by base code.

CODE_TO_FAMILY_PATH: Dict[str, List[str]] = {
    # Indo-European → Germanic
    "en": ["Indo-European", "Germanic", "West Germanic"],
    "de": ["Indo-European", "Germanic", "West Germanic"],
    "nl": ["Indo-European", "Germanic", "West Germanic"],
    "af": ["Indo-European", "Germanic", "West Germanic"],
    "fy": ["Indo-European", "Germanic", "West Germanic"],
    "sco": ["Indo-European", "Germanic", "West Germanic"],
    "is": ["Indo-European", "Germanic", "North Germanic"],
    "no": ["Indo-European", "Germanic", "North Germanic"],
    "nb": ["Indo-European", "Germanic", "North Germanic"],
    "nn": ["Indo-European", "Germanic", "North Germanic"],
    "sv": ["Indo-European", "Germanic", "North Germanic"],
    "da": ["Indo-European", "Germanic", "North Germanic"],

    # Indo-European → Romance
    "es": ["Indo-European", "Romance"],
    "fr": ["Indo-European", "Romance"],
    "it": ["Indo-European", "Romance"],
    "pt": ["Indo-European", "Romance"],
    "ro": ["Indo-European", "Romance"],
    "ca": ["Indo-European", "Romance"],
    "gl": ["Indo-European", "Romance"],
    "oc": ["Indo-European", "Romance"],
    "rm": ["Indo-European", "Romance"],
    "co": ["Indo-European", "Romance"],
    "sc": ["Indo-European", "Romance"],
    "scn": ["Indo-European", "Romance"],
    "fur": ["Indo-European", "Romance"],
    "lad": ["Indo-European", "Romance"],

    # Indo-European → Slavic
    "ru": ["Indo-European", "Slavic", "East Slavic"],
    "uk": ["Indo-European", "Slavic", "East Slavic"],
    "be": ["Indo-European", "Slavic", "East Slavic"],
    "bg": ["Indo-European", "Slavic", "South Slavic"],
    "mk": ["Indo-European", "Slavic", "South Slavic"],
    "sr": ["Indo-European", "Slavic", "South Slavic"],
    "hr": ["Indo-European", "Slavic", "South Slavic"],
    "bs": ["Indo-European", "Slavic", "South Slavic"],
    "sl": ["Indo-European", "Slavic", "South Slavic"],
    "sk": ["Indo-European", "Slavic", "West Slavic"],
    "cs": ["Indo-European", "Slavic", "West Slavic"],
    "pl": ["Indo-European", "Slavic", "West Slavic"],
    "sh": ["Indo-European", "Slavic", "South Slavic"],

    # Indo-European → Hellenic / Albanian / Armenian / Baltic / Celtic
    "el": ["Indo-European", "Hellenic"],
    "sq": ["Indo-European", "Albanian"],
    "hy": ["Indo-European", "Armenian"],
    "lt": ["Indo-European", "Baltic"],
    "lv": ["Indo-European", "Baltic"],
    "ltg": ["Indo-European", "Baltic"],
    "ga": ["Indo-European", "Celtic", "Goidelic"],
    "gd": ["Indo-European", "Celtic", "Goidelic"],
    "br": ["Indo-European", "Celtic", "Brythonic"],
    "cy": ["Indo-European", "Celtic", "Brythonic"],
    "kw": ["Indo-European", "Celtic", "Brythonic"],
    "gv": ["Indo-European", "Celtic", "Goidelic"],

    # Indo-European → Indo-Aryan / Iranian
    "hi": ["Indo-European", "Indo-Aryan"],
    "bn": ["Indo-European", "Indo-Aryan"],
    "pa": ["Indo-European", "Indo-Aryan"],
    "ur": ["Indo-European", "Indo-Aryan"],
    "sd": ["Indo-European", "Indo-Aryan"],
    "as": ["Indo-European", "Indo-Aryan"],
    "mr": ["Indo-European", "Indo-Aryan"],
    "gu": ["Indo-European", "Indo-Aryan"],
    "or": ["Indo-European", "Indo-Aryan"],
    "ne": ["Indo-European", "Indo-Aryan"],
    "si": ["Indo-European", "Indo-Aryan"],
    "mai": ["Indo-European", "Indo-Aryan"],
    "bho": ["Indo-European", "Indo-Aryan"],
    "mag": ["Indo-European", "Indo-Aryan"],
    "awa": ["Indo-European", "Indo-Aryan"],
    "hne": ["Indo-European", "Indo-Aryan"],
    "gom": ["Indo-European", "Indo-Aryan"],
    "doi": ["Indo-European", "Indo-Aryan"],
    "sa": ["Indo-European", "Indo-Aryan"],
    "sat": ["Austroasiatic", "Munda"],

    "fa": ["Indo-European", "Iranian"],
    "prs": ["Indo-European", "Iranian"],
    "ps": ["Indo-European", "Iranian"],
    "tg": ["Indo-European", "Iranian"],
    "ku": ["Indo-European", "Iranian"],
    "ckb": ["Indo-European", "Iranian"],

    # Uralic
    "fi": ["Uralic", "Finnic"],
    "et": ["Uralic", "Finnic"],
    "hu": ["Uralic", "Ugric"],

    # Turkic
    "tr": ["Turkic", "Oghuz"],
    "az": ["Turkic", "Oghuz"],
    "kk": ["Turkic", "Kipchak"],
    "ky": ["Turkic", "Kipchak"],
    "uz": ["Turkic", "Karluk"],
    "tk": ["Turkic", "Oghuz"],
    "ug": ["Turkic", "Karluk"],

    # Sino-Tibetan
    "zh": ["Sino-Tibetan", "Sinitic"],
    "yue": ["Sino-Tibetan", "Sinitic"],
    "hak": ["Sino-Tibetan", "Sinitic"],
    "nan": ["Sino-Tibetan", "Sinitic"],
    "wuu": ["Sino-Tibetan", "Sinitic"],
    "gan": ["Sino-Tibetan", "Sinitic"],
    "bo": ["Sino-Tibetan", "Tibetic"],
    "dz": ["Sino-Tibetan", "Tibetic"],
    "brx": ["Sino-Tibetan", "Bodo-Garo"],

    # Japonic / Koreanic
    "ja": ["Japonic"],
    "ko": ["Koreanic"],

    # Dravidian
    "ta": ["Dravidian", "Southern"],
    "te": ["Dravidian", "South-Central"],
    "kn": ["Dravidian", "Southern"],
    "ml": ["Dravidian", "Southern"],

    # Austroasiatic
    "vi": ["Austroasiatic", "Vietic"],
    "km": ["Austroasiatic", "Khmeric"],

    # Austronesian
    "id": ["Austronesian", "Malayo-Polynesian"],
    "ms": ["Austronesian", "Malayo-Polynesian"],
    "jv": ["Austronesian", "Malayo-Polynesian"],
    "su": ["Austronesian", "Malayo-Polynesian"],
    "fil": ["Austronesian", "Malayo-Polynesian"],
    "tl": ["Austronesian", "Malayo-Polynesian"],
    "to": ["Austronesian", "Polynesian"],
    "sm": ["Austronesian", "Polynesian"],
    "mi": ["Austronesian", "Polynesian"],
    "fj": ["Austronesian", "Melanesian"],
    "ty": ["Austronesian", "Polynesian"],
    "mg": ["Austronesian", "Malayo-Polynesian"],

    # Tai-Kadai
    "th": ["Tai-Kadai", "Tai"],
    "lo": ["Tai-Kadai", "Tai"],
    "tts": ["Tai-Kadai", "Tai"],

    # Afro-Asiatic (Semitic, Berber, Cushitic)
    "ar": ["Afro-Asiatic", "Semitic"],
    "he": ["Afro-Asiatic", "Semitic"],
    "am": ["Afro-Asiatic", "Semitic"],
    "ti": ["Afro-Asiatic", "Semitic"],
    "mt": ["Afro-Asiatic", "Semitic"],
    "kab": ["Afro-Asiatic", "Berber"],
    "tzm": ["Afro-Asiatic", "Berber"],
    "so": ["Afro-Asiatic", "Cushitic"],
    "om": ["Afro-Asiatic", "Cushitic"],

    # Niger–Congo (incl. Atlantic-Congo)
    "sw": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "zu": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "xh": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "st": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "tn": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "ts": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "ve": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "nr": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "nd": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "sn": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "rw": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "rn": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "ln": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "kg": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "lg": ["Niger–Congo", "Atlantic–Congo", "Bantu"],
    "ak": ["Niger–Congo", "Atlantic–Congo", "Kwa"],
    "tw": ["Niger–Congo", "Atlantic–Congo", "Kwa"],
    "ee": ["Niger–Congo", "Atlantic–Congo", "Kwa"],
    "wo": ["Niger–Congo", "Atlantic–Congo", "Senegambian"],
    "ff": ["Niger–Congo", "Atlantic–Congo", "Atlantic"],
    "fuc": ["Niger–Congo", "Atlantic–Congo", "Atlantic"],
    "bm": ["Niger–Congo", "Mande"],
    "mnk": ["Niger–Congo", "Mande"],
    "sg": ["Niger–Congo", "Ubangian"],
    "ig": ["Niger–Congo", "Volta–Niger"],
    "yo": ["Niger–Congo", "Volta–Niger"],

    # Caucasian and others
    "ka": ["Kartvelian"],
    "ab": ["Northwest Caucasian"],
    "ce": ["Northeast Caucasian"],
    "av": ["Northeast Caucasian"],
    "kbd": ["Northwest Caucasian"],
    "os": ["Iranian", "Ossetic"],  # Indo-European Iranian branch

    # Siberian / Steppe
    "ba": ["Turkic", "Kipchak"],
    "tt": ["Turkic", "Kipchak"],
    "udm": ["Uralic", "Permic"],
    "cv": ["Turkic"],

    # Constructed / Creole / Isolate
    "eo": ["Constructed"],
    "io": ["Constructed"],
    "ia": ["Constructed"],
    "tpi": ["Creole", "English-based"],
    "bi": ["Creole", "English-based"],
    "pis": ["Creole", "English-based"],
    "eu": ["Language isolate"],

    # American indigenous language families
    "ay": ["Aymaran"],
    "qu": ["Quechuan"],
    "gn": ["Tupian"],
    "arn": ["Araucanian"],
    "nah": ["Uto-Aztecan"],
    "nv": ["Na-Dene", "Athabaskan"],
    "chr": ["Iroquoian"],
    "cr": ["Algic", "Algonquian"],
    "iu": ["Eskimo–Aleut"],
    "kl": ["Eskimo–Aleut"],

    # Others
    "el-poly": ["Indo-European", "Hellenic"],
}


def family_path_for_code(code: str) -> Optional[List[str]]:
    base = code.split("-")[0].lower()
    return CODE_TO_FAMILY_PATH.get(base) or CODE_TO_FAMILY_PATH.get(code.lower())


