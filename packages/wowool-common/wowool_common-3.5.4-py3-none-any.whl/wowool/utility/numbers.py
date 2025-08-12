from locale import atof, setlocale, LC_NUMERIC
import re

number_parts = re.compile("[\\.,]")


def unique(seq):
    retval = []
    for word in seq:
        if word not in retval:
            retval.append(word)
    return retval


def set_number_local(comma):
    if comma == ".":
        locale = "en_US.UTF-8"
        setlocale(LC_NUMERIC, locale)
        return locale
        # print('en_US.UTF-8')
    elif comma == ",":
        locale = "nl_BE.UTF-8"
        setlocale(LC_NUMERIC, locale)
        return locale


def digit_sep_to_comma(digit_sep):
    if digit_sep == ".":
        return ","
    return "."


def to_float(literal):
    sep_sequence = number_parts.findall(literal)
    sep_sequence = sep_sequence[-2:]
    if len(sep_sequence) == 2 and sep_sequence[0] == sep_sequence[1]:
        set_number_local(digit_sep_to_comma(sep_sequence[0]))
    else:
        separators = unique(sep_sequence)
        if separators:
            set_number_local(separators[-1])
    return atof(literal)
