from PIL import Image
import os
import secrets
from flask import current_app

def save_picture(form_picture):
    # Create a random filename for the image to avoid conflicts
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/uploads', picture_fn)

    # Set the output size for resizing (example: 300x300 pixels)
    output_size = (300, 300)

    # Open the image and resize it
    img = Image.open(form_picture)
    img.thumbnail(output_size)

    # Save the resized image
    img.save(picture_path)

    return picture_fn
        