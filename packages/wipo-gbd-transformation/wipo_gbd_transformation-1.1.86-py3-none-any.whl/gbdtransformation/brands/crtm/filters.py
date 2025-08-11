import re
import gbdtransformation.brands.ipas.filters as ipas

ignore_namespace = [
   'http://www.wipo.int/standards/XMLSchema/trademarks',
   'http://www.wipo.int/standards/XMLSchema/wo-trademarks']

def get_appdate(appdate, appnum):
    return appnum[:appnum.find('-')]

def translate_type(header):
    code = header.TransactionCode
    subcode = header.TransactionSubCode

    if subcode == 'Emblema': return 'EMBLEM'
    if subcode == 'Denominación de origen': return 'AO'
    if subcode == 'Indicaciones geográficas': return 'GI'

    if code == 'Signo Distintivo': return 'TRADEMARK'

    raise Exception('Type "%s" is not mapped.' % code)

def translate_kind(trademark, header):
    code = header.TransactionCode
    subcode = header.TransactionSubCode.lower()

    if subcode == 'marca colectiva': return ['Collective']
    if subcode == 'marca de certificación': return ['Certificate']

    if subcode == 'señal de propaganda': return ['Slogan']

    if subcode == 'denominación de origen': return ['Other']
    if subcode == 'emblema': return ['Emblem']
    if subcode == 'indicaciones geográficas': return ['Other']

    if code == 'Signo Distintivo': return ['Individual']

    raise Exception('Kind "%s" not mapped.' % subcode)

def translate_status(trademark):
    status = trademark.MarkCurrentStatusCode

    status_map = {
        'Con plazo de gracia antes de caducidad': 'Registered',
        'Registered': 'Registered',
        'Registrada': 'Registered',
        'Con edicto publicado': 'Pending',
        'Con edicto para acumular': 'Pending',
        'Con edicto': 'Pending',
        'Con prevención (en examen)': 'Pending',
        'Con prevención (en inscripción)': 'Pending',
        'Con prevencion (en inscripción)': 'Pending',
        'Con prevención (en oposición)': 'Pending',
        'Con resolución de archivo': 'Pending',
        'Con resolución denegatoria': 'Pending',
        'Con resolución de oposición con lugar parcialmente': 'Pending',
        'Con resolución de oposición con lugar': 'Pending',
        'Con resolución de oposición sin lugar': 'Pending',
        'Con suspención de oficio': 'Pending',
        'Con suspensión de oficio (en examen)': 'Pending',
        'Con suspensión de oficio (en inscripción)': 'Pending',
        'Con suspensión de oficio (en oposición)': 'Pending',
        'Con gestoría de negocios': 'Pending',
        'Con prevención (para traslado)': 'Pending',
        'Con prevención de admisibilidad': 'Pending',
        'Con resolución denegatoria parcial': 'Pending',
        'Con suspenso a pedido de parte': 'Pending',
        'Denegada parcialmente': 'Pending',
        'Dividida': 'Pending',
        'En análisis de resolución anulada': 'Pending',
        'En examen': 'Pending',
        'En inscripción': 'Pending',
        'En oposición (con traslado)': 'Pending',
        'En oposición (examen fondo)': 'Pending',
        'En oposición (para traslado)': 'Pending',
        'Historia: anulada resol. reg. por tribunal': 'Pending',
        'Historia: con prevención': 'Pending',
        'Historia: con prevención art.14': 'Pending',
        'Historia: con suspenso': 'Pending',
        'Historia: continua trámite luego revoc/apel': 'Pending',
        'Historia: expediente con resolución': 'Pending',
        'Historia: pendiente de pago': 'Pending',
        'Historia: solicitud con edicto': 'Pending',
        'Historia: Edicto publicado': 'Pending',
        'Historia: En Tribunal': 'Pending',
        'Para abandonar por no publicación': 'Pending',
        'Para Denegar': 'Pending',
        'Para desistir': 'Pending',
        'Para repartir (oposición no recibida)': 'Pending',
        'Para repartir (oposición recibida)': 'Pending',
        'Para repartir (suspenso en exam.oposic finalizado)': 'Pending',
        'Para repartir (suspenso en inscripción finalizado)': 'Pending',
        'Para repartir': 'Pending',
        'Para repartir (edicto no publicado)': 'Pending',
        'Para repartir (nueva marca)': 'Pending',
        'Para repartir (suspenso en examen finalizado)': 'Pending',
        'Para validar rechazo de plano (historia)': 'Pending',
        'Status inicial': 'Pending',
        'Plazo vencido (edicto)': 'Pending',
        'Plazo vencido (gracia caducidad)': 'Pending',
        'Plazo vencido (oposiciones)': 'Pending',
        'Plazo vencido (suspenso a pedido de parte)': 'Pending',
        'Resolución oposición para firma': 'Pending',
        'Abandoned': 'Ended',
        'Anulada': 'Ended',
        'Archivada': 'Ended',
        'Cancelada': 'Ended',
        'Cancelado por error de recepción': 'Ended',
        'Denegada': 'Ended',
        'Desistida': 'Ended',
        'Historia: Status especial en Fox': 'Ended',
        'Historia: desistida por no pago': 'Ended',
        'Invalidated': 'Ended',
        'Rechazada': 'Ended',
        'Rechazada (historia)': 'Ended',
        'Rejected': 'Ended',
        'Withdrawn': 'Ended',
        'Expired': 'Expired'
    }

    return status_map.get(status, 'Unknown')

