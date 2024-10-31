'''
A wrapper of OCR Page as page engine.
'''

import logging
from .RawPage import RawPage
from ..image.ImagesExtractor import ImagesExtractor
from ..shape.Paths import Paths
from ..common.constants import FACTOR_A_HALF
from ..common.Element import Element
from ..common.share import (RectType, debug_plot)
from ..common.algorithm import get_area



class RawPageOCR(RawPage):

    def extract_raw_dict(self, **settings):
        raw_dict = {}
        if not self.page_engine: return raw_dict
        # OCRPage
        # get page size 
        w, h = self.page_engine.width, self.page_engine.height
        raw_dict.update({"width": w, "height": h})
        self.width, self.height = w, h

        #preprocessing layout elements 
        text_blocks = self._preprocess_text(**settings)
        return text_blocks


    def _preprocess_text(self, **settings):
        sort = settings.get("sort")
        raw = self.page_engine.get_text(
        )
        # raw['blocks'] = [{'number': 0, 'type': 0, 'bbox': (433.014404296875, 51.2666015625, 575.654296875, 89.514892578125), 'lines': [{...}, {...}, {...}, {...}, {...}]}...]
        # line : {'spans': [{...}], 'wmode': 0, 'dir': (1.0, 0.0), 'bbox': (491.9013977050781, 51.2666015625, 573.2503662109375, 63.52294921875)}
        # span : {'size': 9.0, 'flags': 16, 'font': 'OpenSans-Bold', 'color': 16777215, 'ascender': 1.06884765625, 'descender': -0.29296875, 'chars': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}], 'origin': (491.9013977050781, 60.88623046875), 'bbox': (491.9013977050781, 51.2666015625, 573.2503662109375, 63.52294921875)}
        # char : {'origin': (491.9013977050781, 60.88623046875), 'bbox': (491.9013977050781, 51.2666015625, 498.1108703613281, 63.52294921875), 'c': 'A'}
        
        text_blocks = raw.get('blocks', [])
        return text_blocks
