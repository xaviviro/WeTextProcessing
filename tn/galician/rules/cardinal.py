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
        zero = string_file(get_abs_path("galician/data/number/zero.tsv"))
        digit = string_file(get_abs_path("galician/data/number/digit.tsv"))
        teen = string_file(get_abs_path("galician/data/number/teen.tsv"))
        tens = string_file(get_abs_path("galician/data/number/tens.tsv"))  # 3-9 only
        sign = string_file(get_abs_path("galician/data/number/sign.tsv"))
        dot = string_file(get_abs_path("galician/data/number/dot.tsv"))

        digits = zero | digit
        nz_digit = digit
        # Non-one digit for multi-hundred/thousand (2-9)
        digit_2_9 = (
            cross("2", "dous") | cross("3", "tres") | cross("4", "catro") |
            cross("5", "cinco") | cross("6", "seis") | cross("7", "sete") |
            cross("8", "oito") | cross("9", "nove")
        )

        # Single digit: 0-9
        one_digit = digits

        # 10-19: direct lookup from teen file
        # 20: vinte
        twenty_exact = cross("20", "vinte")
        # 21-29: vinte e un, vinte e dous, etc.
        twenty_compound = cross("2", "vinte e ") + nz_digit
        # 30, 40, ..., 90
        thirty_plus_exact = tens + cross("0", "")
        # 31-39, 41-49, ..., 91-99
        thirty_plus_compound = tens + insert(" e ") + nz_digit

        two_digit = teen | twenty_exact | twenty_compound | thirty_plus_exact | thirty_plus_compound

        # 100: cen (special case)
        hundred_exact = cross("100", "cen")
        # 101-109: cento un, cento dous, etc.
        hundred_0X = cross("10", "cento ") + nz_digit
        # 110-199: cento dez, cento once, cento vinte e un, etc.
        hundred_XX = cross("1", "cento ") + two_digit
        # 200, 300, ..., 900
        multi_hundred_exact = digit_2_9 + cross("00", "centos")
        # 201-209, 301-309, etc.
        multi_hundred_0X = digit_2_9 + cross("0", "centos ") + nz_digit
        # 210-299, 310-399, etc.
        multi_hundred_XX = digit_2_9 + insert("centos ") + two_digit

        three_digit = (
            hundred_exact | hundred_0X | hundred_XX |
            multi_hundred_exact | multi_hundred_0X | multi_hundred_XX
        )

        # 1000: mil
        thousand_exact = cross("1000", "mil")
        # 1001-1009: mil un, mil dous, etc.
        thousand_00X = cross("100", "mil ") + nz_digit
        # 1010-1099: mil dez, mil once, etc.
        thousand_0XX = cross("10", "mil ") + two_digit
        # 1100-1999: mil cen, mil douscentos, etc.
        thousand_XXX = cross("1", "mil ") + three_digit
        # 2000, 3000, ..., 9000
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
        percent = number + delete("%") + insert(" por cento")

        cardinal = number | percent

        tagger = insert('value: "') + cardinal + insert('"')
        self.tagger = self.add_tokens(tagger)
