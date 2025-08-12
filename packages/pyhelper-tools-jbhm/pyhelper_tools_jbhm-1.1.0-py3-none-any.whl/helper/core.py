import pandas as pd
import numpy as np
import ast
import sys
import os
import time
from pathlib import Path
import json
import csv
import xml.etree.ElementTree as ET
from typing import Union, List, Dict, Set
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import re
import inspect
import asyncio
from collections.abc import Callable
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Optional

try:
    from IPython.display import display, Markdown
except ImportError:
    display = None
    Markdown = None


def is_jupyter_notebook():
    try:
        from IPython import get_ipython

        ip = get_ipython()
        if ip is None:
            return False

        shell_name = ip.__class__.__name__
        if shell_name == "ZMQInteractiveShell":
            return True
        else:
            return False
    except ImportError:
        return False


IN_JUPYTER = is_jupyter_notebook()

CONFIG_LANG = "en"
NORMAL_SIZE = (10, 6)
BIG_SIZE = (12, 8)
BG_COLOR = "#2d2d2d"
TEXT_COLOR = "#ffffff"
BTN_BG = "#3d3d3d"
HIGHLIGHT_COLOR = "#4e7cad"


config = {
    "verbose": True,
    "default_timeout": 5,
}


def show_gui_popup(
    title, content, fig=None, plot_function=None, plot_args=None, preview_mode=False
):
    copy = t("copy")
    close = t("close")
    save = t("save")
    content_text = t("content")
    preview = t("preview")
    gui_error = t("error_in_gui")

    # Set matplotlib backend
    if "ipykernel" in sys.modules:
        mpl.use("module://ipykernel.pylab.backend_inline")
    else:
        mpl.use("Agg")

    current_fig = fig
    if plot_function is not None:
        if plot_args is None:
            plot_args = {}
        current_fig = plot_function(**plot_args)

    if preview_mode:
        if current_fig is not None:
            current_fig.patch.set_facecolor(BG_COLOR)
            for ax in current_fig.get_axes():
                ax.set_facecolor(BG_COLOR)
                ax.title.set_color(TEXT_COLOR)
                ax.xaxis.label.set_color(TEXT_COLOR)
                ax.yaxis.label.set_color(TEXT_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)
        return current_fig

    # Main window setup
    window = tk.Tk()
    window.title(title)
    window.geometry("900x700")
    window.configure(bg=BG_COLOR)

    # Style configuration
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Dark.TFrame", background=BG_COLOR)
    style.configure(
        "Dark.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Consolas", 10)
    )
    style.configure(
        "Dark.TButton", background=BTN_BG, foreground=TEXT_COLOR, borderwidth=1
    )
    style.map("Dark.TButton", background=[("active", HIGHLIGHT_COLOR)])

    # Main container with proper weight distribution
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    main_frame = ttk.Frame(window, style="Dark.TFrame")
    main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    main_frame.grid_rowconfigure(0, weight=1)
    main_frame.grid_columnconfigure(0, weight=1)

    # Notebook for tabs
    notebook = ttk.Notebook(main_frame)
    notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

    # Content tab
    doc_frame = ttk.Frame(notebook, style="Dark.TFrame")
    notebook.add(doc_frame, text=content_text)

    text_area = ScrolledText(
        doc_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
        selectbackground=HIGHLIGHT_COLOR,
    )
    text_area.pack(expand=True, fill="both", padx=5, pady=5)
    text_area.insert(tk.END, content)
    text_area.config(state="disabled")

    # Visualization handling
    current_fig = fig
    canvas = None

    if fig is not None or plot_function is not None:
        # Preview tab
        graph_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(graph_frame, text=preview)

        if plot_function is not None:
            if plot_args is None:
                plot_args = {}
            current_fig = plot_function(**plot_args)

        if current_fig is not None:
            # Style the figure
            current_fig.patch.set_facecolor(BG_COLOR)
            for ax in current_fig.get_axes():
                ax.set_facecolor(BG_COLOR)
                ax.title.set_color(TEXT_COLOR)
                ax.xaxis.label.set_color(TEXT_COLOR)
                ax.yaxis.label.set_color(TEXT_COLOR)
                ax.tick_params(colors=TEXT_COLOR)
                for spine in ax.spines.values():
                    spine.set_color(TEXT_COLOR)

            # Display in canvas
            canvas = FigureCanvasTkAgg(current_fig, master=graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Button functions
    def copy_to_clipboard():
        window.clipboard_clear()
        window.clipboard_append(content)
        window.update()

    def save_image():
        if current_fig is not None:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*"),
                ],
            )
            if filepath:
                current_fig.savefig(filepath, bbox_inches="tight", dpi=300)

    def on_close():
        if current_fig is not None:
            plt.close(current_fig)
        window.quit()
        window.destroy()

    # Button container - using grid for better layout control
    btn_frame = ttk.Frame(main_frame, style="Dark.TFrame")
    btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))

    # Configure button frame columns
    btn_frame.grid_columnconfigure(0, weight=1)
    btn_frame.grid_columnconfigure(1, weight=1)

    # Action button (changes function based on tab)
    action_btn = ttk.Button(
        btn_frame, text=copy, command=copy_to_clipboard, style="Dark.TButton"
    )
    action_btn.grid(row=0, column=0, padx=5, sticky="w")

    # Close button
    close_btn = ttk.Button(
        btn_frame, text=close, command=on_close, style="Dark.TButton"
    )
    close_btn.grid(row=0, column=1, padx=5, sticky="e")

    # Tab change handler
    def on_tab_change(event):
        if notebook.index("current") == 1 and current_fig is not None:  # Preview tab
            action_btn.config(text=save, command=save_image)
        else:
            action_btn.config(text=copy, command=copy_to_clipboard)

    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    # Initial button state
    if fig is not None or plot_function is not None:
        if notebook.index("current") == 1:  # If preview tab is active
            action_btn.config(text=save, command=save_image)

    # Jupyter Notebook specific handling
    if "ipykernel" in sys.modules:
        from IPython.display import display
        import ipywidgets as widgets

        output = widgets.Output()
        display(output)

        def run_in_jupyter():
            with output:
                try:
                    window.mainloop()
                except Exception as e:
                    print(f"{gui_error}: {str(e)}")

        # Schedule the GUI to run in the next event loop iteration
        window.after(100, run_in_jupyter)
    else:
        # Standard CLI execution
        window.mainloop()

    # Cleanup
    if current_fig is not None:
        plt.close(current_fig)


