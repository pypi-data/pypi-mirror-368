import gbdtransformation.brands.ipas.filters as ipas
import gbdtransformation.brands.filters as common

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return ipas.get_appdate(appdate, appnum)

def st13(appnum, office, **args):
    return common.st13(appnum, office)

def translate_type(header):
    code = header.TransactionCode

    # extraction missing info.
    if not code:
        # defaulting rather than failing...
        return 'TRADEMARK'
        #raise Exception('Incomplete Document Info')
    if code == 'Marca': return 'TRADEMARK'
    if code == 'Marca Madri': return 'TRADEMARK'
    """
    if code == 'National TradeMarks': return 'TRADEMARK'
    if code == 'Zimbabwe': return 'TRADEMARK'
    if code == 'Madrid': return 'TRADEMARK'
    if code == 'Banjul Protocol Marks': return 'TRADEMARK'
    """
    return 'TRADEMARK'
    #raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    subcode = header.TransactionSubCode
    if subcode == 'Marca de Produto': return ['Individual']
    if subcode == 'Marca de Serviço': return ['Individual']
    if subcode == 'Marca Genérica': return  ['Individual']
    if subcode == 'Marca de Produto/Serviço': return ['Individual']
    if subcode == 'Madri Produto/Serviço': return ['Individual']
    if subcode == 'Madri Coletiva': return ['Collective']
    if subcode == 'Marca Coletiva': return ['Collective']
    if subcode == 'Marca de Propaganda': return ['Individual']
    if subcode == 'Marca de Certificação': return ['Certificate']
    if subcode == 'Madri Certificação': return ['Certificate']
    """
    if subcode == 'Marca de Certificação': return ['Certificate']
    if subcode == 'Part A': return ['Individual']
    if subcode == 'Part B': return ['Individual']
    if subcode == 'Part C': return ['Individual']
    if subcode == 'Part D': return ['Individual']
    if subcode == 'National Trademarks': return ['Individual']
    if subcode == 'Madrid Protocol': return ['Individual']
    if subcode == 'Banjul Protocol Marks': return ['Individual']
    """
    return ['Undefined']
    #raise Exception('Kind "%s" not mapped.' % subcode)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode
    if status in ['Registrado']: return 'Registered'
    if status in ['Expirado']: return 'Expired'
    if status in ['Recorrido','Examinado', 'Publicado','Oposto', 'Pendente', 'Sub judice', 'Sobrestado']: return 'Pending'
    if status in ['Abandonado/arquivado', 'Depositado', 'Anulado','Indeferido']: return 'Ended'

    if status == 'Inativo':
        if trademark.ExpiryDate: return 'Expired'
        else: return 'Ended'

    if status == "662":
        # "Verificando o pagamento da concessão (encerrado o prazo extraordinário)"
        return "Pending"

    if status == "663":
        # ?
        return "Unknown"

    if status == "687":
        # "Designação de Madri aguardando processamento de DEATH CPN"
        return "Pending"

    #raise Exception('status "%s" not mapped.' % status)
    return ipas.translate_status(status)

def parseStatus(status):
    if status == 'Depositado': return "Filed"
    if status == 'Publicado': return "Published"
    if status == 'Oposto': return "Opposed"
    if status == 'Registrado': return "Registered"
    if status == 'Indeferido': return "Rejected"
    if status == 'Desistido': return "Withdrawn"
    if status == 'Recorrido': return "Appealed"
    if status == 'Sobrestado': return "Suspended"
    if status == 'Abandonado/arquivado': return "Abandoned"
    if status == 'Convertido': return "Converted"
    if status == 'Renunciado': return "Surrendered"
    if status == 'Anulado': return "Invalidated"
    if status == 'Sub judice': return "Awaiting Court Action"
    if status == 'Examinado': return "Examined"
    if status == 'Expirado': return "Expired"
    if status == 'Reinstado': return "Reinstated"
    if status == 'Inativo': return "Inactive"
    if status == 'Pendente': return "Pending"
    return status

def translate_feature(trademark):
    feature = trademark.MarkFeature

    if not feature: return 'Undefined'

    return ipas.translate_feature(feature)

def translate_event(event):
    return ipas.translate_event(event)

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

def is_international(header):
    code = header.TransactionCode
    return code == 'Madrid'

# IB/D/1/1020123
def get_ir_refnum(appnum):
    return appnum.split('/')[-1]

def parse_version(version):
    return None
def get_goods_services(goods_services, nice_only = True):
    nc_gs = {}  # classified
    if not goods_services:
        goods_services = []

    if not isinstance(goods_services, list):
        goods_services = [goods_services]

    for goods_service in goods_services:
        code = goods_service.ClassNumber
        if code and not code == '0' and (not nice_only and int(code) >= 110 or int(code) <= 45 and nice_only):
            nc_gs[code] = {}
            desc = goods_service.GoodsServicesDescription

            if hasattr(desc, '__value'):
                terms = desc.__value
            else:
                terms = desc

            if terms:
                nc_gs[code]['terms'] = terms
            else:
                continue

            if hasattr(desc, '_languageCode'):
                lang = desc._languageCode
                nc_gs[code]['lang'] = lang.lower()
    return nc_gs
