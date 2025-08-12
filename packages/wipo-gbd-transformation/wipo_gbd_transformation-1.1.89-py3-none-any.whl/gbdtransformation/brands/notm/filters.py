import re

def translate_kind(kind):
    if not kind: return 'Individual'

    if kind.lower() == 'individual mark': return 'Individual'
    if kind.lower() == 'trademark': return 'Individual'
    if kind.lower() == 'collective mark': return 'Collective'
    if kind.lower() == 'guarantee' or kind.lower() =='guarantee mark': return 'Collective'
    if kind.lower() == 'certificate' or kind.lower() =='certificate mark': return 'Certificate'
    if kind.lower() == 'certification' or kind.lower() =='certification mark': return 'Certificate'

    return 'Other'
    #raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(status):
    if not status: return 'Ended'

    if status in ['Registered',
                  'Granted']: 
        return 'Registered'

    if status in ['Pending']:
        return 'Pending'

    if status in ['Refused',
                  'Shelved',
                  'Finally shelved',
                  'Ceased',
                  'Ceased/cancelled',
                  'Withdrawn',
                  'Rejected']:
        return 'Ended'

    return 'Unknown'
    #raise Exception('Status "%s" unmapped' % status)

def translate_feature(feature):
    """translation of mark feature"""
    if not feature: return 'Undefined'
    feature = feature.upper()
    if feature == 'COMBINED/FIGURATIVE MARK': return 'Combined'
    if feature == 'FIGURATIVE MARK': return 'Figurative'
    if feature == 'WORD MARK': return 'Word'
    if feature == '3D-MARK': return "Three dimensional"
    if feature == '3D MARK': return "Three dimensional"
    if feature == 'SOUND MARK': return 'Sound'
    if feature == 'COLOR MARK': return 'Colour'
    if feature == 'MOTION MARK': return 'Motion'
    if feature == 'MULTIMEDIA MARK': return 'Multimedia'
    if feature == 'POSITION MARK': return 'Position'
    if feature == 'PATTERN MARK': return 'Pattern'
    if feature == 'HOLOGRAM MARK': return 'Hologram'
    if feature == 'TRACER MARK': return 'Tracer'
    if feature == 'OLFACTORY MARK': return 'Olfactory'
    if feature == 'OLFACTIVE MARK': return 'Olfactory'
    if feature == 'STYLIZED CHARACTERS': return 'Stylized characters'
    if feature == 'STYLIZED CHARACTERS MARK': return 'Stylized characters'

    return 'Unknown'

    # raise Exception to recognize unmapped values
    #raise Exception('Feature "%s" unmapped' % feature)

def get_local_text(node):
    if node is None:
        return None
    if "$" in node:
        return node["$"]

def get_local_texts(nodes):
    if nodes is None:
        return None
    text = ""
    start = True
    for node in nodes:
        if "$" in node:
            if start:
                start = False
            else:
                text += ", "
            text += node["$"]
    return text

def get_full_address(postalStructuredAddress):
    if postalStructuredAddress is None:
        return 
    result = ""
    if "addressLineText" in postalStructuredAddress:
        for addressLineText in postalStructuredAddress["addressLineText"]:
            # always empty, which is good
            """
            if hasattr(addressLineText, '__value'):
                if len(result) > 0:
                    result += ", "
                result += addressLineText.__value
            """
    if "cityName" in postalStructuredAddress:
        if len(result) > 0:
            result += ", "
        result += postalStructuredAddress["cityName"]
    if "countryCode" in postalStructuredAddress:
        result += ", " + postalStructuredAddress["countryCode"]
    if "postalCode" in postalStructuredAddress:
        result += " " + postalStructuredAddress["postalCode"]
    if len(result) == 0:
        return
    else: 
        return result.strip()

def local_guess_language(content):
    if content == None:
        return None
    from lingua import Language, LanguageDetectorBuilder
    detector = LanguageDetectorBuilder.from_all_spoken_languages().build()
    language = detector.detect_language_of(content)
    if language:
        lang = language.iso_code_639_1.name.lower()
        # we merge Norwegian flavors, Norwegian Bokmål and Norwegian Nynorsk 
        if lang == "nn" or lang =="nb":
            lang = "no"
        return lang
    else:
        return "en"

def has_vienna_classes(markImage):
    if not "markImageClassification" in markImage:
        return False
    if not "figurativeElementClassificationBag" in markImage["markImageClassification"]:
        return False
    if not "viennaClassificationBag" in markImage["markImageClassification"]["figurativeElementClassificationBag"]:
        return False

    for element in markImage["markImageClassification"]["figurativeElementClassificationBag"]["viennaClassificationBag"]:
        if "viennaClassification" in element:
            for viennaClassification in element["viennaClassification"]:
                if "viennaCategory" in viennaClassification:
                    return True
    return False

def translate_licence_category(kind):
    if not kind: return 'Other'

    if kind.lower() == 'exclusive': return 'Exclusive'
    if kind.lower() == 'nonexclusive' or kind.lower() == 'non exclusive' or kind.lower() == 'non-exclusive': return 'NonExclusive'

    return 'Other'
    #raise Exception('licence category "%s" is not mapped.' % kind)

def translate_licence_status(status):
    if not status: return 'Other'
    # Cancelled, Valid, Other

    if status.lower() == 'cancelled': return 'Cancelled'
    if status.lower() == 'valid': return 'Valid'

    return 'Other'
    #raise Exception('licence status "%s" is not mapped.' % status)

def clean_vienna_class(the_class):
    if the_class == None:
        return None
    if len(the_class) == 0:
        return None
    # remove trailing dot
    if the_class.endswith("."):
        the_class = the_class[:-1]
    if len(the_class) == 0:
        return None
    return the_class
