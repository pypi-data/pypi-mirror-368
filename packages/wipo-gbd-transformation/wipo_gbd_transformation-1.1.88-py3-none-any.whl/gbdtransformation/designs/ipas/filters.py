# standard gdd definitions
from gbdtransformation.designs import kinds as std_kinds
from gbdtransformation.designs import status as std_status

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
        return [kind.capitalize()]

    # __insert here__ : translation logic

    # raise Exception to recognize unmapped values
    raise Exception('kind "%s" is not mapped.' % kind)

# Expired trademarks with no Expiry date
# => get it from Expired event
def get_expiry_date(design, idstatus):
    if design.ExpiryDate:
        return design.ExpiryDate

    if not idstatus == 'Expired':
        return None

    # find the MarkEvent Expired and get its date
    events = design.get('MarkEventDetails', {}).get('MarkEvent', [])
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if(event.MarkEventCode == 'Expired'):
                return event.MarkEventDate


# Registered or Expired trademarks with no registration date
# => get it from Registered or Published Event
def get_registration_date(trademark, tmstatus):
    if trademark.RegistrationDate:
        return trademark.RegistrationDate

    if not tmstatus in ['Expired', 'Registered']:
        return None

    # find the MarkEvent Expired and get its date
    events = trademark.get('MarkEventDetails', {}).get('MarkEvent', [])

    # first priority is to get the Registered Event
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if event.MarkEventCode == 'Registered':
                return event.MarkEventDate
    # second priority is to get the Published Event
    for event in events:
        if hasattr(event, 'MarkEventCode'):
            if event.MarkEventCode == 'Published':
                return event.MarkEventDate

# given a list of dates as strings, e.g. publication dates, deduplicate
def deduplicate_dates(dates):
    return list(set(dates))

# given a list of publications, deduplicate
def deduplicate_publication_dates(design):
    if design == None:
        return None
    dates = []
    if "PublicationDetails" in design:
        publicationDetails = design["PublicationDetails"]
        publications = publicationDetails.get('Publication', [])
        if not isinstance(publications, list): 
            publications = [publications]
        for publication in publications:
            if "PublicationDate" in publication:
                dates.append(publication["PublicationDate"])
    return deduplicate_dates(dates)

# given a list of classes, deduplicate
def deduplicate_classes(classes):
    deduplicate_classes = []
    if not isinstance(classes, list): 
        classes = [classes]
    for the_class in classes:
        if the_class["ClassNumber"] not in deduplicate_classes:
            deduplicate_classes.append(the_class["ClassNumber"])
    result = []
    for deduplicate_class in deduplicate_classes:
        result.append({ "code": deduplicate_class} )
    return result

# given a list of publications, deduplicate
def deduplicate_publications(publications):
    deduplicate_publications = []
    pub_keys = []
    if not isinstance(publications, list): 
        publications = [publications]
    for publication in publications:
        publication_date = publication.get("PublicationDate")
        publication_identifier = publication.get("PublicationIdentifier")
        pub_key = ""
        if publication_identifier:
            pub_key += publication_identifier
        if publication_date:
            pub_key += publication_date
        if pub_key not in pub_keys:
            deduplicate_publications.append(publication)
            pub_keys.append(pub_key)
    result = []
    for publication in deduplicate_publications:
        res = {}
        if "PublicationIdentifier" in publication:
            res["identifier"] = publication["PublicationIdentifier"]
        if "PublicationDate" in publication:
            res["date"] = publication["PublicationDate"]
        result.append(res)
    return result

# given a list of publications with dates as strings, select the earliest date publication
def select_earliest_date(design):
    if design == None:
        return None

    if "PublicationDetails" in design:
        publicationDetails = design["PublicationDetails"]
        publications = publicationDetails.get('Publication', [])
        if not isinstance(publications, list): 
            publications = [publications]
        if len(publications) == 0:
            return None
        elif len(publications) == 1:
            return publications[0]["PublicationDate"]
        else:
            earliest_date = None
            n = -1
            for count, publication in enumerate(publications):
                if earliest_date == None or publication["PublicationDate"] < earliest_date:
                    earliest_date = publication["PublicationDate"]
            return earliest_date
    else:
        return None

def translate_status(status):
    status = status.lower()

    if status == 'registered': return 'Registered'
    if status == 'active': return 'Registered'
    if status == 'reinstated': return 'Registered'
    if status == 'expired': return 'Expired'
    if status == 'inactive': return 'Expired'
    if status == 'published': return 'Pending'
    if status == 'examined': return 'Pending'
    if status == 'filed': return 'Pending'
    if status == 'converted': return 'Pending'
    if status == 'opposed': return 'Pending'
    if status == 'pending': return 'Pending'
    if status == 'appealed': return 'Pending'
    if status == 'awaiting court action': return 'Pending'
    if status == 'application published': return 'Pending'
    if status == 'abandoned': return 'Ended'
    if status == 'withdrawn': return 'Ended'
    if status == 'rejected': return 'Ended'
    if status == 'finalrefusal': return 'Ended'
    if status == 'suspended': return 'Ended'
    if status == 'invalidated': return 'Ended'
    if status == 'surrendered': return 'Ended'
    if status == 'suspended': return 'Ended'
    if status == 'renewed': return 'Registered'
    if status == 'renewalprocess': return 'Registered'
    if status == 'canceled': return 'Ended'
    if status == 'cancelled': return 'Ended'

    #return 'Unknown'
    raise Exception('Status "%s" not mapped.' % status)