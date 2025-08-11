from gbdtransformation.common import countries

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []


def get_feature(doc):
    has_word = doc['PROTECTED_SIGN'].get('TEXT', None) is not None
    has_image = doc['PROTECTED_SIGN'].get('IMAGE', None) is not None

    if has_word and has_image: return 'Combined'
    if has_image: return 'Figurative'
    if has_word: return 'Word'

    raise Exception('Undetected feature')

def translate_kind(kind):
    if kind.lower().replace('_', ' ') == 'armorial bearings': return 'Armorial bearings'
    if kind.lower().replace('_', ' ') == 'flag': return 'Flag'
    if kind.lower().replace('_', ' ') == 'state emblem': return 'State emblem'
    if kind.lower().replace('_', ' ') == 'emblem': return 'Emblem'
    if kind.lower().replace('_', ' ') == 'official sign': return 'Official sign'
    if kind.lower().replace('_', ' ') == 'abbreviation': return 'Abbreviation'
    if kind.lower().replace('_', ' ') == 'name': return 'Name'

    raise Exception('kind "%s" is not mapped.' % kind.lower().replace('_', ' '))

def get_coutry_name(code):
    country_name = countries.get(code, None)
    if not country_name:
        raise Exception('Country code %s not mapped' % state)
    if isinstance(country_name, list):
        country_name = country_name[0]
    return country_name

def get_status_and_date(sixter):
    status = "Registered"
    gbd_status = "Registered"
    status_date = None
    if sixter.STATUS:
        status = sixter.STATUS.TEXT.lower().capitalize()
        if status == 'Withdrawn':
            gbd_status = 'Ended'
        else:
            raise Exception('Status %s not mapped' % status)

        data = sixter.STATUS.DATE
        if data:
            status_date = "%s-%s-%s" % (data[0:4], data[4:6], data[6:])
    return status, gbd_status, status_date

def st13_sixter(sixter):
    # remove special characters
    appdate = sixter['_DATE']
    appnum = sixter['_NUMBER']
    if not appnum:
        raise Exception("No appnumber provided")
    if not appdate:
        appdate = '0000'
    office = sixter.STATE_ORG or 'WO'
    return 'WO80%s%s%s' % (appdate[:4], office.upper(), appnum.zfill(7))

def get_addr(addr):
    vals = [addr.ADDRESS, addr.CITY, addr.ZIP]
    vals = [ v for v in vals if v ]
    return ', '.join(vals)

def sanitize_text(text):
    try: text = text.__value
    except: pass

    if text:
        text = text.replace('"', '')
    return text

def split_vienna(data):
   return '%s.%s.%s' % (data[0:2], data[2:4], data[4:])

def reg_number(sixter):
    # remove special characters
    appnum = sixter.get('_NUMBER', '0')
    office = sixter.STATE_ORG or 'QO'
    return '%s%s' % (office.upper(), appnum)

def to_link(value):
    if value:
        return 'https://6ter.wipo.int/pdf/en/e' + value + '.pdf'
    return None