import re

REGEX_BARCODE = r"^(S[0-9]+.+\.)?([1-9][0-9]{8})$"


def validate_barcode(barcode):
    if not barcode:
        pkg_valid = None
        return pkg_valid
    matches = re.findall(REGEX_BARCODE, barcode)
    if matches:
        pkg_valid = matches[0][1]
    else:
        pkg_valid = None
    return pkg_valid
