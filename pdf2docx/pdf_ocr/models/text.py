from dataclasses import dataclass
@dataclass
class OCRText:
    x: int
    y: int
    w: int
    h: int
    text: str


