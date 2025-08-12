ignore_namespace = []

def translate_status(status):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    if not status: return 'Unknown'

    if status == 'Recommended':
        return "Registered"
    else:
        return 'Pending'


def get_appnum(inn):
    appnum = ''
    if inn.get('recommended'):
        appnum += 'R' + inn.get('recommended').get('__value') + 'E' + inn.get('recommended').get('_entry')
    if inn.get('proposed'):
        appnum += 'P' + inn.get('proposed').get('__value') + 'E' + inn.get('proposed').get('_entry')
    return appnum


def get_status(inn):
    status = 'Proposed'
    if inn.get('recommended'):
        status = 'Recommended'
    return status

def get_languages(inn):
    to_return = []
    if not  inn.get('transliteration', None):
        return to_return
    for el in sorted(inn['transliteration'].keys()):
        if not inn['transliteration'][el]:
            continue
        to_return.append({
            'lang': el,
            'value': inn['transliteration'][el]
        })
    return to_return


def get_st13_INN(appnum):
    # QO: Organization without st13 code
    return 'QO82%s' % (appnum.zfill(13))
