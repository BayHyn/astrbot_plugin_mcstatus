from astrbot.api import logger
from PIL import Image, ImageDraw, ImageFont
import os

class Draw:
    def __init__(self):
        self.output = "data/whitecloudcn_plugins_data/draw_temp.jpg"
        pass

    def create_image_with_text(self,
                               text: str,
                               background_path: str = "data/plugins/astrbot_plugin_mcstatus/assess/bg.jpg",
                               output_path: str = "data/whitecloudcn_plugins_data/draw_temp.jpg"):
        try:
            background = Image.open(background_path)
            draw = ImageDraw.Draw(background)
            width, height = background.size
            
            font = None
            font_paths = [
                "data/plugins/astrbot_plugin_mcstatus/cute_font.ttf",
                "simhei.ttf",
                "msyh.ttc",
                # Linux系统常用字体路径
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/arphic/ukai.ttc",
                "/usr/share/fonts/truetype/arphic/uming.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "DejaVuSans.ttf",
                "Arial.ttf",
            ]
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, 40)
                    logger.info(f"使用字体: {font_path}")
                    break
                except IOError:
                    continue
            if font is None:
                logger.warning("未找到指定字体，使用默认字体")
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            shadow_color = (0, 0, 0, 128)
            draw.text((x+2, y+2), text, font=font, fill=shadow_color)
            
            text_color = (255, 255, 255)
            draw.text((x, y), text, font=font, fill=text_color)

            background.save(output_path)
        except FileNotFoundError:
            logger.error(f"错误: 找不到底图文件 {background_path}")
        except Exception as e:
            logger.error(f"生成图片时出错: {e}")