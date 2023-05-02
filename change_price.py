# |  ₴ — hryvnia  |  $ — dollar  |  € — euro  |

def currency_sign(price_from_advertisement: str):
    """
    Taking string with full price: value and sign or currency.
    Returning the currency sign, which depends on text in price.
    |  ₴ — hryvnia  |  $ — dollar  |  € — euro  |
    :param price_from_advertisement:
    :return:
    """
    sign = '€' if price_from_advertisement.split()[-1] == '€' else \
        '$' if price_from_advertisement.split()[-1] == '$' else '₴'
    return sign


def to_int(full_price: str):
    if full_price.lower() == 'безкоштовно' or full_price.lower() == 'обмін':
        price = 0
    elif len(full_price.split()) == 2:
        price = int(full_price.split()[0])
    else:
        price = int(''.join((full_price.split()[:-1])))
    return price
