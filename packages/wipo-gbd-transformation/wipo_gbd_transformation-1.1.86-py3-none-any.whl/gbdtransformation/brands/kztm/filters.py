import datetime
import re

from . import countries

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def translate_kind(patent_type):
    if patent_type == 'Коллективный товарный знак': return 'Collective'
    else: return 'Individual'


def translate_feature(doc):
    patent_type = (doc.patent_type or '').strip()
    if patent_type == 'Движущийся товарный знак': return 'Motion'
    if patent_type == 'Звуковой товарный знак': return 'Sound'
    if patent_type == 'Позиционный товарный знак': return 'Position'
    if patent_type == 'Товарный знак голографический': return 'Hologram'
    else:
        has_word = doc.trademark_name_ru  or doc.trademark_name_en or doc.trademark_name_kz
        has_image = doc.image == 'yes'
        if has_word and has_image: return 'Combined'
        if has_word: return 'Word'
        if has_image: return 'Figurative'

    return 'Undefined'

# -------------------------------------------------------------
def deduce_status(edate):
    if not edate: return 'Ended'

    today = datetime.datetime.today().strftime('%Y-%m-%d')

    if today > edate: return 'Expired'
    else: return 'Registered'

def get_color_names(colors_claimed):
    if not colors_claimed: return []

    if not isinstance(colors_claimed, list):
        colors_claimed = [colors_claimed]

    color_names = []
    for  cc in colors_claimed:
        color_names.append(cc.color)

    return color_names

def get_vienna_codes(vclasses):
    if not vclasses: return []

    if not isinstance(vclasses, list):
        vclasses = [vclasses]

    codes = []
    for  vclass in vclasses:
        code = vclass.class_number
        if len(code.split('.')) == 3:
            codes.append(code)

    return codes

def get_goods_services(list_goods_services):
    if not list_goods_services: return

    nc = list_goods_services['class'] or []
    gs = list_goods_services['list'] or []

    if not isinstance(nc, list): nc = [nc]
    if not isinstance(gs, list): gs = [gs]

    # if not len(nc) == len(gs) and len(gs) > 0:
    #     raise Exception('attention to goods n services')

    nc_gs = {}
    nc_gs['00'] = [] # holder for nonclassified

    nbmatch = len(nc) == len(gs)
    for i,code in enumerate(nc):
        nc_gs[code] = []

    for i,line in enumerate(gs):
        if not line: continue
        terms = [l.strip() for l in line.split(';')]
        #32 класса - безалкогольные напитки;
        matches = re.findall(r'^0?(\d+) класса - (.*)', line)
        if len(matches):
            # split the class number and the rest of the line
            (cls, line) = matches[0]
            nc_gs.setdefault(cls, [])
            nc_gs[cls] += terms
        else:
            #02
            matches = re.findall(r'^0?(\d+)$', line)
            if len(matches):
                cls = matches[0]
                nc_gs.setdefault(cls, [])
            elif nbmatch:
                nc_gs[nc[i]] += terms
            else:
                nc_gs['00'] += terms
    return nc_gs

def parse_persons(inid_7_0):
    if not inid_7_0: return []

    if not isinstance(inid_7_0, list): inid_7_0 = [inid_7_0]

    persons = []
    for record in inid_7_0:
        if not record: continue
        person = {'address': record['address']}
        name = record.name or ''
        matches = re.findall(r'^(.*)\(([A-Z]{2})\)$', name)
        if len(matches):
            (person['name'], person['country']) = matches[0]
        else:
            person['name'] = name
            person['country'] = country_name2code(record.country)
        persons.append(person)

    return persons

def country_name2code(name):
    if not name:
        return None

    name = name.strip().lower()
    for code, country in countries.items():
        if isinstance(country, list):
            for syn in country:
                if syn.lower() == name:
                    return code
        else:
            if country.lower() == name:
                return code
    raise Exception('[%s] country name is not mapped' % name)
