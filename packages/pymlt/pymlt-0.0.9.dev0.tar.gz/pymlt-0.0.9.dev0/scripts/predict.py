import mlflow
import pandas as pd
from src.data_processing import load_data, preprocess_data


def main():
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")

    # Load the latest model and scaler
    model = mlflow.sklearn.load_model("models:/titanic-model/latest")
    scaler = mlflow.sklearn.load_model("models:/titanic-scaler/latest")

    # Load and preprocess new data
    df = load_data("data/test.csv")
    X, _, _ = preprocess_data(df)

    # Make predictions
    predictions = model.predict(X)

    # Save predictions
    output = pd.DataFrame({"PassengerId": df["PassengerId"], "Survived": predictions})
    output.to_csv("data/predictions.csv", index=False)
    print("Predictions saved to data/predictions.csv")


if __name__ == "__main__":
    main()
