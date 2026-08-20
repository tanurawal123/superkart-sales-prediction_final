import joblib
import pandas as pd
from flask import Flask, request, jsonify, Response

# ------------------------------------------------------------------------------
# Load the serialized model pipeline (preprocessing + tuned XGBoost regressor)
# ------------------------------------------------------------------------------
MODEL_PATH = "backend_files/superkart_model.joblib"
model_pipeline = joblib.load(MODEL_PATH)

# Reference year used consistently with the training notebook's Store_Age
# feature (Store_Age = REFERENCE_YEAR - Store_Establishment_Year).
REFERENCE_YEAR = 2026

superkart_api = Flask(__name__)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recreates the exact feature engineering used in the training notebook so
    a raw request payload matches the columns the fitted pipeline expects.
    """
    df = df.copy()

    if "Product_Sugar_Content" in df.columns:
        df["Product_Sugar_Content"] = df["Product_Sugar_Content"].replace({"reg": "Regular"})

    df["Store_Age"] = REFERENCE_YEAR - df["Store_Establishment_Year"]
    df["Product_MRP_Per_Weight"] = df["Product_MRP"] / df["Product_Weight"]
    df["Product_Category_Code"] = df["Product_Id"].astype(str).str[:2]

    drop_cols = [c for c in ["Product_Id", "Store_Id", "Store_Establishment_Year"] if c in df.columns]
    return df.drop(columns=drop_cols)


@superkart_api.get("/")
def home():
    return jsonify({"message": "SuperKart Sales Prediction API is up and running."})


@superkart_api.post("/v1/predict")
def predict():
    """
    Online (single-record) inference. Expects a JSON payload with:
    Product_Id, Product_Weight, Product_Sugar_Content, Product_Allocated_Area,
    Product_MRP, Product_Type, Store_Establishment_Year, Store_Size,
    Store_Location_City_Type, Store_Type
    """
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
    """
    Batch inference. Expects a CSV file (form field 'file') with the same
    raw columns as the single-record endpoint. Returns row index -> prediction.
    """
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
