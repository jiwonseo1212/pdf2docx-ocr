from dataclasses import dataclass
from .text import OCRText
@dataclass
class OCRPage:
    page: int
    width: float
    height: float
    ocr_result: list[OCRText]

    
    def scaling(self, box, width, height, target_size=1000):
        # Calculate scaling factors for both x and y axes
        x_scale = target_size / width
        y_scale = target_size / height

        
        # Loop through each bounding box and apply scaling
        x, y, w, h = box
        # Convert [x, y, w, h] to [left, top, right, bottom]
        left = x
        top = y
        right = x + w
        bottom = y + h

        # Scale the coordinates based on the x_scale and y_scale
        left_scaled = round(left * x_scale)
        top_scaled = round(top * y_scale)
        right_scaled = round(right * x_scale)
        bottom_scaled = round(bottom * y_scale)

        # Ensure the scaled coordinates are within bounds
        assert left_scaled <= right_scaled <= target_size and top_scaled <= bottom_scaled <= target_size
        return [left_scaled, top_scaled, right_scaled, bottom_scaled]

    def get_page_bbox(self, lines):
        small_x = min(list(map(lambda x : x['bbox'][0], lines)))
        small_y = min(list(map(lambda x : x["bbox"][1], lines)))
        max_x = max(list(map(lambda x : x['bbox'][2], lines)))
        max_y = max(list(map(lambda x : x["bbox"][3], lines)))
        return [small_x, small_y, max_x, max_y]


    def get_text(self,  tolerance_x=4, tolerance_y=4):
        """
        # raw['blocks'] = [{'number': 0, 'type': 0, 'bbox': (433.014404296875, 51.2666015625, 575.654296875, 89.514892578125), 'lines': [{...}, {...}, {...}, {...}, {...}]}...]
            # line : {'spans': [{...}], 'wmode': 0, 'dir': (1.0, 0.0), 'bbox': (491.9013977050781, 51.2666015625, 573.2503662109375, 63.52294921875)}
                # span : {'size': 9.0, 'flags': 16, 'font': 'OpenSans-Bold', 'color': 16777215, 'ascender': 1.06884765625, 'descender': -0.29296875, 'chars': [{...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}, {...}], 'origin': (491.9013977050781, 60.88623046875), 'bbox': (491.9013977050781, 51.2666015625, 573.2503662109375, 63.52294921875)}
                    # char : {'origin': (491.9013977050781, 60.88623046875), 'bbox': (491.9013977050781, 51.2666015625, 498.1108703613281, 63.52294921875), 'c': 'A'}        
        """

        raw = {}
        
        lines = []
        last_box = [0, 0, 0, 0]
        last_text = ""
        text_and_bbox = []
        for block in self.ocr_result:
            word, box = block.text, [block.x, block.y, block.w, block.h]
            box =  self.scaling(box, self.width, self.height)
            if (not box[2] >= box[0]) or (not box[3] >= box[1]):
                # skip invalid box
                continue
            if (
                (abs(box[1] - last_box[1]) < tolerance_x)
                and (abs(box[3] - last_box[3]) < tolerance_y)
                and box[0] >= last_box[2]
                and (box[0] - last_box[2])
                # < ((last_box[2] - last_box[0]) / max(len(last_text), 1))
            ):
                # merge box of the same line
                text_and_bbox.append(
                     {'origin': (box[0], box[3]), 
                      'bbox': box, 'c': word})
                last_box[2] = box[2]
                last_text += " " + word
                
            else:
                if last_text != "":
                    line_span = {'size': 10.0, 
                            'flags': 16, 
                            'font': 'ariel', 
                            'color': 16777215, 
                            'ascender': 1.06884765625, 
                            'descender': -0.29296875, 
                            'chars': [text_and_bbox], 
                            'origin': (491.9013977050781, 60.88623046875), 
                            'bbox': last_box}
                    line =  {'spans': [line_span], 
                             'wmode': 0, 
                             'dir': (1.0, 0.0), 
                             'bbox': last_box}
                    lines.append(line)
                    text_and_bbox = []


                # renew buffer
                last_box = box.copy()
                last_text = word


        if last_text != "":
            line_span = {'size': 10.0, 
                'flags': 16, 
                'font': 'ariel', 
                'color': 16777215, 
                'ascender': 1.06884765625, 
                'descender': -0.29296875, 
                'chars': [text_and_bbox], 
                'origin': (491.9013977050781, 60.88623046875), 
                'bbox': last_box}
            line =  {'spans': [line_span], 
                            'wmode': 0, 
                            'dir': (1.0, 0.0), 
                            'bbox': last_box}
            lines.append(line)
            text_and_bbox = []
        raw["blocks"] = [{'number': 0, 
                            'type': 0, 
                            'bbox': self.get_page_bbox(lines), 
                            'lines': [lines]}]
        return raw
