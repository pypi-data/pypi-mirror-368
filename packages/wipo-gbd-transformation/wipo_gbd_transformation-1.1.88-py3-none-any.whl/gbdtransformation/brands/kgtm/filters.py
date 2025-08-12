# standard gbd definitions
from datetime import datetime

from gbdtransformation.brands import kinds as std_kinds
from gbdtransformation.brands import status as std_status
from gbdtransformation.brands import features as std_features
from gbdtransformation.brands import events as std_events

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []


# -------------------------------------------------------------
# data translation helpers:
# translate values from office interpretation to gbd equivalent
# -------------------------------------------------------------

def translate_kind(kind):
    """translation of the kind of trademark to a
        multivalue gbd interpretation"""

    # out-of-the-box match
    if kind.capitalize() in std_kinds:
        return kind.capitalize()

    # __insert here__ : translation logic

    # raise Exception to recognize unmapped values
    raise Exception('kind "%s" is not mapped.' % kind)

def translate_status(expiryDate):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    if not expiryDate: return 'Unknown'

    if datetime.now().strftime('%Y-%m-%d') > expiryDate:
        return "Expired"
    else:
        return 'Registered'


map_feature = {
    'Словесный': 'Word',
    'Изобразительный': 'Figurative',
    'Комбинированный': 'Combined',
    'Объемный':  'Three dimensional'
}

def translate_feature(feature):
    """translation of mark feature"""

    # needed information from office
    # if office cannot provide information, then agree on a way to guess (uatm)
    if not feature: return 'Undefined'

    # out-of-the-box match
    if feature.capitalize() in std_features:
        return feature.capitalize()

    translated_feature = map_feature.get(feature, None)
    if translated_feature:
        return translated_feature

    # raise Exception to recognize unmapped values
    raise Exception('Feature "%s" unmapped' % feature)

