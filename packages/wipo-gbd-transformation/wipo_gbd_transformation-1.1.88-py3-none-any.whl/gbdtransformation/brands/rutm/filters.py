# namespaces defined in XML and to be ignored during processing
ignore_namespace = [
    'http://www.wipo.int/standards/XMLSchema/ST96/Common',
    'http://www.wipo.int/standards/XMLSchema/ST96/Trademark',
    'urn:ru:rupto:trademark',
    'http://www1.fips.ru/standards/XMLSchema/Publication/TM/96/ST96Schema_TM_V1_6/RUTrademark/Document/TrademarkTransaction.xsd'
]

# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------
def translate_kind(kind):

    if kind == 'Trademark': return ['Individual']
    if kind == 'Collective trademark': return ['Collective']
    if kind == 'Certification mark': return ['Certificate']

    raise Exception('kind "%s" is not mapped.' % kind)

def get_path(path, data):
    if not path:
        return data
    tmp_path = path.split('.')
    if '[' in tmp_path[0]:
        if isinstance(data, list):
            nb = tmp_path[0].split('[')[1][:-1]
            return get_path('.'.join(tmp_path[1:]), data[nb])
        else:
            return get_path('.'.join(tmp_path[1:]), data[tmp_path[0].split('[')[0]])
    if isinstance(data, dict):
        if tmp_path[0] in data.keys():
            return get_path('.'.join(tmp_path[1:]), data[tmp_path[0]])


def get_trademark(data):
    if data.TrademarkBag:
        trademark = data.TrademarkBag.Trademark
        status = 'Registered'
        if get_path('MarkRecordBag.MarkRecord[-1].BasicRecord.BasicRecordKind', trademark) == 'Non Renewal':
            et_path('MarkRepresentation.MarkReproduction.MarkImageBag.MarkImage.ImageFileName', trademark)
            print("expired for %s" % trademark.ApplicationNumber.ApplicationNumberText)
            status = 'Expired'
        return trademark, status
    if data.TradeMarkApplication:
        status = 'Pending'
        return data.TradeMarkApplication.TradeMarkDetails.TradeMark, status

def get_termination(value, gbd_status):
    if gbd_status == 'Ended':
        return value
    return None

def translate_feature(trademark):
    feature = get_path('MarkRepresentation.MarkFeatureCategory',
                        trademark)
    if feature == None: return 'Undefined'

    if feature == 'Three dimensional': return 'Three dimensional'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Colour': return 'Colour'
    if feature == 'Sound': return 'Sound'
    if feature == 'Olfactory': return 'Olfactory'
    if feature == 'Motion': return 'Motion'

    # positional is not a feature considered or observed so far in any collections
    if feature == 'Positional': return 'Other'

    # the office wild card. bof
    if feature == 'Other': return 'Other'

    has_word = get_path('MarkRepresentation.MarkReproduction.WordMarkSpecification.MarkSignificantVerbalElementText',
                        trademark)
    has_figure = get_path('MarkRepresentation.MarkReproduction.MarkImageBag.MarkImage.ImageFileName', trademark)
    if has_word and has_figure:
        return 'Combined'
    elif has_word:
        return 'Word'
    elif has_figure:
        return 'Figurative'

    raise Exception('Feature "%s" unmapped' % feature)
