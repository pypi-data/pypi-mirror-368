import re

def transform_name_address(entities, app_lang):
    names = {}
    cc = []
    lang = ''
    if isinstance(entities, list):
        for entity in entities:
            for name in entity.get('fullName', []):
                suffix = name.languageCode if name.languageCode else ''
                names.setdefault(suffix, [])
                names[suffix].append(name.text)
            cc.append(entity.countryCode)

    return {'names': names, 'cc': cc}

def sanitize_name(name):
    return re.sub('[.,"\'\(\)]', '', name or '').upper()

def transform_goods_services(gservices):
    gs_terms = {}
    if not gservices: return gs_terms
    if not isinstance(gservices, list):
        gservices = [gservices]

    for gservice in gservices:
        gs_terms.setdefault(str(gservice.code), {})
        if not gservice.terms:
            continue
        for language in gservice.terms.keys() or {}:
            terms = gservice.terms[language]
            for term in terms:
                gs_terms[str(gservice.code)].setdefault(language, [])
                gs_terms[str(gservice.code)][language].append(term)

    return gs_terms

def merge_national_unclassified_goods_services(ngservices, ugservices):
    for nclass in ngservices.keys():
        n = ngservices[nclass]
        for lang in n.keys():
            ugservices.setdefault(lang, [])
            ugservices[lang] += n[lang]
    return(ugservices)

def transform_unclassified_goods_services(gservices):
    gs_terms = {}
    if not gservices: return gs_terms

    if not isinstance(gservices, list):
        gservices = [gservices]

    for gservice in gservices:
        for lang in gservice.keys():
            gs_terms[lang] = gservice[lang]

    return gs_terms

def filter_events(events):
    events_names = []
    if isinstance(events, list):
        for event in events:
            events_names.append(event.gbdKind)

    return set(events_names)

# if combined, then image type has Word and Device
def get_image_type(mark_feature):
    if mark_feature == 'Combined':
        return ['Word', 'Device']
    if mark_feature == 'Figurative':
        return ['Device']

    return [mark_feature]

# only top 2 for classification
# might be useful for faceting
def cl_top2(classes):
    return ['.'.join(c.split('.')[:2]) for c in classes]

def validate_status(status):
    if status not in ['Ended', 'Expired', 'Registered', 'Pending', 'Unknown']:
         raise Exception('Invalid Status: %s' % status)

    return status
