# standard gbd definitions
from . import status_map

# namespaces defined in XML and to be ignored in procecssing
ignore_namespace = []

# WARNING: pypers is making a transformation of the original USPTO XML
# into a "compressed" format that changes in particula the names of tags
# for example <mark-drawing-code> becomes <drawCode>, so
# the USPTO documentation has to be "translated" to this weirdo intermediary
# format (why doing simple and readable? :)
# to see this "pypers" mapping: 
# https://git.wipo.int/projects/BDDS/repos/gbd_etl_pypers/browse/pypers/steps/fetch/extract/us/ustm-tags.xml

def translate_kind(flags):
    is_trademark           = flags[2] == '1'
    is_collective         = flags[3] == '1'
    is_service            = flags[4] == '1'
    is_service_collective = flags[5] == '1'
    is_membership_collective = flags[6] == '1'
    is_certificate        = flags[7] == '1'

    kind = []
    if is_trademark          : kind = [ 'Individual' ]
    if is_collective        : kind = [ 'Collective' ]
    if is_service           : kind = [ 'Individual' ]
    if is_service_collective: kind = [ 'Collective' ]
    if is_membership_collective : kind = [ 'Membership', 'Collective' ]
    if is_certificate       : kind = [ 'Certificate' ]

    if len(kind): 
        return kind
    else: 
        return ['Other']

def translate_status(status):
    """translation of mark status"""
    # a required data from office. if not present and no way to guess,
    # return Unknown
    if not status: 
        return 'Unknown'

    try:
        return status_map[status]
    except:
        return ['Unknown']
        #raise Exception('Status "%s" unmapped' % status)

def translate_feature(drawcode):
    if not drawcode: return 'Undefined'

    code = drawcode [0]
    # PL: '0' means "Mark drawing code not yet assigned"
    if code == '1': return 'Word' #1000
    if code == '2': return 'Figurative'
    if code == '3': return 'Combined'
    if code == '4': return 'Word' #4000
    if code == '5': return 'Stylized characters'
    # PL: the code '6'' was incorrectly mapped to 'Olfactory', 
    # Official documentation: '6' means "Where no drawing is possible, such as for sound", so it means "other".
    # Unfortunately until June 2025, everything was mapped to 'Olfactory', so sound or 3D trademarks are all
    # 'Olfactory' in GBD until this date
    if code == '6': return 'Other' #6000

    return ['Other']
    # note: documentation explains that mark-drawing-code is optional, so we don't want to raise an exception here
    #raise Exception('DrawCode "%s" unmapped' % drawcode)

def get_img_class(dessearches):
    if not dessearches: return None
    if not isinstance(dessearches, list):
        dessearches = [dessearches]

    codes = []
    for dessearch in dessearches:
        code = dessearch.code
        codes.append('.'.join([code[0:2], code[2:4], code[4:6]]))

    return codes

def get_goods_services(stmts):
    nc_gs = {} # classified
    uc_gs = [] # unclassified

    if not stmts:
        stmts = []

    if not isinstance(stmts, list):
        stmts = [stmts]

    for stmt in stmts:
        code = stmt.typeCode
        if code.startswith('GS'):
            nc = code[-3:-1]
            if nc == '00':
                uc_gs = [l.strip() for l in stmt.text.split(';')]
            else:
                nc_gs[nc] = [l.strip() for l in stmt.text.split(';')]

    return nc_gs, uc_gs

def get_mark_description(stmts):
    if not stmts: return {}
    if not isinstance(stmts, list):
        stmts = [stmts]

    desc = None
    for stmt in stmts:
        code = stmt.typeCode
        if code == 'DM0000':
            return stmt.text

def get_color_claim(stmts):
    if not stmts: return {}
    if not isinstance(stmts, list):
        stmts = [stmts]

    claim = None
    for stmt in stmts:
        code = stmt.typeCode
        if code == 'CC0000':
            return stmt.text

def get_related_docs(priors):
    if not priors: return ([], [])
    if not isinstance(priors, list):
        priors = [priors]

    relapps = []
    relregs = []

    for prior in priors:
        type = prior.relType
        if type == '0':
            relregs.append(prior.num)
        else:
            relapps.append(prior.num)

    return (relapps, relregs)

def get_correspondence(corr):
    if not corr: return

    correspondence = { 'name' : corr.add1 }
    adrlines = []
    i = 2
    while(corr['add%s' % i]):
        adrlines.append(corr['add%s' % i].replace(';', ''))
        i += 1
    correspondence['address'] = '; '.join(adrlines)

    return correspondence


def get_applicants(owners, status):
    if not owners: return []

    if not isinstance(owners, list):
        owners = [owners]
    # look for owners
    if status in ['Registered', 'Expired']:
        cdl = 20 # code low
        cdh = 30 # code high
    # look for applicants
    else:
        cdl = 10
        cdh = 20

    applicants = []
    for owner in owners:
        code = owner.partyType
        if cdl <= int(code) <= cdh:
            # get the address
            adrlines = []
            for i in range(1, 10):
                if(owner.get('add%s' % i)):
                    adrlines.append(owner['add%s' % i].replace(';', ''))

            address_str = ', '.join(adrlines)
            address_str = address_str.replace(",,", ",")
            if address_str.endswith(","):
                address_str = address_str[:-1]

            if len(address_str.strip()) == 0:
                address_str = None

            city = []
            city_str = None
            postCode_str = None
            if owner.postCode:
                city.append(owner.postCode)
                postCode_str = owner.postCode
            if owner.city:
                city.append(owner.city)
                city_str = owner.city

            if len(city):
                adrlines.append(' '.join(city))

            state_str = None
            if owner.state:
                adrlines.append(owner.state)
                state_str = owner.state

            address = '; '.join(adrlines)

            country = owner.country
            if not country and owner.state:
                country = 'US'

            applicants.append({
                'kind': 'Natural Person' if owner.entType == '01' else 'Legal Entity',
                'name': owner.partyName,
                'address': address,
                'country': country,
                'city': city_str,
                'postCode': postCode_str,
                'addressLines': address_str,
                'state': state_str
            })

    return applicants