def translate_feature(trademark):
    feature = trademark.MarkFeature

    # test if name says it's a 3-D
    try:
        # safe assumption that  only one language will be present
        # when it's 3-D
        name = trademark.WordMarkSpecification.MarkVerbalElementText.__value.lower()
        if name == 'figura tridimensional': return 'Three dimensional'
        if name == 'diseño tridimensional': return 'Three dimensional'
        if name == 'marca tridimensional': return 'Three dimensional'
    except: pass

    if feature == 'M' or feature == 'Mixta': return 'Combined'
    if feature == 'F' or feature == 'Figurativa': return 'Figurative'
    if feature == 'D' or feature == 'Denominativa': return 'Word'
    if feature == 'T' or feature == 'Tridimensional': return 'Three dimensional'
    if feature == 'S' or feature == 'Sonora': return 'Sound'
    if feature == 'O' or feature == 'Olfativa': return 'Olfactory'

    return ipas.translate_feature(feature)

def translate_event(event):
    return 'Unknown'

# ---------------------------------------

def verbal_lang_map(markVerbalElements, applang=None):
    langmap = ipas.verbal_lang_map(markVerbalElements, applang=applang)

    if not len(list(langmap.keys())): return ''

    lang = 'es'
    if not lang in langmap.keys():
        lang = list(langmap.keys())[0]

    name = langmap.get(lang)[0]

    if name.lower() == 'figura tridimensional': return ''
    if name.lower() == 'diseño tridimensional': return ''
    if name.lower() == 'marca tridimensional': return ''

    # clean the spanish name
    name = re.sub(r"\s?\(dise(ñ|n)o\)\W*$", '', name, flags=re.IGNORECASE) # kueski (diseño)
    name = re.sub(r"^diseño especial$", '', name, flags=re.IGNORECASE) # "diseño especial"
    name = re.sub(r"^diseño$", '', name, flags=re.IGNORECASE) # "diseño"

    langmap[lang] = [name]

    return ipas.verbal_lang_map(markVerbalElements, applang=applang)

def get_registration_nb(trademark, tmstatus):
    if trademark.RegistrationNumber:
        return trademark.RegistrationNumber

    # no way to decude regnum from appnum
    return None

def get_expiry_date(trademark, tmstatus):
    return ipas.get_expiry_date(trademark, tmstatus)

def get_registration_date(trademark, tmstatus):
    return ipas.get_registration_date(trademark, tmstatus)

# no international for CR
def is_international(header):
    return False

def get_goods_services(goods_services):
    return ipas.get_goods_services(goods_services)

# never accessed
def get_ir_refnum(appnum):
    return
