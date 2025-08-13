def rolling_average(df, x: str, y: str, window: int):
    df = df.sort_values(x)
    df[f"{y}_smooth"] = df[y].rolling(window=window, center=True, min_periods=1).mean()
    return df


def exponential_moving_average(df, x: str, y: str, span: int):
    df = df.sort_values(x)
    df[f"{y}_smooth"] = df[y].ewm(span=span, adjust=False).mean()
    return df