TRANSLATIONS_PATH = Path(__file__).parent / "translations.json"
TRANSLATIONS = {}
_translations = {}


def t(key: str, lang: str = None) -> str:
    if not key:
        return t("missing_translation_key").format(key=key)

    lang = lang or CONFIG_LANG

    entry = _translations.get(key, {})

    if lang not in entry:
        return f"[{key}]"

    return entry[lang]


def load_user_translations(lang_path: str = "lang.json"):
    global _translations

    user_translations = {}
    path = Path(lang_path)

    if path.is_file():
        try:
            with open(path, "r", encoding="utf-8") as f:
                user_translations = json.load(f)
        except Exception as e:
            show_gui_popup(
                t("warning"), t("load_user_translations_error").format(error=str(e))
            )

    _translations = TRANSLATIONS.copy()
    _translations.update(user_translations)


if TRANSLATIONS_PATH.exists():
    with open(TRANSLATIONS_PATH, encoding="utf-8") as f:
        TRANSLATIONS = json.load(f)
        _translations = TRANSLATIONS.copy()

else:
    show_gui_popup(t("warning"), t("translations_not_found_warning"))


REGISTRY = {}


def register(name=None):
    """
    Decorator to register a function or class in the global REGISTRY.
    Allows other parts of the package to dynamically access utilities by name.
    """

    def wrapper(fn):
        key = name or fn.__name__
        REGISTRY[key] = fn
        return fn

    return wrapper


