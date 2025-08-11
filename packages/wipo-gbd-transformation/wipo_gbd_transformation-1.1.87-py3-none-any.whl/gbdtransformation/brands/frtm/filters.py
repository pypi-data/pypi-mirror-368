import datetime

ignore_namespace = [
   'http://www.inpi.fr/schemas/frst66/v1_00_11',
   'http://www.inpi.fr/schemas/frst66/v1_00_12',
   'http://www.inpi.fr/schemas/frst66/v1_00_13'
]

def translate_kind(kind):
    if not kind: return ['Individual']

    kind = kind.lower()
    if kind == 'collective de certification': return ['Certificate', 'Collective']
    if kind == 'collective': return ['Collective']
    if kind == 'guarantee': return ['Certificate']
    if kind == 'other': return ['Other']
    if kind == 'marque collective de certification': return ['Certificate', 'Collective']

    raise Exception('"%s" kind not mapped' % kind)

def translate_status(trademark):
    if trademark._operationCode == 'Delete':
        return 'Delete'

    status = trademark.MarkCurrentStatusCode
    status = status.lower()

    if status == "marque renouvelée": return "Registered"
    if status == "renouvellement demandé": return "Registered"
    if status == "marque enregistrée": return "Registered"

    if status == "marque expirée": return "Expired"
    if status == "marque ayant fait l'objet d'une renonciation totale": return "Expired"

    if status == "marque annulée": return "Ended"
    if status == "marque déchue": return "Ended"
    if status == "demande totalement rejetée": return "Ended"
    if status == "demande irrecevable après publication": return "Ended"
    if status == "marque ayant fait l'objet d'un retrait total": return "Ended"

    if status == "demande publiée": return "Pending"
    if status == "demande non publiée": return "Pending"
    if status == "demande déposée": return "Pending"

    raise Exception('"%s" status not mapped' % status)

def translate_feature(feature):
    # needed information from office
    if not feature: return 'Undefined'

    if feature == 'Word': return 'Word'
    if feature == 'Figurative': return 'Figurative'
    if feature == 'Combined': return 'Combined'
    if feature == '3-D': return 'Three dimensional'
    if feature == 'Form': return 'Three dimensional'
    if feature == 'Hologram': return 'Hologram'
    if feature == 'Sound': return 'Sound'
    if feature == 'Colour': return 'Colour'
    if feature == 'Position': return 'Position'
    if feature == 'Pattern': return 'Pattern'
    if feature == 'Motion': return 'Motion'
    if feature == 'Multimedia': return 'Multimedia'
    if feature == 'Other': return 'Other'

    raise Exception('"%s" feature not mapped' % feature)

# -------------------------
# handling dates exceptions
# -------------------------

# registration number = application number
# in case the record has an Enregistrement recordal
def get_registration_number(trademark):
    registeration_recordal = _get_registered_recordal(trademark)
    if registeration_recordal:
        return trademark.get('ApplicationNumber')

# registration date = date of Enregistrement recordal
def get_registration_date(trademark):
    registeration_recordal = _get_registered_recordal(trademark)

    return _get_recordal_date(registeration_recordal)

def get_publication_date(trademark):
    publication_recordal = _get_publication_recordal(trademark)

    return _get_recordal_date(publication_recordal)

def get_status_date(trademark):
    recordals = _get_recordals(trademark)
    if not len(recordals):
        return None

    # the last recordal is the latest
    return _get_recordal_date(recordals[-1].get('BasicRecord'))

def _get_recordal_date(recordal):
    if not recordal:
        return None

    pubdetails = recordal.get('RecordPublicationDetails', {}) \
                         .get('RecordPublication', {})

    pub_date = pubdetails.get('PublicationDate', None)

    # if no PublicationDate or it is malformed
    #   Ex: 3735098: 'PublicationDate': '2020-10-'
    # => fall back to PublicationIdentifier
    if pub_date and len(pub_date) < len('yyyy-mm-dd'):
        # sometimes only the Identifier is provided (yyyy-ww)
        # => deduce the date (friday of the week)
        return _weeknb_to_date(pubdetails.get('PublicationIdentifier'))
    else:
        return pub_date



# get the Enregistrement recordal
def _get_registered_recordal(trademark):
    recordals = _get_recordals(trademark)
    for record in recordals:
        brecord = record.get('BasicRecord', {})
        brecordKind = brecord.get('BasicRecordKind', None)
        if brecordKind and brecordKind.startswith('Enregistrement'):
            return brecord

    return None

# get the Publication recordal
def _get_publication_recordal(trademark):
    recordals = _get_recordals(trademark)
    for record in recordals:
        brecord = record.get('BasicRecord', {})
        brecordKind = brecord.get('BasicRecordKind', None)
        if brecordKind and brecordKind.startswith('Publication'):
            return brecord

    return None

def _get_recordals(trademark):
    recordals = trademark.get('MarkRecordDetails', {}).get('MarkRecord', [])
    if not isinstance(recordals, list):
        recordals = [recordals]

    recordals = [r for r in recordals if r is not None]

    return recordals


# ------------
# helpers
# ------------
# doing our best attempt
def _weeknb_to_date(weeknb):
    try:
        friday = datetime.datetime.strptime(weeknb + '-5', '%G-%V-%u')
        return friday.strftime('%Y-%m-%d')
    except:
        return None


def get_full_address(address):
    if not address:
        return None

    details = [address.AddressStreet, address.AddressPostOfficeBox, address.AddressPostcode, address.AddressCity]
    details = [d for d in details if d]
    line = ', '.join(details)
    if line:
        return line
    else:
        return None
