import base64
import os

def convert_base64_to_png(input_file, output_file):
    with open(input_file, 'r') as f:
        b64_data = f.read().strip()
    
    # Decode base64 data
    image_data = base64.b64decode(b64_data)
    
    # Write binary data to PNG file
    with open(output_file, 'wb') as f:
        f.write(image_data)

# Convert style1.png
if os.path.exists('style1.png'):
    os.rename('style1.png', 'style1.png.b64')
convert_base64_to_png('style1.png.b64', 'style1.png')

# Do the same for style2.png if it exists and is base64
if os.path.exists('style2.png'):
    os.rename('style2.png', 'style2.png.b64')
    convert_base64_to_png('style2.png.b64', 'style2.png')