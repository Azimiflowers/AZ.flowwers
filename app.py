from flask import Flask, render_template, request
import requests
import base64

app = Flask(__name__)

API_KEY = "6w5jzkX5T18Iz31aL2kSM9NgDVodRPGs86dgrDOYnlZGqhZBw4"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            image_data = base64.b64encode(file.read()).decode('utf-8')
            payload = {
                'api_key': API_KEY,
                'images': [image_data],
                'modifiers': ['crops_fast', 'similar_images'],
                'plant_language': 'fa',
                'plant_details': ['common_names', 'url', 'name_authority', 'wiki_description', 'taxonomy']
            }
            try:
                response = requests.post('https://api.plant.id/v2/identify', json=payload)
                response.raise_for_status()
                data = response.json()

                if data.get("suggestions"):
                    suggestion = data['suggestions'][0]
                    plant_details = suggestion.get('plant_details', {})
                    common_names = plant_details.get('common_names', [])
                    description = plant_details.get('wiki_description', {}).get('value', 'توضیحی موجود نیست')

                    if common_names and isinstance(common_names[0], str):
                        name_fa = common_names[0]
                    else:
                        persian_names = []
                        for name_item in common_names:
                            if isinstance(name_item, dict) and name_item.get('language') == 'fa':
                                persian_names.append(name_item.get('name'))
                        name_fa = persian_names[0] if persian_names else suggestion.get('plant_name', 'نام موجود نیست')

                    result = {
                        'name': name_fa,
                        'description': description,
                        'url': plant_details.get('url', '')
                    }
                else:
                    error = "گل مورد نظر یافت نشد."
            except requests.exceptions.RequestException as e:
                error = f"خطا در درخواست: {e}"
        else:
            error = "فایلی انتخاب نشده است."

    return render_template('index.html', result=result, error=error)


if __name__ == '__main__':
    app.run(debug=True)
