import base64
import os

img_path = r'c:\Users\GEO\Desktop\IRise\assets\background.png'
if os.path.exists(img_path):
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    with open(r'c:\Users\GEO\Desktop\IRise\assets\bg_b64.txt', 'w') as f:
        f.write(encoded_string)
    print("Success")
else:
    print("File not found")
