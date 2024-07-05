import streamlit as st
import requests
from PIL import Image
from io import BytesIO

"""
# Flip an image
"""

with st.container(border=True):
    uploaded_image = st.file_uploader(label='Image file')

st.write('')

if uploaded_image:

    # URL of the Flask API endpoint
    url = 'http://127.0.0.1:5000/flip-vertical'

    # Path to the image file you want to upload
    image_path = r"C:\Users\Tom Eleff\Downloads\default.png"
    image_object = Image.open(uploaded_image)
    image_object.save(image_path)

    # Send a POST request to the Flask API with the image file
    files = {'file': open(image_path, 'rb')}
    response = requests.post(url, files=files)

    # Check if the request was successful
    if response.status_code == 200:
        try:

            # Read the returned image from the response
            flipped_image_bytes = BytesIO(
                response.json()['flipped_image'].encode('latin1')
            )
            with st.container(border=True):
                st.image(flipped_image_bytes)

        except Exception as e:
            print(f'Error processing the flipped image: {e}')
    else:
        print(f'Error: {response.status_code}, {response.text}')
