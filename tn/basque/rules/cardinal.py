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
    """Basque cardinal numbers using vigesimal (base-20) system."""

    def __init__(self):
        super().__init__("cardinal")
        self.number = None
        self.build_tagger()
        self.build_verbalizer()

    def build_tagger(self):
        zero = string_file(get_abs_path("basque/data/number/zero.tsv"))
        digit = string_file(get_abs_path("basque/data/number/digit.tsv"))
        teen = string_file(get_abs_path("basque/data/number/teen.tsv"))
        twenties = string_file(get_abs_path("basque/data/number/twenties.tsv"))
        sign = string_file(get_abs_path("basque/data/number/sign.tsv"))
        dot = string_file(get_abs_path("basque/data/number/dot.tsv"))

        digits = zero | digit
        nz_digit = digit
        # Non-one digit for multi-hundred/thousand (2-9)
        digit_2_9 = (
            cross("2", "bi") | cross("3", "hiru") | cross("4", "lau") |
            cross("5", "bost") | cross("6", "sei") | cross("7", "zazpi") |
            cross("8", "zortzi") | cross("9", "bederatzi")
        )

        # Teens mapping for second digit (0-9 -> hamar, hamaika, etc.)
        # This maps the units digit to the teens words for vigesimal compounds
        teen_units = (
            cross("0", "hamar") | cross("1", "hamaika") | cross("2", "hamabi") |
            cross("3", "hamahiru") | cross("4", "hamalau") | cross("5", "hamabost") |
            cross("6", "hamasei") | cross("7", "hamazazpi") | cross("8", "hemezortzi") |
            cross("9", "hemeretzi")
        )

        # Single digit: 0-9
        one_digit = digits

        # 10-19: direct lookup from teen file
        # Vigesimal system:
        # 20: hogei, 40: berrogei, 60: hirurogei, 80: laurogei
        twenty_exact = twenties

        # 21-29: hogeita bat, hogeita bi, ...
        twenty_one_to_twenty_nine = cross("2", "hogeita ") + nz_digit
        # 30-39: hogeita hamar, hogeita hamaika, ...
        thirty_to_thirty_nine = cross("3", "hogeita ") + teen_units

        # 41-49: berrogeita bat, berrogeita bi, ...
        forty_one_to_forty_nine = cross("4", "berrogeita ") + nz_digit
        # 50-59: berrogeita hamar, berrogeita hamaika, ...
        fifty_to_fifty_nine = cross("5", "berrogeita ") + teen_units

        # 61-69: hirurogeita bat, hirurogeita bi, ...
        sixty_one_to_sixty_nine = cross("6", "hirurogeita ") + nz_digit
        # 70-79: hirurogeita hamar, hirurogeita hamaika, ...
        seventy_to_seventy_nine = cross("7", "hirurogeita ") + teen_units

        # 81-89: laurogeita bat, laurogeita bi, ...
        eighty_one_to_eighty_nine = cross("8", "laurogeita ") + nz_digit
        # 90-99: laurogeita hamar, laurogeita hamaika, ...
        ninety_to_ninety_nine = cross("9", "laurogeita ") + teen_units

        # Two digit numbers
        two_digit = (
            teen | twenty_exact |
            twenty_one_to_twenty_nine | thirty_to_thirty_nine |
            forty_one_to_forty_nine | fifty_to_fifty_nine |
            sixty_one_to_sixty_nine | seventy_to_seventy_nine |
            eighty_one_to_eighty_nine | ninety_to_ninety_nine
        )

        # 100: ehun
        hundred_exact = cross("100", "ehun")
        # 101-109: ehun eta bat, ehun eta bi, etc.
        hundred_0X = cross("10", "ehun eta ") + nz_digit
        # 110-199: ehun eta hamar, ehun eta hogeita bat, etc.
        hundred_XX = cross("1", "ehun eta ") + two_digit
        # 200, 300, ..., 900
        multi_hundred_exact = digit_2_9 + cross("00", " ehun")
        # 201-209, 301-309, etc.
        multi_hundred_0X = digit_2_9 + cross("0", " ehun eta ") + nz_digit
        # 210-299, 310-399, etc.
        multi_hundred_XX = digit_2_9 + insert(" ehun eta ") + two_digit

        three_digit = (
            hundred_exact | hundred_0X | hundred_XX |
            multi_hundred_exact | multi_hundred_0X | multi_hundred_XX
        )

        # 1000: mila
        thousand_exact = cross("1000", "mila")
        # 1001-1009: mila eta bat, mila eta bi, etc.
        thousand_00X = cross("100", "mila eta ") + nz_digit
        # 1010-1099: mila eta hamar, mila eta hogeita bat, etc.
        thousand_0XX = cross("10", "mila eta ") + two_digit
        # 1100-1999: mila ehun, mila bi ehun, etc.
        thousand_XXX = cross("1", "mila ") + three_digit
        # 2000, 3000, ..., 9000
        multi_thousand_exact = digit_2_9 + cross("000", " mila")
        # 2001-2009, etc.
        multi_thousand_00X = digit_2_9 + cross("00", " mila eta ") + nz_digit
        # 2010-2099, etc.
        multi_thousand_0XX = digit_2_9 + cross("0", " mila eta ") + two_digit
        # 2100-9999
        multi_thousand_XXX = digit_2_9 + insert(" mila ") + three_digit

        four_digit = (
            thousand_exact | thousand_00X | thousand_0XX | thousand_XXX |
            multi_thousand_exact | multi_thousand_00X | multi_thousand_0XX | multi_thousand_XXX
        )

        # Build complete number
        number = one_digit | two_digit | three_digit | four_digit
        number = sign.ques + number + (dot + digits.plus).ques
        self.number = number

        # Percent
        percent = number + delete("%") + insert(" ehuneko")

        cardinal = number | percent

        tagger = insert('value: "') + cardinal + insert('"')
        self.tagger = self.add_tokens(tagger)
