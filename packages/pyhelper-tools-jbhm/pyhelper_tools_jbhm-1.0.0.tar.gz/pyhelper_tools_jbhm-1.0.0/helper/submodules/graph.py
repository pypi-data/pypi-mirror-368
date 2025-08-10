from ..core import pd, BIG_SIZE, NORMAL_SIZE, plt, format_number, sns, mpl, Optional


def hbar(
    data: pd.Series,
    title: str,
    xlabel: str,
    ylabel: str,
    save_path=None,
    show: bool = True,
):
    if not show:
        mpl.use("Agg")

    fig = plt.figure(figsize=BIG_SIZE)

    y_pos = range(len(data))
    bars = plt.barh(y_pos, data.values, color="skyblue")

    plt.yticks(ticks=y_pos, labels=data.index)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="x", alpha=0.3)

    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(
            width + 2,
            bar.get_y() + bar.get_height() / 2,
            format_number(width, use_decimals=False),
            va="center",
        )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def vbar(
    data: pd.DataFrame,
    title: str,
    xlabel: str,
    ylabel: str,
    save_path=None,
    show: bool = True,
):
    if not show:
        mpl.use("Agg")

    fig = plt.figure(figsize=BIG_SIZE)
    bars = plt.bar(data.index, data.values, color="skyblue")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(axis="y", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        x = bar.get_x() + bar.get_width() / 2
        plt.text(
            x,
            height + (height * 0.02),
            format_number(height, use_decimals=False),
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def pie(
    valores,
    etiquetas,
    colores,
    title: str,
    decimales: int = 1,
    save_path=None,
    show: bool = True,
):
    if not show:
        mpl.use("Agg")

    fig, ax = plt.subplots()

    use_labels = len(etiquetas) <= 10
    labels = etiquetas if use_labels else None

    def format_pct(pct):
        return format_number(
            pct / 100, use_decimals=True, decimals=decimales, percent=True
        )

    wedges, texts, autotexts = ax.pie(
        valores,
        labels=labels,
        autopct=format_pct,
        colors=colores,
        startangle=90,
        wedgeprops={"edgecolor": "black", "linewidth": 0.8},
        textprops={"fontsize": 8},
    )

    if not use_labels:
        ax.legend(
            wedges,
            etiquetas,
            title="Categorías",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=8,
            title_fontsize=9,
        )

    ax.set_title(title)
    ax.axis("equal")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def boxplot(
    df: pd.DataFrame,
    x: str = None,
    y: str = None,
    hue: str = None,
    title: str = "",
    save_path=None,
    show: bool = True,
):
    if not show:
        mpl.use("Agg")

    fig = plt.figure(figsize=BIG_SIZE)
    sns.boxplot(data=df, x=x, y=y, hue=hue)
    plt.title(title)
    if x is not None:
        plt.xlabel(x)
    if y is not None:
        plt.ylabel(y)
    if hue:
        plt.legend(title=hue)
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def histo(
    df: pd.DataFrame,
    column: str,
    condition: Optional[pd.Series] = None,
    bins: int = 20,
    title: str = "",
    save_path=None,
    show: bool = True,
):
    if not show:
        mpl.use("Agg")

    if condition is not None:
        df = df[condition]

    fig = plt.figure(figsize=NORMAL_SIZE)
    plt.hist(
        df[column].dropna(), bins=bins, color="skyblue", edgecolor="black", alpha=0.7
    )
    plt.title(title or f"Histograma de {column}")
    plt.xlabel(column)
    plt.ylabel("Frecuencia")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def heatmap(
    df, index_col, column_col, value_col, title="", save_path=None, show: bool = True
):
    if not show:
        mpl.use("Agg")

    tabla = df.groupby([index_col, column_col])[value_col].size().unstack(fill_value=0)

    fig = plt.figure(figsize=NORMAL_SIZE)
    sns.heatmap(
        tabla, cmap="YlGnBu", annot=True, fmt="d", annot_kws={"size": 7}, linewidths=0.1
    )
    plt.title(title)
    plt.xlabel(column_col)
    plt.ylabel(index_col)
    plt.xticks(rotation=0)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig


def table(data, col_labels, title="", save_path=None, show: bool = True):
    if not show:
        mpl.use("Agg")

    fig, ax = plt.subplots()
    ax.axis("off")

    tabla = ax.table(cellText=data, colLabels=col_labels, cellLoc="center", loc="top")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(12)
    tabla.scale(1.5, 1.5)

    if title:
        plt.title(title)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, bbox_inches="tight")

    if show:
        plt.show()
        return None
    else:
        return fig
