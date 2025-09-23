from PIL import Image, ImageDraw, ImageFont
import os

class Draw:
    def __init__(self):
        self.output = "data/whitecloudcn_plugins_data/draw_temp.jpg"
        pass

    def create_image_with_text(self,
                               text: str,
                               background_path: str="data/plugins/astrbot_plugin_mcstatus/assess/bg.jpg" ,
                               output_path: str="data/whitecloudcn_plugins_data/draw_temp.jpg"):
        try:
            background = Image.open(background_path)
            draw = ImageDraw.Draw(background)
            width, height = background.size
            try:
                font = ImageFont.truetype("simhei.ttf", 40)  # 黑体
            except:
                try:
                    font = ImageFont.truetype("msyh.ttc", 40)  # 微软雅黑
                except:
                    # 使用默认字体
                    font = ImageFont.load_default()
            
            # 计算文字位置（居中）
            # 估算文字大小
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 文字位置（居中）
            x = (width - text_width) / 2
            y = (height - text_height) / 2
            
            # 添加文字阴影效果（可选）
            shadow_color = (0, 0, 0, 128)  # 半透明黑色
            draw.text((x+2, y+2), text, font=font, fill=shadow_color)
            
            # 添加主文字
            text_color = (255, 255, 255)  # 白色文字
            draw.text((x, y), text, font=font, fill=text_color)
            
            # 保存图片
            background.save(output_path)
            print(f"图片已生成: {output_path}")
            
            # 显示图片（可选）
            # background.show()
        except FileNotFoundError:
            print(f"错误: 找不到底图文件 {background_path}")
        except Exception as e:
            print(f"生成图片时出错: {e}")