def generate_all_previews(preview_data):
    """Función auxiliar para generar todos los previews en un solo gráfico"""
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec

    # Textos traducidos
    preview_title = t("function_preview_title")  # "Preview de {function}"
    non_graph_preview = t(
        "non_graph_preview_available"
    )  # "Preview no gráfico disponible"
    preview_error = t("preview_error_message")  # "Error en preview:\n{error}"

    fig = plt.figure(figsize=(12, 8), tight_layout=True)
    gs = GridSpec(len(preview_data), 1, figure=fig)

    for idx, (func_name, data) in enumerate(preview_data.items()):
        ax = fig.add_subplot(gs[idx])
        ax.set_title(preview_title.format(function=func_name), fontsize=10)

        try:
            # Ejecutar la función de preview y capturar la figura si existe
            result = data["preview_func"]()
            if hasattr(result, "figure"):
                result.figure.clf()
                plt.close(result.figure)
                ax.imshow(result.canvas.renderer.buffer_rgba())
            else:
                ax.text(0.5, 0.5, non_graph_preview, ha="center", va="center")
                ax.axis("off")
        except Exception as e:
            ax.text(
                0.5,
                0.5,
                preview_error.format(error=str(e)),
                ha="center",
                va="center",
                color="red",
            )
            ax.axis("off")

    return fig


