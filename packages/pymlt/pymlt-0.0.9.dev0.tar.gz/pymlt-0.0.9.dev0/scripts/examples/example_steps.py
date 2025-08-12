import pandas as pd


def step_1(df):
    return df.assign(b=1)


def step_2(df):
    return df.assign(c=2)


def step_3(df):
    return df.assign(d=3)


def step_4(df):
    return df


def steps(df):
    df = df.pipe(step_1).pipe(step_2).pipe(step_3).pipe(step_4)
    return df


df = pd.DataFrame({"a": [1, 2, 3]})
print(steps(df))
