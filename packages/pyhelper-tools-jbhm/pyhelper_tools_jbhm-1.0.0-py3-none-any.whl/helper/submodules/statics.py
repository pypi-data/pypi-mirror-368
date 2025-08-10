from ..core import pd, np, format_number, Union, List


def get_moda(
    data: np.ndarray, with_repetition: bool = False
) -> Union[float, List[Union[float, int]]]:
    data_no_nan = data[~np.isnan(data)]

    valores, conteos = np.unique(data_no_nan, return_counts=True)

    if len(conteos) == 0:
        return np.nan if not with_repetition else [np.nan, 0]

    index_moda = np.argmax(conteos)

    if with_repetition:
        return [format_number(valores[index_moda]), format_number(conteos[index_moda])]
    else:
        return format_number(valores[index_moda])


def get_media(data: np.ndarray, nan: bool = False) -> float:
    return format_number(np.nanmean(data) if nan else np.mean(data))


def get_median(data: np.ndarray, nan: bool = False) -> float:
    return format_number(np.nanmedian(data) if nan else np.median(data))


def get_rank(df: pd.DataFrame, column: str) -> float:
    return format_number(np.nanmax(df[column]) - np.nanmin(df[column]))


def get_var(df: pd.DataFrame, column: str) -> float:
    return format_number(np.nanvar(df[column]))


def get_desv(df: pd.DataFrame, column: str) -> float:
    return format_number(np.nanstd(df[column]))


def disp(df: pd.DataFrame, column: str, condition: pd.Series = None) -> dict:
    if condition is not None:
        df = df[condition]

    return {
        "rango": get_rank(df, column),
        "varianza": get_var(df, column),
        "desviacion estandar": get_desv(df, column),
    }
