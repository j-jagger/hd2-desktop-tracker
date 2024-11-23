from flask import Flask, jsonify

app = Flask(__name__)

# sample data matching HD2 API structures
# change id32 / id to make the program react.
major_orders_data = [
    {
        "id32": 121111231,
        "setting": {
            "overrideTitle": "these people",
            "overrideBrief": "they're eating the dogs they're eating the cats"
        }
    },
    {
        "id32": 221321,
        "setting": {
            "overrideTitle": "clean general brasch's dishes",
            "overrideBrief": "secure the strategic location."
        }
    }
]
1
news_data = [
    {
        "id": 1010,
        "message": "foobar"
    },
    {
        "id": 102,
        "message": "hellbivers 3"
    }
]

@app.route('/major-orders', methods=['GET'])
def get_major_orders():
    return jsonify(major_orders_data)

@app.route('/news', methods=['GET'])
def get_news():
    return jsonify(news_data)

if __name__ == '__main__':
    app.run(debug=True)
