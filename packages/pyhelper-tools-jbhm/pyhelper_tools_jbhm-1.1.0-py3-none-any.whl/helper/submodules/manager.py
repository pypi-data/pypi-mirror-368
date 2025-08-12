from ..core import np


def normalize(data: np.ndarray):
    range_val = data.max() - data.min()
    return np.zeros_like(data) if range_val == 0 else (data - data.min()) / range_val


def conditional(df, conditions, results, column_name):
    try:
        if len(conditions) != len(results):
            raise ValueError("La cantidad de condiciones y resultados debe ser igual.")
        df[column_name] = np.select(conditions, results, default=False)
        return df
    except Exception as e:
        print(f"Error: {e}")
