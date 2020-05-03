import os
from typing import Dict

from flask import Flask, request, jsonify

from model import get_learner
from model import min_abs_diff, mean_abs_diff, max_abs_diff  # need this import inderectly by the model

import pandas as pd

app = Flask(__name__)
learner = get_learner()


def predict_price(row) -> Dict:
    _, price, _ = learner.predict(row)
    return price.item()  # item() to convert tensor to value


@app.route("/predictor/", methods=["POST"])
def predict():
    print(f"request: {request.json}")
    df = pd.DataFrame(request.json)
    df["price"] = df.apply(predict_price, axis=1)
    # df to List[Dict]
    # details: https://stackoverflow.com/questions/29815129/pandas-dataframe-to-list-of-dictionaries
    predictions = list(df.T.to_dict().values())
    print(f"predictions: {predictions}")
    return jsonify(predictions)


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=os.environ.get("PORT", 8080),
        debug=os.environ.get("FLASK_DEBUG", False),
    )
