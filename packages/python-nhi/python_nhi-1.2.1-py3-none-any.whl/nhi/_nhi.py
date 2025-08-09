# Copyright 2025 NHI contributors
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import re
from operator import mul

_OLD_NHI_FORMAT_REGEX = re.compile(r"^[A-HJ-NP-Z]{3}\d{4}$")
_NEW_NHI_FORMAT_REGEX = re.compile(r"^[A-HJ-NP-Z]{3}\d{2}[A-HJ-NP-Z]{2}$")


def is_nhi(nhi: str) -> bool:
    """
    Checks a string against the New Zealand Ministry of Health NHI specification
    defined by HISO 10046:2023 and the NHI validation routine

    .. seealso::
        - https://www.tewhatuora.govt.nz/publications/hiso-100462023-consumer-health-identity-standard/

    :param nhi: A potential NHI string
    :return: True if the given string satisfies the New Zealand NHI Validation
        Routine and False otherwise
    """
    nhi = nhi.upper()
    if _NEW_NHI_FORMAT_REGEX.match(nhi):
        nhi_values = [_char_code(c) for c in nhi]
        checksum = sum(map(mul, nhi_values, range(7, 1, -1))) % 23
        check_digit = 23 - checksum
        return check_digit == nhi_values[-1]
    elif _OLD_NHI_FORMAT_REGEX.match(nhi):
        nhi_values = [_char_code(c) for c in nhi]
        checksum = sum(map(mul, nhi_values, range(7, 1, -1))) % 11
        check_digit = (11 - checksum) % 10
        return checksum != 0 and check_digit == nhi_values[-1]
    return False


def _char_code(c: str) -> int:
    if c.isdigit():
        return int(c)
    else:
        return ord(c) - ord('@') - ('I' < c) - ('O' < c)
