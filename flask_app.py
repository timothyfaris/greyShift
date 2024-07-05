from flask import Flask, request, jsonify
from PIL import Image
from io import BytesIO

app = Flask(__name__)


def flip_image_vertical(image):
    return image.transpose(Image.FLIP_TOP_BOTTOM)


@app.route('/flip-vertical', methods=['POST'])
def flip_vertical():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        try:
            img = Image.open(file)
            flipped_img = flip_image_vertical(img)
            output_buffer = BytesIO()
            flipped_img.save(output_buffer, format='PNG')
            output_buffer.seek(0)
            return jsonify(
                {'flipped_image': output_buffer.getvalue().decode('latin1')}
            )
        except Exception as e:
            return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
