from PIL import Image, ImageEnhance, ImageFilter  

image = Image.open(r"C:\Users\fetis\OneDrive\Рабочий стол\stega_5\stegoimage_130_20.png")  
  


blurred_image = image.filter(ImageFilter.BLUR)
blurred_image.save('blurred_image_130_20.png')