"""
Matplotlib-specific analyzer for extracting information from matplotlib figures.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.axes as mpl_axes
import matplotlib.figure as mpl_figure
import numpy as np
from matplotlib.colors import to_hex
from matplotlib.markers import MarkerStyle

from plot2llm.analyzers.bar_analyzer import analyze as analyze_bar
from plot2llm.analyzers.histogram_analyzer import analyze as analyze_histogram
from plot2llm.analyzers.line_analyzer import analyze as analyze_line
from plot2llm.analyzers.scatter_analyzer import analyze as analyze_scatter
from plot2llm.sections.data_summary_section import build_data_summary_section
from plot2llm.utils import generate_unified_interpretation_hints

from .base_analyzer import BaseAnalyzer

logger = logging.getLogger(__name__)


class MatplotlibAnalyzer(BaseAnalyzer):
    """
    Analyzer specifically designed for matplotlib figures.
    """

    def __init__(self):
        """Initialize the MatplotlibAnalyzer."""
        super().__init__()
        self.supported_types = ["matplotlib.figure.Figure", "matplotlib.axes.Axes"]
        logger.debug("MatplotlibAnalyzer initialized")

    def analyze(
        self,
        figure: Any,
        detail_level: str = "medium",
        include_data: bool = True,
        include_colors: bool = True,
        include_statistics: bool = True,
    ) -> dict:
        """
        Analyze a matplotlib figure and extract comprehensive information.
        Returns a dict compatible with tests and formatters.
        """
        import matplotlib.axes as mpl_axes
        import matplotlib.figure as mpl_figure

        if figure is None:
            raise ValueError("Invalid figure object: None")
        if not (
            isinstance(figure, mpl_figure.Figure) or isinstance(figure, mpl_axes.Axes)
        ):
            raise ValueError("Not a matplotlib figure")
        try:
            # Basic info
            figure_info = self._get_figure_info(figure)

            # Extract axes information using the new utility
            axes_list = []
            real_axes = self._get_axes(figure)
            for ax in real_axes:
                plot_types = self._get_data_types(ax)
                plot_type = plot_types[0] if plot_types else None

                # Detectar tipos de ejes antes de llamar a los analizadores específicos
                x_type, x_labels = self._detect_axis_type_and_labels(ax, "x")
                y_type, y_labels = self._detect_axis_type_and_labels(ax, "y")

                # Mapear correctamente los tipos detectados a los esperados por los analizadores
                # Priorizar histogramas y bar plots sobre líneas cuando hay patches
                if hasattr(ax, "patches") and ax.patches:
                    # Usar las funciones específicas para distinguir entre bar plots e histogramas
                    if self._is_histogram(ax):
                        axes_section = analyze_histogram(ax, x_type, y_type)
                    elif self._is_bar_plot(ax):
                        axes_section = analyze_bar(ax, x_type, y_type)
                    else:
                        # Fallback: usar histograma por defecto
                        axes_section = analyze_histogram(ax, x_type, y_type)
                elif plot_type == "line_plot" or (hasattr(ax, "lines") and ax.lines):
                    axes_section = analyze_line(ax, x_type, y_type)
                elif plot_type == "scatter_plot" or (
                    hasattr(ax, "collections")
                    and ax.collections
                    and any(hasattr(c, "get_offsets") for c in ax.collections)
                ):
                    axes_section = analyze_scatter(ax, x_type, y_type)
                else:
                    axes_section = {
                        "plot_type": plot_type or "unknown",
                        "message": f"El tipo de gráfico '{plot_type or 'unknown'}' está pendiente de implementación profesional.",
                    }

                # Añadir los tipos de ejes detectados al resultado del analizador específico
                axes_section["x_type"] = x_type
                axes_section["y_type"] = y_type

                # Añadir información adicional del eje que no está en los analizadores específicos
                # Solo añadir campos que no existan ya en el resultado del analizador específico
                if "title" not in axes_section:
                    axes_section["title"] = str(ax.get_title())
                if "xlabel" not in axes_section:
                    axes_section["xlabel"] = str(ax.get_xlabel())
                if "ylabel" not in axes_section:
                    axes_section["ylabel"] = str(ax.get_ylabel())
                if "x_range" not in axes_section:
                    axes_section["x_range"] = [float(x) for x in ax.get_xlim()]
                if "y_range" not in axes_section:
                    axes_section["y_range"] = [float(y) for y in ax.get_ylim()]
                if "has_grid" not in axes_section:
                    axes_section["has_grid"] = bool(
                        any(
                            line.get_visible()
                            for line in ax.get_xgridlines() + ax.get_ygridlines()
                        )
                    )
                if "has_legend" not in axes_section:
                    axes_section["has_legend"] = bool(ax.get_legend() is not None)
                if "spine_visibility" not in axes_section:
                    axes_section["spine_visibility"] = {
                        side: bool(spine.get_visible())
                        for side, spine in ax.spines.items()
                    }
                if "tick_density" not in axes_section:
                    axes_section["tick_density"] = int(len(ax.get_xticks()))

                # Preservar stats y pattern de los analizadores específicos
                # (estos campos ya están incluidos por los analizadores específicos)

                # Convertir plot_type a plot_types para compatibilidad
                if "plot_type" in axes_section:
                    axes_section["plot_types"] = [{"type": axes_section["plot_type"]}]

                axes_list.append(axes_section)

            # Get additional information
            colors = self._get_colors(figure) if include_colors else []
            statistics = (
                self._get_statistics(figure, axes_list)
                if include_statistics
                else {"per_curve": [], "per_axis": []}
            )

            # Layout information
            layout_info = {
                "shape": [len(real_axes), 1] if len(real_axes) > 0 else [1, 1],
                "size": len(real_axes),
                "nrows": len(real_axes) if len(real_axes) > 0 else 1,
                "ncols": 1,
            }

            # Visual elements
            visual_elements = {
                "lines": [[str(line) for line in ax.lines] for ax in real_axes],
                "axes_styling": [
                    {
                        "has_grid": bool(
                            any(
                                line.get_visible()
                                for line in ax.get_xgridlines() + ax.get_ygridlines()
                            )
                        ),
                        "spine_visibility": {
                            side: bool(spine.get_visible())
                            for side, spine in ax.spines.items()
                        },
                        "tick_density": int(len(ax.get_xticks())),
                    }
                    for ax in real_axes
                ],
                "primary_colors": [str(color["hex"]) for color in colors],
                "accessibility_score": float(
                    self._calculate_accessibility_score(colors)
                ),
            }

            # Domain context
            domain_context = self._infer_domain_context(axes_list)

            # LLM description
            llm_description = self._generate_llm_description(axes_list, statistics)

            # LLM context
            llm_context = self._generate_llm_context(axes_list, statistics)

            # Statistical insights
            statistical_insights = self._generate_statistical_insights(statistics)

            # Pattern analysis
            pattern_analysis = self._generate_pattern_analysis(axes_list)

            # Compose the final output
            modern_output = {
                "figure": figure_info,
                "axes": axes_list,
                "layout": layout_info,
                "colors": colors,
                "statistics": statistics,
                "visual_elements": visual_elements,
                "domain_context": domain_context,
                "llm_description": llm_description,
                "llm_context": llm_context,
                "statistical_insights": statistical_insights,
                "pattern_analysis": pattern_analysis,
            }

            # Data summary - construir después de tener el resultado completo
            modern_output["data_summary"] = build_data_summary_section(modern_output)

            # Return modern format directly for consistency
            return modern_output

        except Exception as e:
            logger.error(f"Error analyzing figure: {str(e)}")
            raise

    def _get_figure_type(self, figure: Any) -> str:
        """Get the type of the matplotlib figure (standardized)."""
        if isinstance(figure, mpl_figure.Figure):
            return "matplotlib.Figure"
        elif isinstance(figure, mpl_axes.Axes):
            return "matplotlib.Axes"
        else:
            return "unknown"

    def _get_dimensions(self, figure: Any) -> Tuple[int, int]:
        """Get the dimensions of the matplotlib figure."""
        try:
            if isinstance(figure, mpl_figure.Figure):
                return figure.get_size_inches()
            elif isinstance(figure, mpl_axes.Axes):
                return figure.figure.get_size_inches()
            else:
                return (0, 0)
        except Exception:
            return (0, 0)

    def _get_title(self, figure: Any) -> Optional[str]:
        """Get the title of the matplotlib figure."""
        try:
            if isinstance(figure, mpl_figure.Figure):
                # Get the main title if it exists
                if figure._suptitle:
                    return figure._suptitle.get_text()
                # Get title from the first axes
                axes = figure.axes
                if axes:
                    return axes[0].get_title()
            elif isinstance(figure, mpl_axes.Axes):
                return figure.get_title()
            return None
        except Exception:
            return None

    def _get_axes(self, figure: Any) -> List[Any]:
        """Get all axes in the matplotlib figure."""
        try:
            if isinstance(figure, mpl_figure.Figure):
                return figure.axes
            elif isinstance(figure, mpl_axes.Axes):
                return [figure]
            else:
                return []
        except Exception:
            return []

    def _get_axes_count(self, figure: Any) -> int:
        """Get the number of axes in the matplotlib figure."""
        return len(self._get_axes(figure))

    def _get_axis_type(self, ax: Any) -> str:
        """Get the type of a matplotlib axis."""
        try:
            if hasattr(ax, "get_xscale"):
                xscale = ax.get_xscale()
                yscale = ax.get_yscale()
                if xscale == "log" or yscale == "log":
                    return "log"
                elif xscale == "symlog" or yscale == "symlog":
                    return "symlog"
                else:
                    return "linear"
            return "unknown"
        except Exception:
            return "unknown"

    def _get_x_label(self, ax: Any) -> Optional[str]:
        """Get the x-axis label."""
        try:
            return ax.get_xlabel()
        except Exception:
            return None

    def _get_y_label(self, ax: Any) -> Optional[str]:
        """Get the y-axis label."""
        try:
            return ax.get_ylabel()
        except Exception:
            return None

    def _get_axis_title(self, ax: Any) -> Optional[str]:
        """Get the title of an individual axis."""
        try:
            return ax.get_title()
        except Exception:
            return None

    def _get_x_range(self, ax: Any) -> Optional[Tuple[float, float]]:
        """Get the x-axis range."""
        try:
            xmin, xmax = ax.get_xlim()
            return (float(xmin), float(xmax))
        except Exception:
            return None

    def _get_y_range(self, ax: Any) -> Optional[Tuple[float, float]]:
        """Get the y-axis range."""
        try:
            ymin, ymax = ax.get_ylim()
            return (float(ymin), float(ymax))
        except Exception:
            return None

    def _has_grid(self, ax: Any) -> bool:
        """Check if the axis has a grid."""
        try:
            return ax.get_xgrid() or ax.get_ygrid()
        except Exception:
            return False

    def _has_legend(self, ax: Any) -> bool:
        """Check if the axis has a legend."""
        try:
            return ax.get_legend() is not None
        except Exception:
            return False

    def _get_data_points(self, figure: Any) -> int:
        """Get the number of data points in the figure."""
        try:
            total_points = 0
            axes = self._get_axes(figure)

            for ax in axes:
                # Count data from lines
                for line in ax.lines:
                    if hasattr(line, "_x") and hasattr(line, "_y"):
                        total_points += len(line._x)

                # Count data from collections (scatter plots)
                for collection in ax.collections:
                    if hasattr(collection, "_offsets"):
                        total_points += len(collection._offsets)

                # Count data from patches (histograms, bar plots)
                for patch in ax.patches:
                    try:
                        if hasattr(patch, "get_height"):
                            height = patch.get_height()
                            if height > 0:
                                total_points += 1
                    except Exception:
                        continue

                # Count data from images
                for image in ax.images:
                    try:
                        if hasattr(image, "get_array"):
                            img_data = image.get_array()
                            if img_data is not None:
                                total_points += img_data.size
                    except Exception:
                        continue

            return total_points
        except Exception:
            return 0

    def _get_data_types(self, figure: Any) -> List[str]:
        """Get the types of data in the figure."""
        data_types = []
        try:
            axes = self._get_axes(figure)

            for ax in axes:
                if ax.lines:
                    data_types.append("line_plot")
                if ax.collections:
                    data_types.append("scatter_plot")
                if ax.patches:
                    data_types.append("histogram")
                if ax.images:
                    data_types.append("image")
                if ax.texts:
                    data_types.append("text")

            return list(set(data_types))
        except Exception:
            return []

    def _detect_axis_type_and_labels(
        self, ax: Any, axis: str = "x"
    ) -> Tuple[str, List[str]]:
        """
        Detecta el tipo de eje y sus etiquetas de forma robusta.

        Args:
            ax: El eje de matplotlib
            axis: 'x' o 'y' para indicar qué eje analizar

        Returns:
            Tuple[str, List[str]]: (tipo_de_eje, lista_de_etiquetas)
        """
        try:
            import pandas as pd

            # Asegurar que los labels estén disponibles
            if hasattr(ax, "figure") and hasattr(ax.figure, "canvas"):
                try:
                    ax.figure.canvas.draw()
                except Exception:
                    pass

            # 1. Obtener etiquetas del eje
            if axis == "x":
                labels = [lbl.get_text().strip() for lbl in ax.get_xticklabels()]
            else:
                labels = [lbl.get_text().strip() for lbl in ax.get_yticklabels()]

            labels = [lbl for lbl in labels if lbl]  # Filtrar etiquetas vacías

            # 2. Buscar en los datos originales
            data_values = []

            # Revisar líneas
            for line in ax.lines:
                if axis == "x" and hasattr(line, "get_xdata"):
                    data = line.get_xdata()
                    if len(data) > 0:
                        data_values.extend(data)
                elif axis == "y" and hasattr(line, "get_ydata"):
                    data = line.get_ydata()
                    if len(data) > 0:
                        data_values.extend(data)

            # Revisar colecciones (scatter plots)
            for collection in ax.collections:
                if hasattr(collection, "get_offsets"):
                    offsets = collection.get_offsets()
                    if offsets is not None and len(offsets) > 0:
                        data_values.extend(offsets[:, 0 if axis == "x" else 1])

            # Revisar patches (barras)
            if axis == "x":
                for patch in ax.patches:
                    if hasattr(patch, "get_x"):
                        data_values.append(patch.get_x())
            else:
                for patch in ax.patches:
                    if hasattr(patch, "get_height"):
                        data_values.append(patch.get_height())

            # 3. Analizar los datos para determinar el tipo
            if len(data_values) > 0:
                data_array = np.array(data_values)

                # Verificar si son fechas
                if np.issubdtype(data_array.dtype, np.datetime64):
                    return "date", [
                        pd.Timestamp(x).strftime("%Y-%m-%d") for x in data_values
                    ]

                # Verificar si son períodos
                if hasattr(data_array, "dtype") and str(data_array.dtype).startswith(
                    "period"
                ):
                    return "period", [str(x) for x in data_values]

                # Verificar si son strings/categorías
                if all(isinstance(x, str) for x in data_values):
                    return "categorical", data_values

                # Si hay etiquetas no numéricas y coinciden con la cantidad de datos
                if labels and len(labels) == len(set(data_values)):
                    try:
                        float("".join(labels))  # Intentar convertir a número
                    except ValueError:
                        # Si no se puede convertir a número, son categorías
                        return "categorical", labels

                # Si los valores son enteros consecutivos y hay etiquetas significativas
                if all(
                    isinstance(x, (int, np.integer))
                    or (isinstance(x, float) and x.is_integer())
                    for x in data_values
                ):
                    unique_values = sorted(set(data_values))
                    if len(unique_values) > 1 and unique_values == list(
                        range(int(min(unique_values)), int(max(unique_values)) + 1)
                    ):
                        if labels and len(labels) >= len(unique_values):
                            try:
                                float("".join(labels[: len(unique_values)]))
                            except ValueError:
                                return "categorical", labels[: len(unique_values)]

                # Si no es ninguno de los anteriores, es numérico
                return "numeric", [str(x) for x in data_values]

            # Si no hay datos pero hay etiquetas no numéricas
            if labels:
                try:
                    float("".join(labels))
                    return "numeric", labels
                except ValueError:
                    return "categorical", labels

            return "numeric", []

        except Exception as e:
            import logging

            logging.getLogger(__name__).warning(f"Error detecting axis type: {str(e)}")
            return "numeric", []

    def _is_histogram(self, ax):
        """
        Lógica migrada desde seaborn_analyzer.py para detectar histogramas.
        Esta función usa la misma heurística robusta que funciona bien en Seaborn.
        """
        if not (hasattr(ax, "patches") and ax.patches):
            return False

        try:
            # Verificar propiedades específicas de histogramas
            num_patches = len(ax.patches)

            # Los histogramas típicamente tienen muchos bins (>= 10)
            if num_patches >= 10:
                return True
            else:
                # Para pocos patches, usar análisis más detallado
                tick_labels = [label.get_text() for label in ax.get_xticklabels()]

                # Verificar si las etiquetas son claramente categóricas (texto no numérico)
                categorical_labels = []
                for label in tick_labels:
                    label_text = label.strip()
                    if label_text and not (
                        label_text.replace(".", "")
                        .replace("-", "")
                        .replace("+", "")
                        .replace("e", "")
                        .replace("E", "")
                        .isdigit()
                    ):
                        categorical_labels.append(label_text)

                # Si hay etiquetas claramente categóricas, es un bar plot
                if (
                    len(categorical_labels) > 0
                    and len(categorical_labels) == num_patches
                ):
                    return False
                else:
                    # Verificar continuidad de los patches (histogramas son continuos)
                    if num_patches > 1:
                        patch_positions = []
                        patch_widths = []
                        for patch in ax.patches:
                            if hasattr(patch, "get_x") and hasattr(patch, "get_width"):
                                patch_positions.append(patch.get_x())
                                patch_widths.append(patch.get_width())

                        if patch_positions and patch_widths:
                            # Verificar si son continuos (sin gaps significativos)
                            sorted_positions = sorted(patch_positions)
                            avg_width = sum(patch_widths) / len(patch_widths)
                            gaps = []
                            for i in range(1, len(sorted_positions)):
                                gap = sorted_positions[i] - (
                                    sorted_positions[i - 1] + avg_width
                                )
                                gaps.append(abs(gap))

                            max_gap = max(gaps) if gaps else 0
                            # Si el gap máximo es menor que 10% del ancho promedio, es continuo (histograma)
                            if max_gap < 0.1 * avg_width:
                                return True
                            else:
                                return False
                        else:
                            return True  # Default para casos ambiguos
                    else:
                        return True  # Un solo patch, probablemente histograma
        except Exception as e:
            # Si falla la detección, usar histograma por defecto
            import logging

            logging.getLogger(__name__).warning(
                f"Error en detección de histograma: {e}"
            )
            return True

    def _is_bar_plot(self, ax):
        """
        Lógica migrada desde seaborn_analyzer.py para detectar bar plots.
        Esta función complementa _is_histogram y usa la misma heurística robusta.
        """
        if not (hasattr(ax, "patches") and ax.patches):
            return False

        try:
            # Si ya se determinó que es histograma, no es bar plot
            if self._is_histogram(ax):
                return False

            # Verificar si hay patches con altura > 0
            heights = [
                patch.get_height()
                for patch in ax.patches
                if hasattr(patch, "get_height")
            ]
            if not any(h > 0 for h in heights):
                return False

            # Verificar etiquetas categóricas
            tick_labels = [label.get_text() for label in ax.get_xticklabels()]
            has_categorical_labels = any(
                label.strip()
                and not label.replace(".", "")
                .replace("-", "")
                .replace("+", "")
                .replace("e", "")
                .replace("E", "")
                .isdigit()
                for label in tick_labels
            )

            # Si tiene etiquetas categóricas claras, es bar plot
            if has_categorical_labels:
                return True

            # Para casos ambiguos, si tiene pocos patches y no es histograma, probablemente es bar plot
            num_patches = len(ax.patches)
            if num_patches <= 20:
                return True

            return False
        except Exception as e:
            # Si falla la detección, no es bar plot
            import logging

            logging.getLogger(__name__).warning(f"Error en detección de bar plot: {e}")
            return False

    def _get_statistics(
        self, figure: Any, axes_list: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get statistical information about the data in the figure."""

        def to_native_type(value):
            """Convierte valores NumPy a tipos Python nativos."""
            if isinstance(value, (np.integer, np.floating)):
                return float(value)
            if isinstance(value, np.bool_):
                return bool(value)
            if isinstance(value, (list, tuple)):
                return [to_native_type(v) for v in value]
            if isinstance(value, dict):
                return {k: to_native_type(v) for k, v in value.items()}
            return value

        statistics = {"per_curve": [], "per_axis": []}

        # Si se proporciona axes_list, usar las estadísticas ya calculadas
        if axes_list:
            for axis_index, ax_info in enumerate(axes_list):
                if "statistics" in ax_info:
                    # Usar las estadísticas del line_analyzer
                    stats = ax_info["statistics"]
                    axis_stats = {
                        "axis_index": axis_index,
                        "title": ax_info.get("title", ""),
                        "data_types": [ax_info.get("plot_type", "unknown")],
                        "mean": stats.get("mean"),
                        "std": stats.get("std"),
                        "min": stats.get("min"),
                        "max": stats.get("max"),
                        "median": stats.get("median"),
                        "data_points": stats.get("data_points"),
                        "range": stats.get("range"),
                        "matrix_data": None,
                        "x_type": "numeric",
                        "y_type": "numeric",
                    }
                    statistics["per_axis"].append(axis_stats)
                    continue

        # Fallback: usar el método original si no hay axes_list
        axes = self._get_axes(figure)

        for axis_index, ax in enumerate(axes):
            plot_types = self._get_data_types(ax)
            plot_type = plot_types[0] if plot_types else None

            # Usar 'statistics' del analyzer si existe (para todos los tipos)
            if isinstance(ax, dict) and "statistics" in ax:
                axis_stats = dict(ax["statistics"])
                axis_stats["axis_index"] = axis_index
                axis_stats["title"] = str(self._get_axis_title(ax))
                axis_stats["data_types"] = [plot_type]
                statistics["per_axis"].append(axis_stats)
                continue

            # Solo generar estadísticas para tipos soportados
            if plot_type in ["line_plot", "scatter_plot"]:
                # Los analizadores específicos ya incluyen estadísticas
                # Crear estadísticas simplificadas para compatibilidad
                axis_stats = {
                    "axis_index": axis_index,
                    "title": str(self._get_axis_title(ax)),
                    "data_types": [plot_type],
                    "data_points": 0,
                    "matrix_data": None,
                    "x_type": "numeric",
                    "y_type": "numeric",
                }

                # Extraer datos básicos para estadísticas
                if plot_type == "line_plot" and ax.lines:
                    # Buscar las estadísticas en el análisis ya realizado
                    # Si no están disponibles, calcular manualmente
                    all_y = []
                    for line in ax.lines:
                        all_y.extend([float(y) for y in line.get_ydata()])

                    if all_y:
                        y_array = np.array(all_y)
                        axis_stats.update(
                            {
                                "mean": float(np.nanmean(y_array)),
                                "std": float(np.nanstd(y_array)),
                                "min": float(np.nanmin(y_array)),
                                "max": float(np.nanmax(y_array)),
                                "median": float(np.nanmedian(y_array)),
                                "data_points": len(all_y),
                            }
                        )

                elif plot_type == "scatter_plot" and ax.collections:
                    all_x, all_y = [], []
                    for collection in ax.collections:
                        if hasattr(collection, "get_offsets"):
                            offsets = collection.get_offsets()
                            if len(offsets) > 0:
                                all_x.extend([float(x) for x in offsets[:, 0]])
                                all_y.extend([float(y) for y in offsets[:, 1]])

                    if all_y:
                        y_array = np.array(all_y)
                        axis_stats.update(
                            {
                                "mean": float(np.nanmean(y_array)),
                                "std": float(np.nanstd(y_array)),
                                "min": float(np.nanmin(y_array)),
                                "max": float(np.nanmax(y_array)),
                                "median": float(np.nanmedian(y_array)),
                                "data_points": len(all_y),
                            }
                        )

                statistics["per_axis"].append(axis_stats)
            elif plot_type in ["bar", "histogram"]:
                # Si no hay 'statistics', poner mensaje mínimo
                axis_stats = {
                    "axis_index": axis_index,
                    "title": str(self._get_axis_title(ax)),
                    "data_types": [plot_type],
                    "data_points": 0,
                    "matrix_data": None,
                    "message": f"Estadísticas no disponibles para tipo '{plot_type}'",
                }
                statistics["per_axis"].append(axis_stats)
            else:
                # Para tipos no soportados, estadísticas mínimas
                axis_stats = {
                    "axis_index": axis_index,
                    "title": str(self._get_axis_title(ax)),
                    "data_types": [plot_type or "unknown"],
                    "data_points": 0,
                    "matrix_data": None,
                    "message": f"Estadísticas no disponibles para tipo '{plot_type}'",
                }
                statistics["per_axis"].append(axis_stats)

        # Convertir todos los valores NumPy a tipos Python nativos
        return to_native_type(statistics)

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness of the data."""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            skewness = np.mean(((data - mean) / std) ** 3)
            return float(skewness)
        except Exception:
            return 0.0

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis of the data."""
        try:
            mean = np.mean(data)
            std = np.std(data)
            if std == 0:
                return 0.0
            kurtosis = np.mean(((data - mean) / std) ** 4) - 3  # Excess kurtosis
            return float(kurtosis)
        except Exception:
            return 0.0

    def _get_colors(self, figure: Any) -> List[dict]:
        """Get the colors used in the figure, with hex and common name if possible. No colors for heatmaps."""

        def hex_to_name(hex_color):
            try:
                import webcolors

                return webcolors.hex_to_name(hex_color)
            except Exception:
                return None

        colors: List[Dict[str, Any]] = []
        try:
            axes = self._get_axes(figure)
            for ax in axes:
                # NO colors from images (heatmaps)
                # Only extract from lines, collections, patches
                # Colors from lines
                for line in ax.lines:
                    if hasattr(line, "_color"):
                        try:
                            color_hex = to_hex(line._color)
                            color_name = hex_to_name(color_hex)
                            if color_hex not in [c["hex"] for c in colors]:
                                colors.append({"hex": color_hex, "name": color_name})
                        except Exception:
                            continue
                # Colors from collections (scatter plots)
                for collection in ax.collections:
                    if hasattr(collection, "_facecolors"):
                        for color in collection._facecolors:
                            try:
                                hex_color = to_hex(color)
                                color_name = hex_to_name(hex_color)
                                if hex_color not in [c["hex"] for c in colors]:
                                    colors.append(
                                        {"hex": hex_color, "name": color_name}
                                    )
                            except Exception:
                                continue
                # Colors from patches (histograms, bar plots)
                for patch in ax.patches:
                    try:
                        if hasattr(patch, "get_facecolor"):
                            facecolor = patch.get_facecolor()
                            if facecolor is not None:
                                try:
                                    hex_color = to_hex(facecolor)
                                    color_name = hex_to_name(hex_color)
                                    if hex_color not in [c["hex"] for c in colors]:
                                        colors.append(
                                            {"hex": hex_color, "name": color_name}
                                        )
                                except Exception:
                                    continue
                    except Exception:
                        continue
        except Exception as e:
            logger.warning(f"Error extracting colors: {str(e)}")
        return colors

    def _get_markers(self, figure: Any) -> List[dict]:
        """Get the markers used in the figure, as readable codes and names."""
        markers: List[Dict[str, Any]] = []
        try:
            axes = self._get_axes(figure)
            for ax in axes:
                for line in ax.lines:
                    marker_code = (
                        line.get_marker() if hasattr(line, "get_marker") else None
                    )
                    if (
                        marker_code
                        and marker_code != "None"
                        and marker_code not in [m["code"] for m in markers]
                    ):
                        try:
                            marker_name = MarkerStyle(marker_code).get_marker()
                        except Exception:
                            marker_name = str(marker_code)
                        markers.append({"code": marker_code, "name": marker_name})
        except Exception as e:
            logger.warning(f"Error extracting markers: {str(e)}")
        return markers

    def _get_line_styles(self, figure: Any) -> List[dict]:
        """Get the line styles used in the figure, with codes and names."""

        def line_style_to_name(style_code):
            """Convert matplotlib line style code to readable name."""
            style_names = {
                "-": "solid",
                "--": "dashed",
                "-.": "dashdot",
                ":": "dotted",
                "None": "none",
                " ": "none",
                "": "none",
            }
            return style_names.get(str(style_code), str(style_code))

        styles: List[Dict[str, Any]] = []
        try:
            axes = self._get_axes(figure)

            for ax in axes:
                for line in ax.lines:
                    if hasattr(line, "_linestyle") and line._linestyle != "None":
                        style_code = line._linestyle
                        style_name = line_style_to_name(style_code)
                        if style_code not in [s["code"] for s in styles]:
                            styles.append({"code": style_code, "name": style_name})

        except Exception as e:
            logger.warning(f"Error extracting line styles: {str(e)}")

        return styles

    def _get_background_color(self, figure: Any) -> Optional[dict]:
        """Get the background color of the figure, with hex and common name if possible."""

        def hex_to_name(hex_color):
            try:
                import webcolors

                return webcolors.hex_to_name(hex_color)
            except Exception:
                return None

        try:
            if isinstance(figure, mpl_figure.Figure):
                bg_color = figure.get_facecolor()
            elif isinstance(figure, mpl_axes.Axes):
                bg_color = figure.get_facecolor()
            else:
                return None

            hex_color = to_hex(bg_color)
            color_name = hex_to_name(hex_color)
            return {"hex": hex_color, "name": color_name}
        except Exception:
            return None

    def _extract_detailed_info(self, figure: Any) -> Dict[str, Any]:
        """Extract detailed information for high detail level."""
        detailed_info = {}
        try:
            axes = self._get_axes(figure)

            detailed_info["line_details"] = []
            detailed_info["collection_details"] = []

            for ax in axes:
                for line in ax.lines:
                    line_detail = {
                        "label": line.get_label(),
                        "color": (
                            to_hex(line._color) if hasattr(line, "_color") else None
                        ),
                        "linewidth": line.get_linewidth(),
                        "linestyle": line.get_linestyle(),
                        "marker": line.get_marker(),
                        "markersize": line.get_markersize(),
                    }
                    detailed_info["line_details"].append(line_detail)

                for collection in ax.collections:
                    collection_detail = {
                        "type": type(collection).__name__,
                        "alpha": collection.get_alpha(),
                        "edgecolors": (
                            [to_hex(c) for c in collection.get_edgecolors()]
                            if hasattr(collection, "get_edgecolors")
                            else []
                        ),
                    }
                    detailed_info["collection_details"].append(collection_detail)

        except Exception as e:
            logger.warning(f"Error extracting detailed info: {str(e)}")

        return detailed_info

    def _get_figure_info(self, figure: Any) -> Dict[str, Any]:
        """Get basic information about the matplotlib figure."""
        try:
            figure_type = self._get_figure_type(figure)
            dimensions = self._get_dimensions(figure)
            title = self._get_title(figure)
            axes_count = self._get_axes_count(figure)

            return {
                "figure_type": figure_type,
                "dimensions": [float(dim) for dim in dimensions],
                "title": title,
                "axes_count": axes_count,
            }
        except Exception as e:
            logger.warning(f"Error getting figure info: {str(e)}")
            return {
                "figure_type": "unknown",
                "dimensions": [0, 0],
                "title": None,
                "axes_count": 0,
            }

    def _get_axis_info(self, figure: Any) -> Dict[str, Any]:
        """Get detailed information about axes, including titles and labels."""
        axis_info = {"axes": [], "figure_title": "", "total_axes": 0}

        try:
            axes = self._get_axes(figure)
            axis_info["total_axes"] = len(axes)

            # Get figure title
            if hasattr(figure, "_suptitle") and figure._suptitle:
                axis_info["figure_title"] = figure._suptitle.get_text()
            elif hasattr(figure, "get_suptitle"):
                axis_info["figure_title"] = figure.get_suptitle()

            for i, ax in enumerate(axes):
                plot_types: List[Dict[str, Any]] = []
                x_type: Optional[str] = None
                y_type: Optional[str] = None

                # Check lines (line plots)
                if hasattr(ax, "lines") and ax.lines:
                    plot_types.append({"type": "line"})
                    for line in ax.lines:
                        x = line.get_xdata()
                        y = line.get_ydata()
                        if x_type is None:
                            import numpy as np

                            if np.issubdtype(np.array(x).dtype, np.datetime64):
                                x_type = "DATE"
                            elif hasattr(x, "dtype") and str(x.dtype).startswith(
                                "period"
                            ):
                                x_type = "PERIOD"
                            elif all(isinstance(val, str) for val in x):
                                x_type = "CATEGORY"
                            else:
                                x_type = "NUMERIC"
                        if y_type is None:
                            import numpy as np

                            if np.issubdtype(np.array(y).dtype, np.datetime64):
                                y_type = "DATE"
                            elif all(isinstance(val, str) for val in y):
                                y_type = "CATEGORY"
                            else:
                                y_type = "NUMERIC"

                # Check collections (scatter plots)
                if hasattr(ax, "collections") and ax.collections:
                    plot_types.append({"type": "scatter"})
                    for collection in ax.collections:
                        if hasattr(collection, "get_offsets"):
                            offsets = collection.get_offsets()
                            if offsets is not None and len(offsets) > 0:
                                x = offsets[:, 0]
                                y = offsets[:, 1]
                                if x_type is None:
                                    import numpy as np

                                    if np.issubdtype(np.array(x).dtype, np.datetime64):
                                        x_type = "DATE"
                                    elif all(isinstance(val, str) for val in x):
                                        x_type = "CATEGORY"
                                    else:
                                        x_type = "NUMERIC"
                                if y_type is None:
                                    import numpy as np

                                    if np.issubdtype(np.array(y).dtype, np.datetime64):
                                        y_type = "DATE"
                                    elif all(isinstance(val, str) for val in y):
                                        y_type = "CATEGORY"
                                    else:
                                        y_type = "NUMERIC"

                # Check patches (bar plots, histograms)
                if hasattr(ax, "patches") and ax.patches:
                    # Determine if it's bar or histogram based on patch properties
                    is_bar = False
                    is_histogram = False

                    for patch in ax.patches:
                        if hasattr(patch, "get_x") and hasattr(patch, "get_height"):
                            # Check if patches are adjacent (bar plot) or overlapping (histogram)
                            if len(ax.patches) > 1:
                                width = patch.get_width()
                                # Simple heuristic: if patches are close together, it's likely a bar plot
                                if width > 0.1:  # Bar plots typically have wider bars
                                    is_bar = True
                                else:
                                    is_histogram = True
                            else:
                                is_bar = True
                            break

                    if is_bar:
                        plot_types.append({"type": "bar"})
                    elif is_histogram:
                        plot_types.append({"type": "histogram"})

                    # For bar plots, check if x-axis has categorical labels
                    if is_bar and hasattr(ax, "get_xticklabels"):
                        try:
                            xticklabels = ax.get_xticklabels()
                            if xticklabels and all(
                                isinstance(label.get_text(), str)
                                for label in xticklabels
                            ):
                                x_type = "CATEGORY"
                            else:
                                x_type = "NUMERIC"
                        except Exception:
                            x_type = "NUMERIC"

                    if y_type is None:
                        y_type = "NUMERIC"

                # Check images (heatmaps)
                if hasattr(ax, "images") and ax.images:
                    plot_types.append({"type": "heatmap"})
                    if x_type is None:
                        x_type = "NUMERIC"
                    if y_type is None:
                        y_type = "NUMERIC"

                # Set default types if not detected
                if x_type is None:
                    x_type = "NUMERIC"
                if y_type is None:
                    y_type = "NUMERIC"

                # Basic axis information
                axis_info = {
                    "plot_types": plot_types,
                    "xlabel": self._get_x_label(ax),
                    "ylabel": self._get_y_label(ax),
                    "title": self._get_axis_title(ax),
                    "x_type": x_type,
                    "y_type": y_type,
                    "x_range": self._get_x_range(ax),
                    "y_range": self._get_y_range(ax),
                    "has_grid": self._has_grid(ax),
                    "has_legend": self._has_legend(ax),
                    "spine_visibility": {
                        side: bool(spine.get_visible())
                        for side, spine in ax.spines.items()
                    },
                    "tick_density": int(len(ax.get_xticks())),
                }

                # Check if axis has data
                try:
                    has_data = False

                    # Check collections (scatter plots, etc.)
                    if hasattr(ax, "collections") and ax.collections:
                        has_data = True

                    # Check lines
                    if hasattr(ax, "lines") and ax.lines:
                        has_data = True

                    # Check patches (histograms, bar plots)
                    if hasattr(ax, "patches") and ax.patches:
                        has_data = True

                    # Check images (heatmaps)
                    if hasattr(ax, "images") and ax.images:
                        has_data = True

                    axis_info["has_data"] = has_data
                except Exception:
                    axis_info["has_data"] = False

                axis_info["axis_index"] = i
                axis_info["index"] = i
                axis_info["title"] = str(self._get_axis_title(ax))
                axis_info["x_label"] = str(self._get_x_label(ax))
                axis_info["y_label"] = str(self._get_y_label(ax))
                axis_info["x_lim"] = [float(x) for x in ax.get_xlim()]
                axis_info["y_lim"] = [float(y) for y in ax.get_ylim()]
                axis_info["has_grid"] = self._has_grid(ax)
                axis_info["has_legend"] = self._has_legend(ax)
                axis_info["spine_visibility"] = {
                    side: bool(spine.get_visible()) for side, spine in ax.spines.items()
                }
                axis_info["tick_density"] = int(len(ax.get_xticks()))

                axis_info["plot_types"] = plot_types
                axis_info["x_type"] = x_type
                axis_info["y_type"] = y_type

                axis_info["axes"].append(axis_info)

        except Exception as e:
            logger.warning(f"Error getting axis info: {str(e)}")

        return axis_info

    def _calculate_accessibility_score(self, colors: List[Dict[str, Any]]) -> float:
        """Calcula un puntaje de accesibilidad basado en los colores."""
        # Placeholder: podrías implementar un cálculo real basado en contraste, etc.
        if not colors:
            return 1.0
        return 0.85

    def _infer_domain_context(self, axes_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Infiere el contexto del dominio basado en los ejes."""
        domain_context = {
            "likely_domain": "general",
            "purpose": "analysis",
            "target_audience": "general",
            "key_metrics": [],
        }

        for ax in axes_list:
            # Inferir dominio basado en etiquetas
            x_label = ax.get("x_label", "").lower()
            y_label = ax.get("y_label", "").lower()

            if any(
                keyword in x_label + y_label
                for keyword in ["time", "date", "month", "year"]
            ):
                domain_context["likely_domain"] = "temporal"
            elif any(
                keyword in x_label + y_label
                for keyword in ["revenue", "cost", "profit", "sales", "usd", "$"]
            ):
                domain_context["likely_domain"] = "financial"
            elif any(
                keyword in x_label + y_label
                for keyword in ["count", "frequency", "number"]
            ):
                domain_context["likely_domain"] = "statistical"

        return domain_context

    def _generate_llm_description(
        self, axes_list: List[Dict[str, Any]], statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera descripción para LLM."""
        # Si los ejes ya tienen descripción LLM, usar el primero
        for ax in axes_list:
            if "llm_description" in ax:
                return ax["llm_description"]

        # Fallback genérico
        return {
            "one_sentence_summary": "Data visualization showing relationships between variables.",
            "structured_analysis": {
                "what": "Data visualization",
                "when": "Point-in-time analysis",
                "why": "Data analysis and pattern recognition",
                "how": "Through visual representation of data points",
            },
            "key_insights": [],  # Los insights vendrán de los analizadores específicos
        }

    def _generate_llm_context(
        self, axes_list: List[Dict[str, Any]], statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera contexto para LLM."""
        # Si los ejes ya tienen contexto LLM, usar el primero
        for ax in axes_list:
            if "llm_context" in ax:
                return ax["llm_context"]

        # Fallback genérico
        return {
            "interpretation_hints": generate_unified_interpretation_hints(
                {
                    "general_analysis": "Analyze the data patterns and relationships",
                    "pattern_recognition": "Look for trends, outliers, and significant features",
                    "statistical_analysis": "Consider the scale and context of the variables",
                }
            ),
            "analysis_suggestions": [
                "Examine statistical properties of the data",
                "Identify key patterns and anomalies",
                "Consider domain-specific interpretations",
            ],
            "common_questions": [
                "What patterns are visible in the data?",
                "Are there any significant trends or outliers?",
                "What insights can be drawn from this visualization?",
            ],
            "related_concepts": [
                "data analysis",
                "statistical visualization",
                "pattern recognition",
            ],
        }

    def _generate_data_summary(self, axes_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera el resumen de datos basado en los ejes."""
        total_data_points = 0
        x_data = []
        y_data = []
        x_type = None
        y_type = None

        for ax in axes_list:
            # Para line plots - usar la estructura de line_analyzer
            if ax.get("plot_type") == "line" and "lines" in ax:
                # Usar estadísticas del line_analyzer si están disponibles
                if "stats" in ax:
                    stats = ax["stats"]
                    data_quality = stats.get("data_quality", {})
                    total_data_points += data_quality.get("total_points", 0)
                else:
                    # Fallback: contar puntos de datos de las líneas
                    for line in ax["lines"]:
                        ydata = line.get("ydata", [])
                        total_data_points += len(ydata)

                # Siempre extraer x_data y y_data de las líneas para data_ranges y missing_values
                for line in ax["lines"]:
                    xdata = line.get("xdata", [])
                    ydata = line.get("ydata", [])
                    x_data.extend(xdata)
                    y_data.extend(ydata)

                x_type = "numeric"
                y_type = "numeric"

            # Para scatter plots - usar la estructura de scatter_analyzer
            elif ax.get("plot_type") == "scatter" and "collections" in ax:
                for collection in ax["collections"]:
                    x_points = collection.get("x_data", [])
                    y_points = collection.get("y_data", [])
                    total_data_points += len(x_points)
                    x_data.extend(x_points)
                    y_data.extend(y_points)
                x_type = "numeric"
                y_type = "numeric"

            # Para histogramas - usar la estructura de histogram_analyzer
            elif ax.get("plot_type") == "histogram" and "stats" in ax:
                stats = ax.get("stats", {})
                data_quality = stats.get("data_quality", {})
                # Para histogramas, usar total_points (que es el número de bins)
                total_data_points += data_quality.get("total_points", 0)

                # Extraer rangos de datos para histogramas
                if "bins" in ax:
                    bin_centers = [
                        bin_data.get("bin_center", 0) for bin_data in ax["bins"]
                    ]
                    frequencies = [
                        bin_data.get("frequency", 0) for bin_data in ax["bins"]
                    ]
                    x_data.extend(bin_centers)
                    y_data.extend(frequencies)

                x_type = "numeric"
                y_type = "numeric"

            # Para bar plots - usar la estructura de bar_analyzer
            elif ax.get("plot_type") == "bar" and "stats" in ax:
                stats = ax.get("stats", {})
                data_quality = stats.get("data_quality", {})
                total_data_points += data_quality.get("total_points", 0)

                # Extraer rangos de datos para bar plots
                if "bars" in ax:
                    heights = [bar_data.get("height", 0) for bar_data in ax["bars"]]
                    # Para bar plots, usar índices como x_data y heights como y_data
                    x_data.extend(range(len(heights)))
                    y_data.extend(heights)

                x_type = "categorical"
                y_type = "numeric"

        return {
            "total_data_points": total_data_points,
            "data_ranges": {
                "x": {
                    "min": float(min(x_data)) if x_data else None,
                    "max": float(max(x_data)) if x_data else None,
                    "type": x_type,
                },
                "y": {
                    "min": float(min(y_data)) if y_data else None,
                    "max": float(max(y_data)) if y_data else None,
                    "type": y_type,
                },
            },
            "missing_values": {
                "x": sum(
                    1
                    for x in x_data
                    if x is None or (isinstance(x, float) and np.isnan(x))
                ),
                "y": sum(
                    1
                    for y in y_data
                    if y is None or (isinstance(y, float) and np.isnan(y))
                ),
            },
            "x_type": x_type,
            "y_type": y_type,
        }

    def _generate_statistical_insights(
        self, statistics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera insights estadísticos basados en las estadísticas."""
        insights = {}

        # Buscar estadísticas en per_axis o directamente en los ejes
        if "per_axis" in statistics and statistics["per_axis"]:
            axis_stats = statistics["per_axis"][0]
            if "mean" in axis_stats and axis_stats["mean"] is not None:
                insights["central_tendency"] = {
                    "mean": axis_stats["mean"],
                    "median": axis_stats.get("median"),
                    "mode": None,  # Placeholder
                }
            if "std" in axis_stats and axis_stats["std"] is not None:
                insights["variability"] = {
                    "standard_deviation": axis_stats["std"],
                    "variance": axis_stats.get("std", 0) ** 2,
                }

        return insights

    def _generate_pattern_analysis(
        self, axes_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        pattern_info = {
            "pattern_type": None,
            "confidence_score": None,
            "equation_estimate": None,
            "shape_characteristics": {},
        }

        # Buscar el primer axis con información de patterns válida
        for ax in axes_list:
            if ax.get("pattern"):
                current_pattern = ax["pattern"]

                # Para line plots
                if ax.get("plot_type") == "line":
                    pattern_info.update(
                        {
                            "pattern_type": current_pattern.get("pattern_type"),
                            "confidence_score": current_pattern.get("confidence_score"),
                            "equation_estimate": current_pattern.get(
                                "equation_estimate"
                            ),
                        }
                    )

                    # Usar las shape_characteristics calculadas en el analyzer específico
                    pattern_info["shape_characteristics"] = current_pattern.get(
                        "shape_characteristics", {}
                    )
                    return pattern_info

                # Para scatter plots
                elif ax.get("plot_type") == "scatter":
                    pattern_info.update(
                        {
                            "pattern_type": current_pattern.get("pattern_type"),
                            "confidence_score": current_pattern.get("confidence_score"),
                            "equation_estimate": current_pattern.get(
                                "equation_estimate"
                            ),
                        }
                    )

                    # Usar las shape_characteristics calculadas en el analyzer específico
                    pattern_info["shape_characteristics"] = current_pattern.get(
                        "shape_characteristics", {}
                    )
                    return pattern_info

                # Para bar plots
                elif ax.get("plot_type") == "bar":
                    pattern_info.update(
                        {
                            "pattern_type": current_pattern.get("pattern_type"),
                            "confidence_score": current_pattern.get("confidence_score"),
                            "equation_estimate": current_pattern.get(
                                "equation_estimate"
                            ),
                        }
                    )

                    # Usar las shape_characteristics calculadas en el analyzer específico
                    pattern_info["shape_characteristics"] = current_pattern.get(
                        "shape_characteristics", {}
                    )
                    return pattern_info

                # Para histogramas
                elif ax.get("plot_type") == "histogram":
                    pattern_info.update(
                        {
                            "pattern_type": current_pattern.get("pattern_type"),
                            "confidence_score": current_pattern.get("confidence_score"),
                            "equation_estimate": current_pattern.get(
                                "equation_estimate"
                            ),
                        }
                    )

                    # Usar las shape_characteristics calculadas en el analyzer específico
                    pattern_info["shape_characteristics"] = current_pattern.get(
                        "shape_characteristics", {}
                    )
                    return pattern_info

        # Si no se encontró información de patterns, usar valores por defecto basados en el tipo
        for ax in axes_list:
            if ax.get("plot_type") == "line":
                pattern_info["pattern_type"] = "trend"
                pattern_info["confidence_score"] = 0.5
                return pattern_info
            elif ax.get("plot_type") == "scatter":
                pattern_info["pattern_type"] = "distribution"
                pattern_info["confidence_score"] = 0.5
                return pattern_info
            elif ax.get("plot_type") == "bar":
                pattern_info["pattern_type"] = "categorical_distribution"
                pattern_info["confidence_score"] = 0.7
                return pattern_info
            elif ax.get("plot_type") == "histogram":
                pattern_info["pattern_type"] = "frequency_distribution"
                pattern_info["confidence_score"] = 0.6
                return pattern_info

        return pattern_info

    def _adapt_to_legacy_format(
        self, modern_output: Dict[str, Any], axes_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Adapta el output moderno al formato compatible con el formatter semántico."""

        # Crear el formato compatible para axes
        legacy_axes = []
        for ax in axes_list:
            if ax.get("plot_type") in ["line", "scatter", "bar", "histogram"]:
                # Usar los datos ricos de los analizadores específicos
                legacy_ax = {
                    "title": ax.get("title", ""),
                    "xlabel": ax.get("x_label", ""),
                    "ylabel": ax.get("y_label", ""),
                    "x_type": "numeric",
                    "y_type": "numeric",
                    "has_grid": ax.get("has_grid", False),
                    "has_legend": ax.get("has_legend", False),
                    "x_range": ax.get("x_lim", [0, 1]),
                    "y_range": ax.get("y_lim", [0, 1]),
                    "plot_types": [{"type": ax.get("plot_type", "unknown")}],
                    "pattern": ax.get("pattern", {}),
                    "domain_context": ax.get("domain_context", {}),
                    "stats": ax.get("statistics", {}),
                }

                # Agregar curve_points basado en el tipo
                if ax.get("plot_type") == "line" and "lines" in ax:
                    curve_points = []
                    for line in ax["lines"]:
                        curve_points.append(
                            {
                                "x": line.get("xdata", []),
                                "y": line.get("ydata", []),
                                "label": line.get("label", ""),
                            }
                        )
                    legacy_ax["curve_points"] = curve_points

                elif ax.get("plot_type") == "scatter" and "collections" in ax:
                    curve_points = []
                    for collection in ax["collections"]:
                        curve_points.append(
                            {
                                "x": collection.get("x_data", []),
                                "y": collection.get("y_data", []),
                                "label": collection.get("label", ""),
                            }
                        )
                    legacy_ax["curve_points"] = curve_points

                elif ax.get("plot_type") == "bar" and "bars" in ax:
                    curve_points = []
                    categories = ax.get("categories", [])
                    bars = ax.get("bars", [])
                    for i, bar in enumerate(bars):
                        label = categories[i] if i < len(categories) else f"Bar_{i}"
                        curve_points.append(
                            {
                                "x": [bar.get("x_center", i)],
                                "y": [bar.get("height", 0)],
                                "label": label,
                            }
                        )
                    legacy_ax["curve_points"] = curve_points

                elif ax.get("plot_type") == "histogram" and "bins" in ax:
                    curve_points = []
                    bins = ax.get("bins", [])
                    for bin_data in bins:
                        curve_points.append(
                            {
                                "x": [bin_data.get("bin_center", 0)],
                                "y": [bin_data.get("frequency", 0)],
                                "label": f"Bin_{bin_data.get('bin_index', 0)}",
                            }
                        )
                    legacy_ax["curve_points"] = curve_points

                else:
                    legacy_ax["curve_points"] = []

                legacy_axes.append(legacy_ax)
            else:
                # Para tipos no soportados, formato mínimo
                legacy_axes.append(
                    {
                        "title": "",
                        "xlabel": "",
                        "ylabel": "",
                        "x_type": "unknown",
                        "y_type": "unknown",
                        "has_grid": False,
                        "has_legend": False,
                        "x_range": None,
                        "y_range": None,
                        "plot_types": [],
                        "curve_points": [],
                        "pattern": None,
                        "domain_context": None,
                        "stats": None,
                    }
                )

        # Estructura compatible con el formatter semántico
        return {
            "figure_type": "matplotlib",
            "title": modern_output["figure"].get("title", ""),
            "axes": legacy_axes,
            "basic_info": modern_output["figure"],
            "axes_info": legacy_axes,
            "data_info": {
                "plot_types": [
                    pt for ax in legacy_axes for pt in ax.get("plot_types", [])
                ],
                "statistics": modern_output["statistics"],
            },
            "visual_info": {"colors": modern_output["colors"]},
            "statistics": modern_output["statistics"],
            "layout": modern_output["layout"],
            "visual_elements": modern_output["visual_elements"],
            "domain_context": modern_output["domain_context"],
            "llm_description": modern_output["llm_description"],
            "llm_context": modern_output["llm_context"],
            "data_summary": modern_output["data_summary"],
            "statistical_insights": modern_output["statistical_insights"],
            "pattern_analysis": modern_output["pattern_analysis"],
        }
