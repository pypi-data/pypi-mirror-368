import re
import os

def transform_name_address(entities, app_lang):
    names = {}
    cc = []
    if isinstance(entities, list):
        for entity in entities:
            for name in entity.get('fullName', []):
                names.setdefault(name.languageCode, [])
                names[name.languageCode].append(name.text)
            cc.append(entity.countryCode)

    return {'names': names, 'cc': cc}

def guess_image_name(appnum):
    appnum = appnum.replace('/', '').replace('-', '')
    return os.path.join(appnum.zfill(4)[-4:-2],
            appnum.zfill(4)[-2:],
            '%s.png' % appnum)

def transform_goods_services(gservices, app_lang):
    gs_terms = {}
    if isinstance(gservices, list):
        for gservice in gservices:
            gs_terms.setdefault(str(gservice.nice), {})
            if not gservice.terms:
                continue
            for language in gservice.terms.keys() or {}:
                terms = gservice.terms[language]
                for term in terms:
                    gs_terms[str(gservice.nice)].setdefault(language, [])
                    gs_terms[str(gservice.nice)][language].append(term)

    return gs_terms

def transform_unclassified_goods_services(gservice, app_lang):
    if not gservice: return {}

    gs_terms = {}
    for language in gservice.keys() or {}:
        terms = gservice[language]
        for term in terms:
            gs_terms.setdefault(language, [])
            gs_terms[language].append(term)

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
    else:
        return status[0:3].upper()
