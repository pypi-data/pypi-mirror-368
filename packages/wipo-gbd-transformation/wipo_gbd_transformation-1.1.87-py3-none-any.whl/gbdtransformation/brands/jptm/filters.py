import unicodedata

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def parse_appnum(appnum):
    if len(appnum) > 4:
        return '%s-%s' % (appnum[:4], appnum[4:])
    else:
        return appnum

def get_verbal(wmspec):
    # first try markVerbalElement
    ve = wmspec.markVerbalElement
    if ve: return ve

    # fallback to markSignificantVerbalElement
    sve = wmspec.markSignificantVerbalElement
    if not sve: return

    if hasattr(sve, 'text'): sve = sve.text

    return ' '.join(sve) if isinstance(sve, list) else sve

def get_signif(wmspec):
    sve = wmspec.markSignificantVerbalElement
    if not sve: return

    if hasattr(sve, 'text'): sve = sve.text

    return ' '.join(sve) if isinstance(sve, list) else sve

def get_transliteration(wmspec):
    trans = wmspec.markTransliteration
    if not trans: return
    if not isinstance(trans, list):
        trans = [trans]
    return ' '.join(trans)

def try_to_8bit(value):
    return unicodedata.normalize('NFKC', value)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'Unknown': return 'Unknown'
    if status == 'Domestic registration': return 'Registered'
    if status == 'Domestic application': return 'Pending'
    if status == 'International registration': return 'Registered'
    if status == 'Domestic registration deletion case': return 'Expired'
    if status == 'Domestic application deletion case': return 'Ended'
    if status == 'International registration deletion case': return 'Expired'

    raise Exception('Status "%s" unmapped' % status)


def translate_feature(feature):
    if not feature: feature = 'Undefined'

    if feature == 'Colour': return 'Colour'
    if feature == 'Sound': return 'Sound'
    if feature == 'Motion': return 'Motion'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Position': return 'Position'
    if feature == 'Other': return 'Other'
    if feature == 'Three dimensional': return 'Three dimensional'

    # TODO look if has word or has figure
    if feature == 'Undefined': return 'Undefined'
    if feature == 'Not a special trademark': return 'Undefined'

    raise Exception('Feature "%s" unmapped' % feature)

