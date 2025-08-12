import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def load_data(file_path: str) -> pd.DataFrame:
    """Load the Titanic dataset."""
    return pd.read_csv(file_path)


def preprocess_data(df: pd.DataFrame) -> tuple:
    """Preprocess the Titanic dataset."""
    # Drop unnecessary columns
    df = df.drop(["PassengerId", "Name", "Ticket", "Cabin"], axis=1)

    # Fill missing values
    df["Age"] = df["Age"].fillna(df["Age"].median())
    df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

    # Convert categorical variables
    df = pd.get_dummies(df, columns=["Sex", "Embarked"], drop_first=True)

    # Split features and target
    X = df.drop("Survived", axis=1)
    y = df["Survived"]

    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled, y, scaler


def split_data(X, y, test_size=0.2, random_state=42):
    """Split data into training and testing sets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)
