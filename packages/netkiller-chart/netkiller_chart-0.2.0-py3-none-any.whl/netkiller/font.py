# from PIL import ImageFont, ImageDraw, Image
#
# class Font:
#     def __int__(self):
#         pass
#     def getTextSize(text, font_path=None, font_size=12):
#         """
#         计算文本的宽度和高度（像素）
#         :param text: 待测量字符串
#         :param font_path: 字体文件路径（None则使用默认字体）
#         :param font_size: 字号
#         :return: (width, height) 宽和高的元组
#         """
#         # 创建一个临时图像用于测量
#         img = Image.new('RGB', (1, 1))
#         draw = ImageDraw.Draw(img)
#
#         # 加载字体
#         # if font_path:
#
#         # font_prop = FontProperties(family="SimHei")
#         #
#         # # 获取字体文件路径
#         # font_path = findfont(font_prop)
#         #
#         # # 加载字体
#         font_path = "/System/Library/Fonts/PingFang.ttc"  # macOS系统苹方
#         # font = ImageFont.truetype(font_path, font_size)
#
#         # else:
#         # font = ImageFont.load_default(20)
#         font = ImageFont.load_default()  # 默认字体
#
#         print(font.getname(), font.size)
#
#         # 计算文本尺寸
#         # 使用 textbbox 获取边界框（参数为文本左上角坐标）
#         bbox = draw.textbbox((0, 0), text, font=font)
#         left, top, right, bottom = bbox
#
#         # 计算宽度和高度
#         width = right - left
#         height = bottom - top
#         return width, height
#
#
# # 使用示例
# if __name__ == "__main__":
#     text = "Hello, 中文测试"
#     # 中文字体路径（需替换为系统中实际存在的字体文件）
#     # font_path = "C:/Windows/Fonts/simhei.ttf"  # Windows系统黑体
#
#     width, height = getTextSize(text, font_path, font_size=16)
#     print(f"文本宽度：{width}px，高度：{height}px")
