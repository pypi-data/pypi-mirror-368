render = 'JSON'
source = 'national'

# CM/A/1/741838
# A/A/1/591810
# CU/M/1998/001838
# CU/R/2020/000129
appnum_mask = [ '([A-Z])/([A-Z])/\\d{1,4}/(\\d*)',
                'C(U|M)/([A-Z])/\\d{1,4}/(\\d*)',
                'CU/([A-Z])/\\d{4}/(\\d*)' ]
