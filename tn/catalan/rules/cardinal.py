# Copyright (c) 2024
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pynini import cross, string_file, union
from pynini.lib.pynutil import delete, insert

from tn.processor import Processor
from tn.utils import get_abs_path


class Cardinal(Processor):

    def __init__(self):
        super().__init__("cardinal")
        self.number = None
        self.build_tagger()
        self.build_verbalizer()

    def build_tagger(self):
        zero = string_file(get_abs_path("catalan/data/number/zero.tsv"))
        digit = string_file(get_abs_path("catalan/data/number/digit.tsv"))
        teen = string_file(get_abs_path("catalan/data/number/teen.tsv"))
        tens = string_file(get_abs_path("catalan/data/number/tens.tsv"))  # 3-9 only
        sign = string_file(get_abs_path("catalan/data/number/sign.tsv"))
        dot = string_file(get_abs_path("catalan/data/number/dot.tsv"))

        digits = zero | digit
        # Non-zero digit for units
        nz_digit = digit
        # Non-one digit for multi-hundred/thousand (2-9)
        digit_2_9 = (
            cross("2", "dos") | cross("3", "tres") | cross("4", "quatre") |
            cross("5", "cinc") | cross("6", "sis") | cross("7", "set") |
            cross("8", "vuit") | cross("9", "nou")
        )

        # Single digit: 0-9
        one_digit = digits

        # 10-19: direct lookup from teen file
        # 20: vint
        twenty_exact = cross("20", "vint")
        # 21-29: vint-i-un, vint-i-dos, etc.
        twenty_compound = cross("2", "vint-i-") + nz_digit
        # 30, 40, ..., 90
        thirty_plus_exact = tens + cross("0", "")
        # 31-39, 41-49, ..., 91-99
        thirty_plus_compound = tens + insert("-") + nz_digit

        two_digit = teen | twenty_exact | twenty_compound | thirty_plus_exact | thirty_plus_compound

        # 100: cent (special case for exactly 100)
        hundred_exact = cross("100", "cent")
        # 101-109: cent un, cent dos, etc.
        hundred_0X = cross("10", "cent ") + nz_digit
        # 110-199: cent deu, cent onze, cent vint-i-un, etc.
        hundred_XX = cross("1", "cent ") + two_digit
        # 200, 300, ..., 900 (using digit_2_9 to avoid matching 100)
        multi_hundred_exact = digit_2_9 + cross("00", "-cents")
        # 201-209, 301-309, etc.
        multi_hundred_0X = digit_2_9 + cross("0", "-cents ") + nz_digit
        # 210-299, 310-399, etc.
        multi_hundred_XX = digit_2_9 + insert("-cents ") + two_digit

        three_digit = (
            hundred_exact | hundred_0X | hundred_XX |
            multi_hundred_exact | multi_hundred_0X | multi_hundred_XX
        )

        # 1000: mil (special case, no "un")
        thousand_exact = cross("1000", "mil")
        # 1001-1009: mil un, mil dos, etc.
        thousand_00X = cross("100", "mil ") + nz_digit
        # 1010-1099: mil deu, mil onze, etc.
        thousand_0XX = cross("10", "mil ") + two_digit
        # 1100-1999: mil cent, mil dos-cents, etc.
        thousand_XXX = cross("1", "mil ") + three_digit
        # 2000, 3000, ..., 9000 (using digit_2_9 to avoid matching 1000)
        multi_thousand_exact = digit_2_9 + cross("000", " mil")
        # 2001-2009, etc.
        multi_thousand_00X = digit_2_9 + cross("00", " mil ") + nz_digit
        # 2010-2099, etc.
        multi_thousand_0XX = digit_2_9 + cross("0", " mil ") + two_digit
        # 2100-9999
        multi_thousand_XXX = digit_2_9 + insert(" mil ") + three_digit

        four_digit = (
            thousand_exact | thousand_00X | thousand_0XX | thousand_XXX |
            multi_thousand_exact | multi_thousand_00X | multi_thousand_0XX | multi_thousand_XXX
        )

        # Build complete number
        number = one_digit | two_digit | three_digit | four_digit
        number = sign.ques + number + (dot + digits.plus).ques
        self.number = number

        # Percent
        percent = number + delete("%") + insert(" per cent")

        cardinal = number | percent

        tagger = insert('value: "') + cardinal + insert('"')
        self.tagger = self.add_tokens(tagger)
