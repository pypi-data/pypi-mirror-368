import mlflow
from src.data_processing import load_data, preprocess_data, split_data
from src.model import evaluate_model, train_model


def main():
    # Set MLflow tracking URI
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("titanic-survival-prediction")

    # Load and preprocess data
    df = load_data("data/train.csv")
    X, y, scaler = preprocess_data(df)
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Train model
    model = train_model(X_train, y_train)

    # Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    print("Model metrics:", metrics)

    # Save model and scaler
    mlflow.sklearn.log_model(model, "model")
    mlflow.sklearn.log_model(scaler, "scaler")


if __name__ == "__main__":
    main()
