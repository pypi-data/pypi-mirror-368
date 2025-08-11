import math
from pandas import Series

def first(series):
    if isinstance(series, str) or isinstance(series, int) or isinstance(series, float):
        return series
    if series.empty:
        return None
    if len(series.to_list()) > 0:
        return series.to_list()[0]
    return None

def translate_kind(kind):
    if kind == '1': return 'Collective'
    return 'Individual'

jptm_rep_types = {
    "0": "No Representative",
    "1": "Representative",
    "2": "Acting representative",
    "3": "Designated representative",
    "4": "Legal representative",
}

jptm_status_country = {
    "1": "Domestic registration",  # LIVE registered?
    "2": "Domestic application",  # LIVE Pending ?
    "3": "International registration",  # LIVE Registered ?
    "A": "Domestic registration",  # DEAD Ended
    "B": "Domestic registration",  # DEAD Ended
    "C": "International registration",  # DEAD Ended
    "None": "Unknown"}


def representative_type(rep_typ_code):
    if isinstance(rep_typ_code, float) and math.isnan(rep_typ_code):
        return
    return jptm_rep_types[str(int(rep_typ_code))]


jptm_status_gbd = {
    "1": "Registered",
    "2": "Pending",  # ??
    "3": "Registered",
    "A": "Ended",  # ??
    "B": "Ended",  # ??
    "C": "Ended",  # ??
    "None": "Unknown"
}


def status_office(status):
    code = first(status)
    return jptm_status_country[str(code)]


def status_gbd(status):
    code = first(status)
    return jptm_status_gbd[str(code)]


features = {
    "0": "Not a special trademark",
    "1": "Three dimensional",
    "2": "Sound",
    "3": "Motion",
    "4": "Hologram",
    "5": "Colour",
    "6": "Position",
    "9": "Other",
    '': "Undefined" }

def make_feature(feature_code):
    # print("Make Feature [", feature_code, "]", type(feature_code))
    if feature_code is None:
        return 'Undefined'
    if isinstance(feature_code, bool):
        return 'Undefined'
    if isinstance(feature_code, Series) and feature_code.empty():
        return 'Undefined'
    if isinstance(feature_code, float) and math.isnan(feature_code):
        return 'Undefined'
    if isinstance(feature_code, float):
        feature_code = int(feature_code)

    return features[str(feature_code)]
