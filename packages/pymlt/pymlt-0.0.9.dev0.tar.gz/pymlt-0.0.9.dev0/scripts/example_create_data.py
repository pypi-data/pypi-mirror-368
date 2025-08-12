from pathlib import Path

import seaborn as sns

Path(__file__).resolve().parent.parent.joinpath("data").mkdir(exist_ok=True)
df = sns.load_dataset("titanic")
df.to_csv("data/titanic.csv", index=False)
