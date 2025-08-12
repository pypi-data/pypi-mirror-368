# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# 1501818-00
# 1501818-01 # only retain version when it is
             # different that 00
appnum_mask = [ '(\\d*)-00',
                '(\\d*)-(\\d{2})',
                '(\\d*)$']
