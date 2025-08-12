# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# B77380
# 3020200118182
# 395218187
# 303018186
# -- old file numbers
# ST17437
# SCH34883
# W15650D
appnum_mask = [ '30\\d{4}(\\d{7})',
                '([A-Z]\\d*)',
                '3\\d{2}(\\d{6})',
                '([A-Z]{2}\\d{6})',
                'DE30(\\d{4})(\\d{6})',
                'DE(.*)',
                '(.*)' ]
