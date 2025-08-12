# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):
    if not kind: return ['Individual']

    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Unknown'

    if status == 'ENREGISTREE': return 'Registered'
    if status == 'PUBLIEE': return 'Registered'

    raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature, treademark):
    # majority of records. bof.
    if not feature: return 'Undefined'

    if feature == 'Dénominative': return 'Word'
    if feature == 'dénominatif': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'figuratif': return 'Figurative'
    if feature == 'Mixte': return 'Combined'
    if feature == 'mixte': return 'Combined'
    if feature == 'sonore': return 'Sound'
    if feature == 'tridimensionnel': return 'Three dimensional'
    if feature == 'Tridimensionnelle': return 'Three dimensional'
    if feature == 'Autres': return 'Other'

    raise Exception('Feature "%s" unmapped' % feature)