def help(type: str = None):

    preview_text = t("preview")
    example_text = t("example")
    description = t("description")
    preview_error_text = t("preview_error")
    gui_error_text = t("error_in_gui")
    available_funcs_text = t("help_available_functions")
    usage_text = t("help_usage")
    error_text = t("help_error")
    all_title_text = t("title_all")
    function_preview_title = t("function_preview_title")  # "Preview de {function}"
    non_graph_preview = t("non_graph_preview_available")
    preview_error_msg = t("preview_error_message")
    async_preview_note = t("async_preview_not_available")

    from . import ALL_FUNCTIONS

    globals().update(ALL_FUNCTIONS)

    def call_func(func_name, *args, **kwargs):
        return ALL_FUNCTIONS[func_name](*args, **kwargs)

    help_map = {
        "hbar": {
            description: t("hbar"),
            example_text: 'hbar(pd.Series([30, 70], index=["A", "B"]), title="My Chart", xlabel="Categories", ylabel="Values")',
            preview_text: lambda: call_func(
                "hbar",
                pd.Series([30, 70], index=["A", "B"]),
                title="My Chart",
                xlabel="Categories",
                ylabel="Values",
                show=IN_JUPYTER,
            ),
        },
        "vbar": {
            description: t("vbar"),
            example_text: 'vbar(pd.Series([30, 70], index=["A", "B"]), title="Vertical Chart", xlabel="Categories", ylabel="Values")',
            preview_text: lambda: call_func(
                "vbar",
                pd.Series([30, 70], index=["A", "B"]),
                title="Vertical Chart",
                xlabel="Categories",
                ylabel="Values",
                show=IN_JUPYTER,
            ),
        },
        "pie": {
            description: t("pie"),
            example_text: 'pie(pd.Series([50, 50], index=["Cats", "Dogs"]), title="Pets")',
            preview_text: lambda: call_func(
                "pie",
                pd.Series([50, 50], index=["Cats", "Dogs"]),
                title="Pets",
                show=IN_JUPYTER,
            ),
        },
        "normalize": {
            description: t("normalize"),
            example_text: 'normalize(pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}), columns=["A", "B"])',
            preview_text: lambda: call_func(
                "disp",
                call_func(
                    "normalize",
                    pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}),
                    columns=["A", "B"],
                ),
            ),
        },
        "get_moda": {
            description: t("get_moda"),
            example_text: "get_moda(pd.Series([1, 2, 2, 3]))",
            preview_text: lambda: print(
                "Moda:", call_func("get_moda", pd.Series([1, 2, 2, 3]))
            ),
        },
        "get_media": {
            description: t("get_media"),
            example_text: "get_media(pd.Series([10, 20, 30]))",
            preview_text: lambda: print(
                "Media:", call_func("get_media", pd.Series([10, 20, 30]))
            ),
        },
        "get_median": {
            description: t("get_median"),
            example_text: "get_median(pd.Series([10, 20, 30]))",
            preview_text: lambda: print(
                "Median:", call_func("get_median", pd.Series([10, 20, 30]))
            ),
        },
        "boxplot": {
            description: t("boxplot"),
            example_text: 'boxplot(pd.DataFrame({"Values": [10, 20, 30, 40, 50]}))',
            preview_text: lambda: call_func(
                "boxplot",
                pd.DataFrame({"Values": [10, 20, 30, 40, 50]}),
                show=IN_JUPYTER,
            ),
        },
        "get_rank": {
            description: t("get_rank"),
            example_text: 'get_rank(pd.DataFrame({"Values": [10, 30, 20]}), "Values")',
            preview_text: lambda: print(
                "Rank:",
                call_func("get_rank", pd.DataFrame({"Values": [10, 30, 20]}), "Values"),
            ),
        },
        "get_var": {
            description: t("get_var"),
            example_text: 'get_var(pd.DataFrame({"Values": [10, 20, 30]}), "Values")',
            preview_text: lambda: print(
                "Varianza:",
                call_func("get_var", pd.DataFrame({"Values": [10, 20, 30]}), "Values"),
            ),
        },
        "get_desv": {
            description: t("get_desv"),
            example_text: 'get_desv(pd.DataFrame({"Values": [10, 20, 30]}), "Values")',
            preview_text: lambda: print(
                "Desviación estándar:",
                call_func("get_desv", pd.DataFrame({"Values": [10, 20, 30]}), "Values"),
            ),
        },
        "histo": {
            description: t("histo"),
            example_text: 'histo(pd.DataFrame({"Values": [1, 2, 2, 3, 3, 3, 4, 4, 5]}))',
            preview_text: lambda: call_func(
                "histo",
                pd.DataFrame({"Values": [1, 2, 2, 3, 3, 3, 4, 4, 5]}),
                show=IN_JUPYTER,
            ),
        },
        "disp": {
            description: t("disp"),
            example_text: 'disp(pd.DataFrame({"X": [1, 2, 3], "Y": [4, 5, 6]}))',
            preview_text: lambda: call_func(
                "disp", pd.DataFrame({"X": [1, 2, 3], "Y": [4, 5, 6]})
            ),
        },
        "table": {
            description: t("table"),
            example_text: 'table(pd.DataFrame({"A": [1, 2], "B": [3, 4]}))',
            preview_text: lambda: call_func(
                "table", pd.DataFrame({"A": [1, 2], "B": [3, 4]}), show=IN_JUPYTER
            ),
        },
        "conditional": {
            description: t("conditional"),
            example_text: 'conditional(pd.DataFrame({"A": [1, 2, 3]}), "A", lambda x: x > 1)',
            preview_text: lambda: call_func(
                "conditional", pd.DataFrame({"A": [1, 2, 3]}), "A", lambda x: x > 1
            ),
        },
        "heatmap": {
            description: t("heatmap"),
            example_text: 'heatmap(pd.DataFrame({"X": ["A", "A", "B"], "Y": ["C", "D", "C"], "Value": [1, 2, 3]}), "X", "Y", "Value")',
            preview_text: lambda: call_func(
                "heatmap",
                pd.DataFrame(
                    {"X": ["A", "A", "B"], "Y": ["C", "D", "C"], "Value": [1, 2, 3]}
                ),
                "X",
                "Y",
                "Value",
                show=IN_JUPYTER,
            ),
        },
        "call": {
            description: t("call"),
            example_text: 'call("test", "csv")',
            preview_text: lambda: print("Resultado:", call_func("call", "test", "csv")),
        },
        "switch": {
            description: t("switch"),
            example_text: """
# Ejemplo 1: Switch básico
result = Switch(5)(
    lambda x: x > 0, lambda: "Positive",
    lambda x: x < 0, lambda: "Negative",
    "default", lambda: "Zero"
)
# Output: "Positive"

# Ejemplo 2: Formato de diccionario
result_dict = Switch(5)({
    "cases": [
        {"case": lambda x: x > 10, "then": lambda: "Greater than 10"},
        {"case": lambda x: x > 0, "then": lambda: "Positive"}
    ],
    "default": lambda: "Zero"
})
# Output: "Positive"

# Ejemplo 3: Múltiples condiciones
print(Switch(3)(
    lambda x: x == 1, lambda: "One",
    lambda x: x in range(2, 5), lambda: "Between 2 and 4",
    lambda x: x > 10, lambda: "Greater than 10",
    "default", lambda: "Other value"
))
# Output: "Between 2 and 4"
    """,
            preview_text: lambda: call_func("Switch", 5)(
                lambda x: x > 0,
                lambda: print(t("switch_preview_positive")),
                "default",
                lambda: print(t("switch_preview_zero")),
            ),
        },
        "async_switch": {
            description: t("async_switch"),
            example_text: """
async def async_positive():
    await asyncio.sleep(0.1)
    return "Async Positive"

async def main_async():
    result = await AsyncSwitch(5)(
        lambda x: x > 0, async_positive,
        "default", lambda: "Default"
    )
    print(result)  # Output: "Async Positive"

asyncio.run(main_async())
    """,
            preview_text: lambda: print(t("async_preview_not_available")),
        },
        "t": {
            description: t("t"),
            example_text: 't("hello")',
            preview_text: lambda: print(call_func("t", "hello")),
        },
        "show_gui_popup": {
            description: t("show_gui_popup"),
            example_text: "show_gui_popup(title, content, fig=None, plot_function=None, plot_args=None)",
            preview_text: lambda: call_func(
                "show_gui_popup",
                "Title",
                "Content",
                "plot_function=lambda: (plt.figure(), plt.plot([1,2,3], [1,4,9])",
                "preview_mode=True)",
            ),
        },
        "load_user_translations": {
            description: t("load_user_translations"),
            example_text: 'load_user_translations({"es": {"hello": "hola"}})',
            preview_text: lambda: call_func(
                "load_user_translations", {"es": {"hello": "hola"}}
            ),
        },
        "scatter": {
            description: t("scatter_description"),
            example_text: 'scatter(df, x="age", y="income", hue="gender", title="Age vs Income")',
            preview_text: lambda: call_func(
                "scatter",
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40, 45, 50],
                        "income": [40000, 45000, 60000, 80000, 75000, 90000],
                        "gender": ["M", "F", "M", "F", "M", "F"],
                    }
                ),
                x="age",
                y="income",
                hue="gender",
                title="Age vs Income",
                show=IN_JUPYTER,
            ),
        },
        "lineplot": {
            description: t("lineplot_description"),
            example_text: 'lineplot(df, x="year", y="sales", hue="product", title="Sales Trend")',
            preview_text: lambda: call_func(
                "lineplot",
                pd.DataFrame(
                    {
                        "year": [2018, 2019, 2020, 2021, 2022],
                        "sales": [100, 120, 150, 180, 200],
                        "product": ["A", "A", "B", "B", "B"],
                    }
                ),
                x="year",
                y="sales",
                hue="product",
                title="Sales Trend",
                show=IN_JUPYTER,
            ),
        },
        "kdeplot": {
            description: t("kdeplot_description"),
            example_text: 'kdeplot(df, column="age", title="Age Distribution")',
            preview_text: lambda: call_func(
                "kdeplot",
                pd.DataFrame({"age": [25, 30, 35, 40, 45, 50, 55, 60]}),
                column="age",
                title="Age Distribution",
                show=IN_JUPYTER,
            ),
        },
        "violinplot": {
            description: t("violinplot_description"),
            example_text: 'violinplot(df, x="category", y="value", title="Distribution by Category")',
            preview_text: lambda: call_func(
                "violinplot",
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B", "C", "C"],
                        "value": [10, 12, 15, 18, 8, 11],
                    }
                ),
                x="category",
                y="value",
                title="Distribution by Category",
                show=IN_JUPYTER,
            ),
        },
        "pairplot": {
            description: t("pairplot_description"),
            example_text: 'pairplot(df[numeric_cols], title="Relationships between Numeric Variables")',
            preview_text: lambda: call_func(
                "pairplot",
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40],
                        "income": [40000, 45000, 60000, 80000],
                        "score": [80, 85, 90, 95],
                    }
                ),
                title="Relationships between Variables",
                show=IN_JUPYTER,
            ),
        },
        "countplot": {
            description: t("countplot_description"),
            example_text: 'countplot(df, x="category", title="Count by Category")',
            preview_text: lambda: call_func(
                "countplot",
                pd.DataFrame({"category": ["A", "B", "A", "C", "B", "A"]}),
                x="category",
                title="Count by Category",
                show=IN_JUPYTER,
            ),
        },
        "lmplot": {
            description: t("lmplot_description"),
            example_text: 'lmplot(df, x="age", y="income", hue="gender", title="Income by Age")',
            preview_text: lambda: call_func(
                "lmplot",
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40, 45, 50],
                        "income": [40000, 45000, 60000, 80000, 75000, 90000],
                        "gender": ["M", "F", "M", "F", "M", "F"],
                    }
                ),
                x="age",
                y="income",
                hue="gender",
                title="Income by Age",
                show=IN_JUPYTER,
            ),
        },
        "jointplot": {
            description: t("jointplot_description"),
            example_text: 'jointplot(df, x="age", y="income", kind="scatter", title="Age vs Income")',
            preview_text: lambda: call_func(
                "jointplot",
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40, 45, 50],
                        "income": [40000, 45000, 60000, 80000, 75000, 90000],
                    }
                ),
                x="age",
                y="income",
                kind="scatter",
                title="Age vs Income",
                show=IN_JUPYTER,
            ),
        },
        "swarmplot": {
            description: t("swarmplot_description"),
            example_text: 'swarmplot(df, x="category", y="value", title="Value Distribution")',
            preview_text: lambda: call_func(
                "swarmplot",
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B", "C", "C"],
                        "value": [10, 12, 15, 18, 8, 11],
                    }
                ),
                x="category",
                y="value",
                title="Value Distribution",
                show=IN_JUPYTER,
            ),
        },
        "regplot": {
            description: t("regplot_description"),
            example_text: 'regplot(df, x="age", y="income", title="Income by Age")',
            preview_text: lambda: call_func(
                "regplot",
                pd.DataFrame(
                    {
                        "age": [25, 30, 35, 40, 45, 50],
                        "income": [40000, 45000, 60000, 80000, 75000, 90000],
                    }
                ),
                x="age",
                y="income",
                title="Income by Age",
                show=IN_JUPYTER,
            ),
        },
        "distplot": {
            description: t("distplot_description"),
            example_text: 'distplot(df["age"], title="Age Distribution")',
            preview_text: lambda: call_func(
                "distplot",
                pd.Series([25, 30, 35, 40, 45, 50, 55, 60]),
                title="Age Distribution",
                show=IN_JUPYTER,
            ),
        },
        "barplot": {
            description: t("barplot_description"),
            example_text: 'barplot(df, x="category", y="value", title="Average Value by Category")',
            preview_text: lambda: call_func(
                "barplot",
                pd.DataFrame({"category": ["A", "B", "C"], "value": [10, 15, 8]}),
                x="category",
                y="value",
                title="Average Value by Category",
                show=IN_JUPYTER,
            ),
        },
        "stripplot": {
            description: t("stripplot_description"),
            example_text: 'stripplot(df, x="category", y="value", title="Value by Category")',
            preview_text: lambda: call_func(
                "stripplot",
                pd.DataFrame(
                    {
                        "category": ["A", "A", "B", "B", "C", "C"],
                        "value": [10, 12, 15, 18, 8, 11],
                    }
                ),
                x="category",
                y="value",
                title="Value by Category",
                show=IN_JUPYTER,
            ),
        },
    }

    functions = sorted(help_map.keys())

    if type is None:
        if IN_JUPYTER:
            display(Markdown(f"**{available_funcs_text}**"))
            for func in sorted(help_map.keys()):
                display(Markdown(f"- `{func}`"))
            display(Markdown(f"\n*{usage_text}*"))
        else:
            func_list = "\n".join([f"- {func}" for func in sorted(help_map.keys())])
            show_gui_popup(
                "Help", f"{available_funcs_text}\n{func_list}\n\n{usage_text}"
            )
        return

    elif not isinstance(type, str):
        msg = t("error_type")
        if IN_JUPYTER:
            display(Markdown(f"**Error:** {msg}"))
        else:
            messagebox.showerror(gui_error_text, msg)
        return

    type = type.lower()

    if type == "all":
        full_doc = ""
        preview_data = {}

        for func_name in functions:
            doc = t(func_name)
            entry = help_map.get(func_name, {})
            example = entry.get(example_text, "")

            # Construir documentación básica
            full_doc += f"\n**{func_name.upper()}**\n```python\n{doc.strip()}\n```\n"

            # Si hay ejemplo, agregarlo
            if example:
                full_doc += f"\n**{example_text}:**\n```python\n{example}\n```\n"

            # Preparar datos para preview si existe
            if preview_text in entry:
                preview_data[func_name] = {
                    example_text: example,
                    "preview_func": entry[preview_text],
                }

        if IN_JUPYTER:
            display(Markdown(full_doc))

            # Mostrar previews en Jupyter
            for func_name, data in preview_data.items():
                display(
                    Markdown(
                        f"\n**{function_preview_title.format(function=func_name)}:**"
                    )
                )
                try:
                    data["preview_func"]()
                except Exception as e:
                    display(
                        Markdown(f"```\n{preview_error_msg.format(error=str(e))}\n```")
                    )
        else:
            # En CLI usar show_gui_popup con pestañas
            def wrapped_preview_function():
                return generate_all_previews(preview_data)

            show_gui_popup(
                all_title_text,
                full_doc.replace("**", "").replace("```python", "").replace("```", ""),
                plot_function=wrapped_preview_function,
                plot_args={},  # Eliminamos el parámetro que causaba el problema
            )
        return

    if type in functions:
        doc = t(type)
        entry = help_map.get(type, {})
        example = entry.get(example_text, "")
        preview_func = entry.get(preview_text)

        if IN_JUPYTER:
            output = f"**{type.upper()}**\n```python\n{doc.strip()}\n```"
            if example:
                output += f"\n\n**{example_text}:**\n```python\n{example}\n```"
            display(Markdown(output))

            if preview_func:
                try:
                    print(f"\n**{preview_text}:**")
                    preview_func()
                except Exception as e:
                    display(Markdown(f"**{preview_error_text}:**\n```\n{str(e)}\n```"))
        else:
            full_text = f"{doc.strip()}"
            if example:
                full_text += f"\n\n{example_text}:\n{example}"

            fig = None
            if preview_func:
                try:
                    result = preview_func()
                    if hasattr(result, "figure"):
                        fig = result.figure
                except Exception as e:
                    messagebox.showerror(f"{preview_error_text} {type}", str(e))

            show_gui_popup(type.upper(), full_text, fig=fig)
    else:
        error_msg = error_text.format(type)
        if IN_JUPYTER:
            display(Markdown(f"**{error_msg}**"))
        else:
            show_gui_popup(gui_error_text, error_msg)


def format_number(
    value: float, use_decimals: bool = True, decimals: int = 2, percent: bool = False
) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "N/A"

    if percent:
        value *= 100

    if use_decimals:
        formatted = f"{value:,.{decimals}f}"
    else:
        formatted = f"{int(round(value)):,}"

    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")

    if percent:
        formatted += "%"

    return formatted


def set_language(lang: str):
    global CONFIG_LANG
    if lang not in next(iter(TRANSLATIONS.values())).keys():
        raise ValueError(f"Language '{lang}' is not available.")
    CONFIG_LANG = lang


__all__ = [
    "sys",
    "ast",
    "pd",
    "Path",
    "Dict",
    "Set",
    "json",
    "csv",
    "ET",
    "mpl",
    "Union",
    "List",
    "sns",
    "tk",
    "messagebox",
    "ScrolledText",
    "np",
    "plt",
    "re",
    "inspect",
    "asyncio",
    "Callable",
    "time",
    "os",
    "re",
    "help",
    "format_number",
    "config",
    "REGISTRY",
    "register",
    "NORMAL_SIZE",
    "BIG_SIZE",
    "CONFIG_LANG",
    "set_language",
    "t",
    "show_gui_popup",
    "load_user_translations",
    "Optional",
    "filedialog",
]
