from pathlib import Path
from PIL import ImageFont

font_name = "Gidole-Regular.ttf"
font_path = str(Path(__file__).parent / font_name) 

small_font = ImageFont.truetype(font_path, size=10)
large_font = ImageFont.truetype(font_path, size=12)
