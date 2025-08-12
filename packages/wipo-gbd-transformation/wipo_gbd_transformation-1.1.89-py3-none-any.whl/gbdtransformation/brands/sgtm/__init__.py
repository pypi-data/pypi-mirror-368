# instruction to render the output to JSON format
render = 'JSON'
source = 'national'

# T0001800A
# T9511877G
# 40201711800X
# 40201711800X-01
# L.* # Slogan
# A.* # Emblem
appnum_mask = [ '40\\d{4}(\\d*[A-Z])',
                '40\\d{4}(\\d*[A-Z])-(\\d{2})',
                'T(\\d*)/?([A-Z])(.*)',
                '(L.*)',
                '(A.*)',
                '(T.*)' ]
