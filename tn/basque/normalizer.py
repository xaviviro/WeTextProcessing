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

from importlib_resources import files
from pynini.lib.pynutil import add_weight, delete

from tn.basque.rules.cardinal import Cardinal
from tn.basque.rules.char import Char
from tn.basque.rules.whitelist import Whitelist
from tn.processor import Processor


class Normalizer(Processor):

    def __init__(self, cache_dir=None, overwrite_cache=False):
        super().__init__(name="eu_normalizer")
        if cache_dir is None:
            cache_dir = files("tn")
        self.build_fst("eu_tn", cache_dir, overwrite_cache)

    def build_tagger(self):
        whitelist = add_weight(Whitelist().tagger, 1.01)
        cardinal = add_weight(Cardinal().tagger, 1.05)
        char = add_weight(Char().tagger, 100)

        tagger = (whitelist | cardinal | char).optimize()
        tagger = tagger.star
        self.tagger = tagger @ self.build_rule(delete(" "), r="[EOS]")

    def build_verbalizer(self):
        cardinal = Cardinal().verbalizer
        char = Char().verbalizer
        whitelist = Whitelist().verbalizer

        verbalizer = (cardinal | char | whitelist).optimize()
        self.verbalizer = verbalizer.star
