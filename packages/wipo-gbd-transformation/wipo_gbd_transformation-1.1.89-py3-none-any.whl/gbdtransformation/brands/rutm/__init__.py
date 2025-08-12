# instruction to render the output to JSON format
render = 'JSON'
source = 'national'


# 201302148
# 95711885
# 141807
# 76833А
# warning, above it is cyrillic capital letter a, not Latin one !
appnum_mask = [ '\\d{4}(\\d{6})',
                '\\d{2}(\\d{6})',
                '(\\d*А?)'
                ]
