import itertools


def get_mod_eleven_digit(string) -> str:
    """Module to get digit"""
    facts = itertools.cycle((2, 3, 4, 5, 6, 7, 8, 9))
    sum_all = sum(int(digit) * f for digit, f in zip(reversed(string), facts))
    # get the module 11 of entire access_key
    control = sum_all % 11
    digit = ""
    if control == 11:
        digit = str(0)
    if control == 10:
        digit = str(1)
    if control < 10:
        digit = str(control)

    return digit[0] if len(digit) > 1 else digit


def parse_integer_string_to_base16(string_number):
    int_cuf_code = int(string_number)
    hexadecimal_format = format(int_cuf_code, "X")
    return hexadecimal_format


def parse_base16_to_integer_string(hexadecimal_string):
    int_cuf_code = int(hexadecimal_string, 16)
    return str(int_cuf_code)
