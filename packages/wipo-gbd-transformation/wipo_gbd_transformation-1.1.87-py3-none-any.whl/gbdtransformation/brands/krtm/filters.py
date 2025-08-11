from gbdtransformation.brands.filters import st13 as std_st13

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = ['http://www.wipo.int/standards/XMLSchema/ST96/Trademark',
                    'http://www.wipo.int/standards/XMLSchema/ST96/Common',
                    'urn:kr:gov:doc:kipo:common',
                    'urn:kr:gov:doc:kipo:trademark']


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def get_appyear(appnum):
    return appnum[2:6]

def get_mark_names(word_mark_spec):
    verbal = word_mark_spec.MarkVerbalElementText
    signif = word_mark_spec.MarkSignificantVerbalElementText

    if not signif == verbal:
        return (verbal, signif)
    else:
        return (verbal, None)

def get_trademark_root(transaction):
    try:
        trademark = transaction.TrademarkBag.KRTrademark
        return (trademark, trademark)
    # division => header information are in DocumentRelated
    except:
        trademark = transaction.KRTrademarkDivisionBag.KRTrademarkDivision
        header = trademark.KRDocumentRelatedBag.KRDocumentRelated
        return (trademark, header)

def get_classification(goodsServices):
    nice_class = []
    domestic_class = []

    if not goodsServices: goodsServices = []

    if not isinstance(goodsServices, list):
        goodsServices = [goodsServices]

    for gs in goodsServices:
        if gs.ClassificationKindCode == 'Nice':
            nice_class.append(gs)
        elif gs.ClassificationKindCode == 'Domestic':
            domestic_class.append(gs)

    return (nice_class, domestic_class)

def translate_kind(kind):
    if not kind: return ['Individual']

    if kind == 'Individual mark': return ['Individual']
    if kind == 'Certification mark, also named Guarantee mark': return ['Certificate']
    if kind == 'Collective mark': return ['Collective']

    # raise Exception to recognize unmapped values
    raise Exception('Kind "%s" is not mapped.' % kind)

def translate_status(trademark):
    if trademark._operationCategory == 'Delete':
        return 'Delete'

    status = trademark.KRMarkCurrentStatusCode

    if not status: return 'Unknown'

    # Ended can also mean expired (bof)
    if status == 'Ended':
        if trademark.RegistrationNumber and trademark.ExpiryDate:
            return 'Expired'
        else:
            return 'Ended'

    if status == 'Registered': return 'Registered'
    if status == 'Application published': return 'Pending'
    if status == 'Application filed': return 'Pending'

    # raise Exception to recognize unmapped values
    raise Exception('status "%s" is not mapped.' % status)

#TODO
def translate_feature(trademark, status):
    try:
        feature = trademark.MarkRepresentation.KRMarkFeatureCategory
    except:
        feature = None

    if feature == '3D Mark': return 'Three dimensional'
    if feature == 'Color': return 'Colour'
    if feature == 'Combination of colors mark': return 'Colour'
    if feature == 'Motion mark': return 'Motion'
    if feature == 'Sound mark': return 'Sound'
    if feature == 'Stylized': return 'Stylized characters'
    if feature == 'Others': return 'Other'

    # otherwise, let's guess
    try:
        has_vienna = trademark.MarkRepresentation.MarkReproduction.MarkImageBag.MarkImage.MarkImageCategory.KRCategoryCodeBag is not None
    except:
        has_vienna = False

    try:
        has_image = trademark.MarkRepresentation.MarkReproduction.MarkImageBag.MarkImage is not None
    except:
        has_image = False

    try:
        has_word = trademark.MarkRepresentation.MarkReproduction.KRWordMarkSpecification.MarkVerbalElementText is not None
    except:
        has_word = False

    try:
        has_word_image = trademark.MarkRepresentation.MarkReproduction.KRWordMarkSpecification.ImageFileName is not None
    except:
        has_word_image = False

    if has_word and (has_image or has_word_image) and has_vienna: return 'Combined'
    if not has_word and (has_image or has_word_image) and has_vienna: return 'Figurative'
    if has_image and has_vienna: return 'Figurative'
    if not has_word and has_word_image: return 'Stylized characters'

    if has_word: return 'Word'

    # still cannot figure it out !
    return 'Undefined'
