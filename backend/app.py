import joblib
import pandas as pd
from flask import Flask, request, jsonify, Response

MODEL_PATH = "backend_files/superkart_model.joblib"
model_pipeline = joblib.load(MODEL_PATH)

superkart_api = Flask(__name__)

RENAME_MAP = {
    "Product_Id_char": "Product_Category_Code",
    "Store_Age_Years": "Store_Age",
    "Product_Type_Category": "Product_Type",
}


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.rename(columns=RENAME_MAP)
    if "Product_Sugar_Content" in df.columns:
        df["Product_Sugar_Content"] = df["Product_Sugar_Content"].replace({"reg": "Regular"})
    df["Product_MRP_Per_Weight"] = df["Product_MRP"] / df["Product_Weight"]
    return df


@superkart_api.get("/")
def home():
    return jsonify({"message": "SuperKart Sales Prediction API is up and running."})


@superkart_api.post("/v1/predict")
def predict():
    payload = request.get_json(force=True)
    input_df = pd.DataFrame([payload])
    try:
        processed_df = engineer_features(input_df)
        prediction = model_pipeline.predict(processed_df)
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"Product_Store_Sales_Total_Prediction": round(float(prediction[0]), 2)})


@superkart_api.post("/v1/predictbatch")
def predict_batch():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Attach a CSV under form field 'file'."}), 400
    batch_df = pd.read_csv(request.files["file"])
    try:
        processed_df = engineer_features(batch_df)
        predictions = model_pipeline.predict(processed_df)
    except KeyError as e:
        return jsonify({"error": f"Missing required column: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    result = pd.Series(predictions, index=batch_df.index).round(2).to_json()
    return Response(result, mimetype="application/json")


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860)
