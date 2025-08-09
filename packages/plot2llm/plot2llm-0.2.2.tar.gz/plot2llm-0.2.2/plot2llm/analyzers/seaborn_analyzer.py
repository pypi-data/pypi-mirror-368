"""
Seaborn-specific analyzer for extracting information from seaborn figures.
"""

import logging
import warnings
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.axes as mpl_axes
import matplotlib.figure as mpl_figure
import numpy as np
from matplotlib.colors import to_hex

from plot2llm.analyzers.bar_analyzer import analyze as analyze_bar
from plot2llm.analyzers.histogram_analyzer import analyze as analyze_histogram
from plot2llm.analyzers.line_analyzer import analyze as analyze_line
from plot2llm.analyzers.scatter_analyzer import analyze as analyze_scatter
from plot2llm.sections.data_summary_section import build_data_summary_section
from plot2llm.utils import generate_unified_interpretation_hints, serialize_axis_values

from .base_analyzer import BaseAnalyzer

# Configure numpy to suppress warnings
np.seterr(all="ignore")  # Suppress all numpy warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

logger = logging.getLogger(__name__)


class SeabornAnalyzer(BaseAnalyzer):
    """
    Analyzer specifically designed for seaborn figures.

    Seaborn is built on top of matplotlib, so this analyzer extends
    matplotlib functionality with seaborn-specific features.
    """

    # Constants for axis types
    NUMERIC = "numeric"
    CATEGORY = "categorical"
    DATE = "date"
    PERIOD = "period"

    def __init__(self):
        """Initialize the SeabornAnalyzer."""
        super().__init__()
        self.supported_types = [
            "matplotlib.figure.Figure",
            "matplotlib.axes.Axes",
            "seaborn.axisgrid.FacetGrid",
            "seaborn.axisgrid.PairGrid",
            "seaborn.axisgrid.JointGrid",
        ]
        logger.debug("SeabornAnalyzer initialized")

    def analyze(
        self,
        figure: Any,
        detail_level: str = "medium",
        include_data: bool = True,
        include_colors: bool = True,
        include_statistics: bool = True,
    ) -> dict:
        """Analyze a seaborn figure and extract comprehensive information."""
        import matplotlib.axes as mpl_axes
        import matplotlib.figure as mpl_figure

        if figure is None:
            raise ValueError("Invalid figure object: None")
        if not (
            isinstance(figure, mpl_figure.Figure) or isinstance(figure, mpl_axes.Axes)
        ):
            raise ValueError("Not a seaborn/matplotlib figure")
        try:
            # Basic info
            figure_info = self._get_figure_info(figure)
            axes_list = []
            real_axes = self._get_axes(figure)
            for ax in real_axes:
                plot_types = self._get_data_types(ax)
                plot_type = plot_types[0] if plot_types else None

                # Detectar tipos de eje
                x_type, y_type, x_labels, y_labels = self._detect_axis_type_and_labels(
                    ax
                )

                # Lógica de detección migrada desde matplotlib_analyzer.py
                # Priorizar histogramas sobre bar plots (misma lógica que Matplotlib)
                if self._is_histogram(ax):
                    axes_section = analyze_histogram(ax, x_type, y_type)
                elif self._is_bar_plot(ax):
                    axes_section = analyze_bar(ax, x_type, y_type)
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

                # Convertir plot_type a plot_types para compatibilidad
                if "plot_type" in axes_section:
                    axes_section["plot_types"] = [{"type": axes_section["plot_type"]}]

                axes_list.append(axes_section)

            colors = self._get_colors(figure) if include_colors else []
            statistics = (
                self._get_statistics(figure)
                if include_statistics
                else {"per_curve": [], "per_axis": []}
            )
            layout_info = {
                "shape": [len(real_axes), 1] if len(real_axes) > 0 else [1, 1],
                "size": len(real_axes),
                "nrows": len(real_axes) if len(real_axes) > 0 else 1,
                "ncols": 1,
            }
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
            domain_context = self._infer_domain_context(axes_list)
            llm_description = self._generate_llm_description(axes_list, statistics)
            llm_context = self._generate_llm_context(axes_list, statistics)
            statistical_insights = self._generate_statistical_insights(statistics)
            pattern_analysis = self._generate_pattern_analysis(axes_list)

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
            import logging

            logging.getLogger(__name__).error(
                f"Error analyzing seaborn figure: {str(e)}"
            )
            raise

    def _get_figure_type(self, figure: Any) -> str:
        """Get the type of the seaborn figure."""
        try:
            # Check for seaborn-specific types
            if hasattr(figure, "__class__"):
                class_name = figure.__class__.__name__
                module_name = figure.__class__.__module__

                # Debug logging
                logger.debug(
                    f"SeabornAnalyzer checking figure: class_name={class_name}, module_name={module_name}"
                )

                if "seaborn" in module_name:
                    if "FacetGrid" in class_name:
                        logger.debug("Detected FacetGrid")
                        return "seaborn.FacetGrid"
                    if "PairGrid" in class_name:
                        logger.debug("Detected PairGrid")
                        return "seaborn.PairGrid"
                    if "JointGrid" in class_name:
                        logger.debug("Detected JointGrid")
                        return "seaborn.JointGrid"
                    if "Heatmap" in class_name:
                        logger.debug("Detected Heatmap")
                        return "seaborn.Heatmap"
                    if "ClusterGrid" in class_name:
                        logger.debug("Detected ClusterGrid")
                        return "seaborn.ClusterGrid"
                    logger.debug(f"Detected generic seaborn: {class_name}")
                    return f"seaborn.{class_name}"

                # Fall back to matplotlib types
                if isinstance(figure, mpl_figure.Figure):
                    logger.debug("Detected matplotlib.Figure")
                    return "matplotlib.Figure"
                if isinstance(figure, mpl_axes.Axes):
                    logger.debug("Detected matplotlib.Axes")
                    return "matplotlib.Axes"

            logger.debug("No specific type detected, returning unknown")
            return "unknown"
        except Exception as e:
            logger.warning(f"Error in _get_figure_type: {str(e)}")
            return "unknown"

    def _get_dimensions(self, figure: Any) -> Tuple[int, int]:
        """Get the dimensions of the seaborn figure."""
        try:
            # Handle seaborn grid objects
            if hasattr(figure, "fig"):
                return figure.fig.get_size_inches()
            if hasattr(figure, "figure"):
                return figure.figure.get_size_inches()
            if isinstance(figure, mpl_figure.Figure):
                return figure.get_size_inches()
            if isinstance(figure, mpl_axes.Axes):
                return figure.figure.get_size_inches()
            return (0, 0)
        except Exception:
            return (0, 0)

    def _get_title(self, figure: Any) -> Optional[str]:
        """Get the title of the seaborn figure."""
        try:
            # Handle seaborn grid objects
            if hasattr(figure, "fig"):
                fig = figure.fig
                if getattr(fig, "_suptitle", None):
                    return fig._suptitle.get_text()
                if fig.axes:
                    return fig.axes[0].get_title()
            if hasattr(figure, "figure"):
                fig = figure.figure
                if getattr(fig, "_suptitle", None):
                    return fig._suptitle.get_text()
                if fig.axes:
                    return fig.axes[0].get_title()
            if isinstance(figure, mpl_figure.Figure):
                if getattr(figure, "_suptitle", None):
                    return figure._suptitle.get_text()
                if figure.axes:
                    return figure.axes[0].get_title()
            if isinstance(figure, mpl_axes.Axes):
                return figure.get_title()
            return None
        except Exception:
            return None

    def _get_axes(self, figure: Any) -> List[Any]:
        """Get all axes in the seaborn figure."""
        try:
            # Handle seaborn grid objects
            if hasattr(figure, "axes"):
                axes = figure.axes
                # Check if axes is a numpy array or list
                if hasattr(axes, "flatten"):
                    return axes.flatten().tolist()
                if isinstance(axes, list):
                    return axes
                return []
            if hasattr(figure, "fig"):
                return figure.fig.axes
            if hasattr(figure, "figure"):
                return figure.figure.axes
            if isinstance(figure, mpl_figure.Figure):
                return figure.axes
            if isinstance(figure, mpl_axes.Axes):
                return [figure]
            return []
        except Exception:
            return []

    def _get_axes_count(self, figure: Any) -> int:
        """Get the number of axes in the seaborn figure."""
        return len(self._get_axes(figure))

    def _get_figure_info(self, figure: Any) -> Dict[str, Any]:
        """Get basic information about the seaborn figure."""
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

    def _extract_seaborn_info(self, figure: Any) -> Dict[str, Any]:
        """Extract seaborn-specific information."""
        seaborn_info = {}

        try:
            # Detect seaborn plot types
            plot_type = self._detect_seaborn_plot_type(figure)
            seaborn_info["plot_type"] = plot_type

            # Extract grid information for FacetGrid, PairGrid, etc.
            if hasattr(figure, "axes"):
                axes = figure.axes
                # Handle both numpy arrays and lists
                if hasattr(axes, "shape"):
                    seaborn_info["grid_shape"] = axes.shape
                    seaborn_info["grid_size"] = axes.size
                elif isinstance(axes, list):
                    seaborn_info["grid_shape"] = (len(axes), 1)
                    seaborn_info["grid_size"] = len(axes)

            # Extract color palette information
            if hasattr(figure, "colormap"):
                seaborn_info["colormap"] = str(figure.colormap)

            # Extract facet information
            if hasattr(figure, "col_names"):
                seaborn_info["facet_columns"] = figure.col_names
            if hasattr(figure, "row_names"):
                seaborn_info["facet_rows"] = figure.row_names

            # Extract pair plot information
            if hasattr(figure, "x_vars"):
                seaborn_info["x_variables"] = figure.x_vars
            if hasattr(figure, "y_vars"):
                seaborn_info["y_variables"] = figure.y_vars

        except Exception as e:
            logger.warning(f"Error extracting seaborn info: {str(e)}")

        return seaborn_info

    def _detect_seaborn_plot_type(self, figure: Any) -> str:
        """Detect seaborn plot type from the figure object."""
        try:
            if hasattr(figure, "__class__"):
                class_name = figure.__class__.__name__
                module_name = figure.__class__.__module__
                if "seaborn" in module_name:
                    if "FacetGrid" in class_name:
                        return "FacetGrid"
                    if "PairGrid" in class_name:
                        return "PairGrid"
                    if "JointGrid" in class_name:
                        return "JointGrid"
                    if "Heatmap" in class_name:
                        return "heatmap"
                    if "ClusterGrid" in class_name:
                        return "clustermap"
                    return class_name
            # Fallback: try to detect from axes
            return self._detect_plot_type_from_axes(figure)
        except Exception:
            return "unknown"

    def _detect_plot_type_from_axes(self, figure: Any) -> str:
        """Detect plot type by examining the axes content."""
        try:
            axes = self._get_axes(figure)
            if not axes:
                return "unknown"
            ax = axes[0]
            # Check for heatmap (QuadMesh)
            for collection in ax.collections:
                if (
                    collection.__class__.__name__ == "QuadMesh"
                    and hasattr(collection, "get_array")
                    and collection.get_array() is not None
                ):
                    return "heatmap"
            # Check for heatmap (has image)
            if hasattr(ax, "images") and ax.images:
                return "heatmap"
            # Check for scatter plot (has collections with offsets)
            if hasattr(ax, "collections") and ax.collections:
                for collection in ax.collections:
                    if hasattr(collection, "get_offsets"):
                        offsets = collection.get_offsets()
                        if offsets is not None and len(offsets) > 0:
                            return "scatter_plot"
            # Check for line plot
            if hasattr(ax, "lines") and ax.lines:
                return "line_plot"
            # Check for bar plot (has patches)
            if hasattr(ax, "patches") and ax.patches:
                return "bar_plot"
            # Check for histogram (has patches and specific characteristics)
            if hasattr(ax, "patches") and ax.patches:
                return "histogram"
            return "unknown_seaborn_plot"
        except Exception:
            return "unknown_seaborn_plot"

    def _get_data_points(self, figure: Any) -> int:
        """Get the number of data points in the seaborn figure."""
        try:
            total_points = 0
            axes = self._get_axes(figure)

            for ax in axes:
                # Count data from images (heatmaps)
                for image in ax.images:
                    try:
                        if hasattr(image, "get_array"):
                            img_data = image.get_array()
                            if img_data is not None:
                                total_points += img_data.size
                    except Exception:
                        continue

                # Count data from collections (scatter plots, etc.)
                for collection in ax.collections:
                    if hasattr(collection, "get_offsets"):
                        offsets = collection.get_offsets()
                        if offsets is not None:
                            total_points += len(offsets)

                # Count data from lines
                for line in ax.lines:
                    if hasattr(line, "get_xdata"):
                        xdata = line.get_xdata()
                        if xdata is not None:
                            total_points += len(xdata)

                # Count data from patches (histograms, bar plots)
                for _ in ax.patches:
                    total_points += 1

            return total_points
        except Exception:
            return 0

    def _get_data_types(self, figure: Any) -> List[str]:
        data_types = set()
        try:
            axes = self._get_axes(figure)
            for ax in axes:
                # Check for heatmaps first (QuadMesh)
                is_heatmap = False
                for collection in ax.collections:
                    if (
                        collection.__class__.__name__ == "QuadMesh"
                        and hasattr(collection, "get_array")
                        and collection.get_array() is not None
                    ):
                        data_types.add("heatmap")
                        is_heatmap = True
                        break
                if not is_heatmap and hasattr(ax, "images") and ax.images:
                    for image in ax.images:
                        if (
                            hasattr(image, "get_array")
                            and image.get_array() is not None
                        ):
                            data_types.add("heatmap")
                            is_heatmap = True
                            break
                if is_heatmap:
                    continue  # Skip other types if heatmap
                # Check for different types of plots (only if not a heatmap)
                if ax.collections:
                    for collection in ax.collections:
                        if hasattr(collection, "get_offsets"):
                            offsets = collection.get_offsets()
                            if offsets is not None and len(offsets) > 0:
                                data_types.add("scatter_plot")
                                break
                if ax.lines:
                    data_types.add("line_plot")
                if ax.patches:
                    data_types.add("histogram")
                if ax.texts:
                    if "heatmap" not in data_types:
                        data_types.add("text")
            plot_type = self._detect_seaborn_plot_type(figure)
            if plot_type != "unknown":
                data_types.add(plot_type)
        except Exception as e:
            logger.warning(f"Error getting data types: {str(e)}")
        return list(data_types)

    def _get_statistics(self, figure: Any) -> Dict[str, Any]:
        """Get statistical information about the data in the seaborn figure, per curve and per axis."""
        stats = {"per_curve": [], "per_axis": []}
        try:
            axes = self._get_axes(figure)
            for i, ax in enumerate(axes):
                axis_stats = {
                    "axis_index": i,
                    "title": (
                        ax.get_title()
                        if hasattr(ax, "get_title") and ax.get_title()
                        else f"Subplot {i+1}"
                    ),
                    "data_types": [],
                    "data_points": 0,
                    "matrix_data": None,
                }
                # Extraer puntos de la curva para este eje
                curve_points = []
                x_type = None
                # Line plots
                if hasattr(ax, "lines") and ax.lines:
                    for line in ax.lines:
                        x = line.get_xdata()
                        y = line.get_ydata()
                        x_serial = serialize_axis_values(x)
                        y_serial = serialize_axis_values(y)
                        if x_type is None:
                            if np.issubdtype(np.array(x).dtype, np.datetime64):
                                x_type = "date"
                            elif hasattr(x, "dtype") and str(x.dtype).startswith(
                                "period"
                            ):
                                x_type = "period"
                            elif all(isinstance(val, str) for val in x_serial):
                                x_type = "categorical"
                            else:
                                x_type = "numeric"
                        curve_points.append(
                            {"x": x_serial, "y": y_serial, "label": line.get_label()}
                        )
                # Scatter plots
                if hasattr(ax, "collections") and ax.collections:
                    for collection in ax.collections:
                        if hasattr(collection, "get_offsets"):
                            offsets = collection.get_offsets()
                            if offsets is not None and len(offsets) > 0:
                                x = offsets[:, 0]
                                y = offsets[:, 1]
                                x_serial = serialize_axis_values(x)
                                y_serial = serialize_axis_values(y)
                                if x_type is None:
                                    if np.issubdtype(np.array(x).dtype, np.datetime64):
                                        x_type = "date"
                                    elif all(isinstance(val, str) for val in x_serial):
                                        x_type = "categorical"
                                    else:
                                        x_type = "numeric"
                                curve_points.append(
                                    {
                                        "x": x_serial,
                                        "y": y_serial,
                                        "label": getattr(
                                            collection, "get_label", lambda: None
                                        )(),
                                    }
                                )
                # Bar/histogram
                if hasattr(ax, "patches") and ax.patches:
                    for patch in ax.patches:
                        if hasattr(patch, "get_x") and hasattr(patch, "get_height"):
                            x = patch.get_x()
                            y = patch.get_height()
                            x_serial = serialize_axis_values([x])
                            y_serial = serialize_axis_values([y])
                            if x_type is None:
                                x_type = "numeric"
                            curve_points.append(
                                {
                                    "x": x_serial,
                                    "y": y_serial,
                                    "label": getattr(
                                        patch, "get_label", lambda: None
                                    )(),
                                }
                            )
                # Determinar si se pueden calcular estadísticas
                can_calc_stats = x_type in (None, "numeric")
                # Solo calcular estadísticas sobre Y si X es fecha/categoría
                y_data = []
                for pt in curve_points:
                    y_data.extend(pt["y"])
                y_data = np.array(y_data)
                if (
                    can_calc_stats
                    and len(y_data) > 0
                    and np.issubdtype(y_data.dtype, np.number)
                ):
                    # Calculate local variance with better handling of small datasets
                    local_var = None
                    if len(y_data) >= 2:
                        # Use at least 2 points, but no more than 10% of data
                        sample_size = max(2, min(len(y_data) // 10, len(y_data)))
                        if sample_size > 1:
                            local_var = float(np.nanvar(y_data[:sample_size]))

                    axis_stats.update(
                        {
                            "mean": float(np.nanmean(y_data)),
                            "std": float(np.nanstd(y_data)),
                            "min": float(np.nanmin(y_data)),
                            "max": float(np.nanmax(y_data)),
                            "median": float(np.nanmedian(y_data)),
                            "outliers": [],
                            "local_var": local_var,
                            "trend": None,
                            "skewness": None,
                            "kurtosis": None,
                        }
                    )
                else:
                    axis_stats.update(
                        {
                            "mean": None,
                            "std": None,
                            "min": None,
                            "max": None,
                            "median": None,
                            "outliers": [],
                            "local_var": None,
                            "trend": None,
                            "skewness": None,
                            "kurtosis": None,
                        }
                    )
                axis_stats["data_types"].append(
                    "line_plot" if hasattr(ax, "lines") and ax.lines else "scatter_plot"
                )
                axis_stats["data_points"] = sum(len(pt["y"]) for pt in curve_points)
                stats["per_axis"].append(axis_stats)
            return stats
        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Error calculating seaborn statistics: {str(e)}"
            )
            return stats

    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness with proper handling of edge cases."""
        try:
            if len(data) < 3:
                return 0.0

            # Remove NaN and infinite values
            clean_data = data[np.isfinite(data)]
            if len(clean_data) < 3:
                return 0.0

            mean_val = np.nanmean(clean_data)
            std_val = np.nanstd(clean_data)

            if std_val == 0 or not np.isfinite(std_val):
                return 0.0

            # Calculate skewness
            skewness = np.nanmean(((clean_data - mean_val) / std_val) ** 3)
            return float(skewness) if np.isfinite(skewness) else 0.0
        except Exception:
            return 0.0

    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis with proper handling of edge cases."""
        try:
            if len(data) < 4:
                return 0.0

            # Remove NaN and infinite values
            clean_data = data[np.isfinite(data)]
            if len(clean_data) < 4:
                return 0.0

            mean_val = np.nanmean(clean_data)
            std_val = np.nanstd(clean_data)

            if std_val == 0 or not np.isfinite(std_val):
                return 0.0

            # Calculate kurtosis
            kurtosis = np.nanmean(((clean_data - mean_val) / std_val) ** 4) - 3
            return float(kurtosis) if np.isfinite(kurtosis) else 0.0
        except Exception:
            return 0.0

    def _get_colors(self, figure: Any) -> List[dict]:
        """Get the colors used in the seaborn figure, with hex and common name if possible. No colors for heatmaps (QuadMesh)."""

        def hex_to_name(hex_color):
            try:
                import webcolors

                return webcolors.hex_to_name(hex_color)
            except Exception:
                return None

        colors = []
        try:
            axes = self._get_axes(figure)
            for ax in axes:
                # Skip axis if it has a heatmap (QuadMesh)
                has_heatmap = False
                for collection in ax.collections:
                    if (
                        collection.__class__.__name__ == "QuadMesh"
                        and hasattr(collection, "get_array")
                        and collection.get_array() is not None
                    ):
                        has_heatmap = True
                        break
                if not has_heatmap and hasattr(ax, "images") and ax.images:
                    for image in ax.images:
                        if (
                            hasattr(image, "get_array")
                            and image.get_array() is not None
                        ):
                            has_heatmap = True
                            break
                if has_heatmap:
                    continue
                # Colors from collections (not QuadMesh)
                for collection in ax.collections:
                    if collection.__class__.__name__ == "QuadMesh":
                        continue
                    if hasattr(collection, "get_facecolor"):
                        facecolor = collection.get_facecolor()
                        if facecolor is not None:
                            if len(facecolor.shape) > 1:
                                for color in facecolor:
                                    try:
                                        hex_color = to_hex(color)
                                        color_name = hex_to_name(hex_color)
                                        if hex_color not in [c["hex"] for c in colors]:
                                            colors.append(
                                                {"hex": hex_color, "name": color_name}
                                            )
                                    except Exception:
                                        continue
                            else:
                                try:
                                    hex_color = to_hex(facecolor)
                                    color_name = hex_to_name(hex_color)
                                    if hex_color not in [c["hex"] for c in colors]:
                                        colors.append(
                                            {"hex": hex_color, "name": color_name}
                                        )
                                except Exception:
                                    continue
                    if hasattr(collection, "get_edgecolor"):
                        edgecolor = collection.get_edgecolor()
                        if edgecolor is not None:
                            if len(edgecolor.shape) > 1:
                                for color in edgecolor:
                                    try:
                                        hex_color = to_hex(color)
                                        color_name = hex_to_name(hex_color)
                                        if hex_color not in [c["hex"] for c in colors]:
                                            colors.append(
                                                {"hex": hex_color, "name": color_name}
                                            )
                                    except Exception:
                                        continue
                            else:
                                try:
                                    hex_color = to_hex(edgecolor)
                                    color_name = hex_to_name(hex_color)
                                    if hex_color not in [c["hex"] for c in colors]:
                                        colors.append(
                                            {"hex": hex_color, "name": color_name}
                                        )
                                except Exception:
                                    continue
                # Colors from lines
                for line in ax.lines:
                    color = line.get_color()
                    if color is not None:
                        try:
                            hex_color = to_hex(color)
                            color_name = hex_to_name(hex_color)
                            if hex_color not in [c["hex"] for c in colors]:
                                colors.append({"hex": hex_color, "name": color_name})
                        except Exception:
                            continue
                # Colors from patches
                for patch in ax.patches:
                    facecolor = patch.get_facecolor()
                    if facecolor is not None:
                        try:
                            hex_color = to_hex(facecolor)
                            color_name = hex_to_name(hex_color)
                            if hex_color not in [c["hex"] for c in colors]:
                                colors.append({"hex": hex_color, "name": color_name})
                        except Exception:
                            continue
                    edgecolor = patch.get_edgecolor()
                    if edgecolor is not None:
                        try:
                            hex_color = to_hex(edgecolor)
                            color_name = hex_to_name(hex_color)
                            if hex_color not in [c["hex"] for c in colors]:
                                colors.append({"hex": hex_color, "name": color_name})
                        except Exception:
                            continue
        except Exception as e:
            logger.warning(f"Error getting colors: {str(e)}")
        return colors

    def _get_markers(self, figure: Any) -> List[dict]:
        """Get the markers used in the seaborn figure, with codes and names."""

        def marker_code_to_name(marker_code):
            """Convert matplotlib marker code to readable name."""
            marker_names = {
                "o": "circle",
                "s": "square",
                "^": "triangle_up",
                "v": "triangle_down",
                "D": "diamond",
                "p": "plus",
                "*": "star",
                "h": "hexagon1",
                "H": "hexagon2",
                "d": "thin_diamond",
                "|": "vline",
                "_": "hline",
                "P": "plus_filled",
                "X": "x_filled",
                "x": "x",
                "+": "plus",
                "1": "tri_down",
                "2": "tri_up",
                "3": "tri_left",
                "4": "tri_right",
                "8": "octagon",
                "None": "none",
            }
            return marker_names.get(str(marker_code), str(marker_code))

        markers = []
        try:
            axes = self._get_axes(figure)

            for ax in axes:
                for line in ax.lines:
                    marker = line.get_marker()
                    if marker is not None and marker != "None":
                        marker_code = str(marker)
                        marker_name = marker_code_to_name(marker)
                        if marker_code not in [m["code"] for m in markers]:
                            markers.append({"code": marker_code, "name": marker_name})

                for collection in ax.collections:
                    if hasattr(collection, "get_paths"):
                        # This might be a scatter plot with markers
                        if "scatter" not in [m["code"] for m in markers]:
                            markers.append(
                                {"code": "scatter", "name": "scatter_points"}
                            )

        except Exception as e:
            logger.warning(f"Error getting markers: {str(e)}")

        return markers

    def _get_line_styles(self, figure: Any) -> List[dict]:
        """Get the line styles used in the seaborn figure, with codes and names."""

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

        line_styles = []
        try:
            axes = self._get_axes(figure)

            for ax in axes:
                for line in ax.lines:
                    linestyle = line.get_linestyle()
                    if linestyle is not None and linestyle != "None":
                        style_code = str(linestyle)
                        style_name = line_style_to_name(linestyle)
                        if style_code not in [s["code"] for s in line_styles]:
                            line_styles.append({"code": style_code, "name": style_name})

        except Exception as e:
            logger.warning(f"Error getting line styles: {str(e)}")

        return line_styles

    def _get_background_color(self, figure: Any) -> Optional[dict]:
        """Get the background color of the seaborn figure, with hex and common name if possible."""

        def hex_to_name(hex_color):
            try:
                import webcolors

                return webcolors.hex_to_name(hex_color)
            except Exception:
                return None

        try:
            if hasattr(figure, "fig"):
                bg_color = figure.fig.get_facecolor()
            elif hasattr(figure, "figure"):
                bg_color = figure.figure.get_facecolor()
            elif isinstance(figure, mpl_figure.Figure):
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
            # Extract grid layout information
            if hasattr(figure, "axes"):
                detailed_info["grid_layout"] = {
                    "shape": figure.axes.shape,
                    "size": figure.axes.size,
                    "nrows": figure.axes.shape[0],
                    "ncols": figure.axes.shape[1],
                }

            # Extract color palette details
            if hasattr(figure, "colormap"):
                detailed_info["color_palette"] = {
                    "name": str(figure.colormap),
                    "type": type(figure.colormap).__name__,
                }

            # Extract facet information in detail
            if hasattr(figure, "col_names"):
                detailed_info["facet_columns"] = {
                    "names": figure.col_names,
                    "count": len(figure.col_names),
                }
            if hasattr(figure, "row_names"):
                detailed_info["facet_rows"] = {
                    "names": figure.row_names,
                    "count": len(figure.row_names),
                }

        except Exception as e:
            logger.warning(f"Error extracting detailed info: {str(e)}")

        return detailed_info

    def _get_axis_info(self, figure: Any) -> Dict[str, Any]:
        """Get detailed information about axes, including titles and labels."""
        axis_info = {"axes": [], "figure_title": "", "total_axes": 0}

        try:
            axes = self._get_axes(figure)
            axis_info["total_axes"] = len(axes)

            # Get figure title
            if hasattr(figure, "suptitle") and getattr(figure, "_suptitle", None):
                axis_info["figure_title"] = figure._suptitle.get_text()
            elif hasattr(figure, "get_suptitle"):
                axis_info["figure_title"] = figure.get_suptitle()

            for i, ax in enumerate(axes):
                ax_info = {
                    "index": i,
                    "title": "",
                    "x_label": "",
                    "y_label": "",
                    "x_lim": None,
                    "y_lim": None,
                    "has_data": False,
                }

                # Extract axis title (subplot title)
                try:
                    if hasattr(ax, "get_title"):
                        title = ax.get_title()
                        if title and title.strip():
                            ax_info["title"] = title.strip()
                except Exception:
                    pass

                # Extract X and Y axis labels
                try:
                    if hasattr(ax, "get_xlabel"):
                        x_label = ax.get_xlabel()
                        if x_label and x_label.strip():
                            ax_info["x_label"] = x_label.strip()
                except Exception:
                    pass

                try:
                    if hasattr(ax, "get_ylabel"):
                        y_label = ax.get_ylabel()
                        if y_label and y_label.strip():
                            ax_info["y_label"] = y_label.strip()
                except Exception:
                    pass

                # Extract axis limits
                try:
                    if hasattr(ax, "get_xlim"):
                        x_lim = ax.get_xlim()
                        if x_lim and len(x_lim) == 2:
                            ax_info["x_lim"] = [float(x_lim[0]), float(x_lim[1])]
                except Exception:
                    pass

                try:
                    if hasattr(ax, "get_ylim"):
                        y_lim = ax.get_ylim()
                        if y_lim and len(y_lim) == 2:
                            ax_info["y_lim"] = [float(y_lim[0]), float(y_lim[1])]
                except Exception:
                    pass

                # Check if axis has data
                try:
                    has_data = False

                    # Check collections (scatter plots, heatmaps, etc.)
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

                    ax_info["has_data"] = has_data
                except Exception:
                    ax_info["has_data"] = False

                axis_info["axes"].append(ax_info)

        except Exception as e:
            logger.warning(f"Error getting axis info: {str(e)}")

        return axis_info

    def _analyze_axis_properties(self, ax):
        """Analyze basic properties of an axis (title, labels, limits)."""
        ax_info = {
            "title": (
                ax.get_title() if hasattr(ax, "get_title") and ax.get_title() else ""
            ),
            "x_label": (
                ax.get_xlabel() if hasattr(ax, "get_xlabel") and ax.get_xlabel() else ""
            ),
            "y_label": (
                ax.get_ylabel() if hasattr(ax, "get_ylabel") and ax.get_ylabel() else ""
            ),
            "x_lim": (
                ax.get_xlim() if hasattr(ax, "get_xlim") and ax.get_xlim() else None
            ),
            "y_lim": (
                ax.get_ylim() if hasattr(ax, "get_ylim") and ax.get_ylim() else None
            ),
            "has_grid": self._check_grid(ax),
            "has_legend": self._check_legend(ax),
        }
        return ax_info

    def _check_grid(self, ax):
        """Check if the axis has grid lines."""
        try:
            # Check if grid is enabled using matplotlib methods
            return (
                (ax.xaxis.grid or ax.yaxis.grid)
                if hasattr(ax, "xaxis") and hasattr(ax, "yaxis")
                else False
            )
        except Exception:
            return False

    def _check_legend(self, ax):
        """Check if the axis has a legend."""
        try:
            return ax.legend_ is not None if hasattr(ax, "legend_") else False
        except Exception:
            return False

    def _detect_plot_types_from_axis(self, ax):
        """Detect plot types from axis elements."""
        plot_types = []

        # Check for line plots
        if hasattr(ax, "lines") and ax.lines:
            plot_types.append("line")

        # Check for scatter plots
        if hasattr(ax, "collections") and ax.collections:
            plot_types.append("scatter")

        # Check for bar plots/histograms
        if hasattr(ax, "patches") and ax.patches:
            plot_types.append("bar")

        return plot_types

    def _detect_axis_type_and_labels(self, ax):
        """Detect axis types and extract labels for categorical axes."""
        x_type = self.NUMERIC
        y_type = self.NUMERIC
        x_labels = None
        y_labels = None

        try:
            # Check X axis
            x_ticks = ax.get_xticks()
            x_tick_labels = [label.get_text() for label in ax.get_xticklabels()]

            # Filter out empty labels
            non_empty_x_labels = [label for label in x_tick_labels if label.strip()]

            if non_empty_x_labels:
                # Check if labels look like dates
                if self._looks_like_dates(non_empty_x_labels):
                    x_type = self.DATE
                    x_labels = non_empty_x_labels
                # Check if they're clearly categorical (non-numeric strings)
                elif any(
                    not self._is_numeric_string(label) for label in non_empty_x_labels
                ):
                    x_type = self.CATEGORY
                    x_labels = non_empty_x_labels
                # If all labels are numeric, check if they represent continuous data
                elif all(
                    self._is_numeric_string(label) for label in non_empty_x_labels
                ):
                    # Convert to numbers and check if they represent a continuous range
                    try:
                        # Normalizar las etiquetas antes de convertir a float
                        normalized_labels = [
                            label.replace("−", "-") for label in non_empty_x_labels
                        ]

                        numeric_labels = [float(label) for label in normalized_labels]
                        if len(numeric_labels) > 1:
                            # Check if the range is continuous (not just a few discrete values)
                            min_val = min(numeric_labels)
                            max_val = max(numeric_labels)
                            range_size = max_val - min_val
                            # For seaborn plots, be more lenient - if we have numeric labels, assume numeric
                            # unless there are very few unique values
                            unique_values = len(set(numeric_labels))
                            if (
                                unique_values > 5
                                or range_size > len(numeric_labels) * 0.3
                            ):
                                x_type = self.NUMERIC
                            else:
                                x_type = self.CATEGORY
                        else:
                            x_type = self.NUMERIC
                    except (ValueError, TypeError):
                        x_type = self.CATEGORY
                # If all labels are numeric but we have explicit labels, might be categorical
                elif len(non_empty_x_labels) <= 10 and len(x_ticks) == len(
                    non_empty_x_labels
                ):
                    # But for seaborn, if they're numeric, prefer numeric type
                    if all(
                        self._is_numeric_string(label) for label in non_empty_x_labels
                    ):
                        x_type = self.NUMERIC
                    else:
                        x_type = self.CATEGORY
                        x_labels = non_empty_x_labels

            # Check Y axis
            y_ticks = ax.get_yticks()
            y_tick_labels = [label.get_text() for label in ax.get_yticklabels()]

            # Filter out empty labels
            non_empty_y_labels = [label for label in y_tick_labels if label.strip()]

            if non_empty_y_labels:
                # Check if labels look like dates
                if self._looks_like_dates(non_empty_y_labels):
                    y_type = self.DATE
                    y_labels = non_empty_y_labels
                # Check if they're clearly categorical
                elif any(
                    not self._is_numeric_string(label) for label in non_empty_y_labels
                ):
                    y_type = self.CATEGORY
                    y_labels = non_empty_y_labels
                # If all labels are numeric, check if they represent continuous data
                elif all(
                    self._is_numeric_string(label) for label in non_empty_y_labels
                ):
                    # Convert to numbers and check if they represent a continuous range
                    try:
                        # Normalizar las etiquetas antes de convertir a float
                        normalized_labels = [
                            label.replace("−", "-") for label in non_empty_y_labels
                        ]

                        numeric_labels = [float(label) for label in normalized_labels]
                        if len(numeric_labels) > 1:
                            # Check if the range is continuous (not just a few discrete values)
                            min_val = min(numeric_labels)
                            max_val = max(numeric_labels)
                            range_size = max_val - min_val
                            # For seaborn plots, be more lenient - if we have numeric labels, assume numeric
                            # unless there are very few unique values
                            unique_values = len(set(numeric_labels))
                            if (
                                unique_values > 5
                                or range_size > len(numeric_labels) * 0.3
                            ):
                                y_type = self.NUMERIC
                            else:
                                y_type = self.CATEGORY
                        else:
                            y_type = self.NUMERIC
                    except (ValueError, TypeError):
                        y_type = self.CATEGORY
                # Small number of explicit labels suggests categorical
                elif len(non_empty_y_labels) <= 10 and len(y_ticks) == len(
                    non_empty_y_labels
                ):
                    # But for seaborn, if they're numeric, prefer numeric type
                    if all(
                        self._is_numeric_string(label) for label in non_empty_y_labels
                    ):
                        y_type = self.NUMERIC
                    else:
                        y_type = self.CATEGORY
                        y_labels = non_empty_y_labels

        except Exception:
            # Default to numeric if detection fails
            pass

        return x_type, y_type, x_labels, y_labels

    def _is_numeric_string(self, s):
        """Check if a string represents a number."""
        try:
            # Normalizar el signo negativo Unicode a ASCII
            normalized_s = s.replace("−", "-")  # Unicode minus sign to ASCII hyphen
            float(normalized_s)
            return True
        except (ValueError, TypeError):
            return False

    def _looks_like_dates(self, labels):
        """Check if labels look like dates."""
        if not labels:
            return False

        # Check first few labels for date patterns
        for label in labels[:3]:
            if any(
                pattern in str(label)
                for pattern in [
                    "-",
                    "/",
                    ":",
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]
            ):
                return True
        return False

    def _calculate_accessibility_score(self, colors):
        """Calcula un puntaje de accesibilidad basado en los colores."""
        # Placeholder: podrías implementar un cálculo real basado en contraste, etc.
        if not colors:
            return 1.0
        return 0.85

    def _infer_domain_context(self, axes_list):
        domain_context = {
            "likely_domain": "general",
            "purpose": "analysis",
            "target_audience": "general",
            "key_metrics": [],
        }
        for ax in axes_list:
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

    def _generate_llm_description(self, axes_list, statistics):
        for ax in axes_list:
            if "llm_description" in ax:
                return ax["llm_description"]
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

    def _generate_llm_context(self, axes_list, statistics):
        for ax in axes_list:
            if "llm_context" in ax:
                return ax["llm_context"]
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

    def _generate_data_summary(self, axes_list):
        total_data_points = 0
        x_data = []
        y_data = []
        x_type = None
        y_type = None
        for ax in axes_list:
            # Para line plots - usar la estructura de line_analyzer
            if ax.get("plot_type") == "line" and "lines" in ax:
                for line in ax["lines"]:
                    xdata = line.get("xdata", [])
                    ydata = line.get("ydata", [])
                    total_data_points += len(ydata)
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
            elif ax.get("plot_type") == "histogram" and "statistics" in ax:
                stats = ax.get("statistics", {})
                # Para histogramas, usar number_of_bins en lugar de total_observations
                if "number_of_bins" in stats:
                    total_data_points += stats["number_of_bins"]
                elif "total_observations" in stats:
                    # Fallback: usar total_observations si number_of_bins no está disponible
                    total_data_points += stats["total_observations"]

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
            elif ax.get("plot_type") == "bar" and "statistics" in ax:
                stats = ax.get("statistics", {})
                if "data_points" in stats:
                    total_data_points += stats["data_points"]

                # Extraer rangos de datos para bar plots
                if "bars" in ax:
                    categories = [
                        bar_data.get("category", "") for bar_data in ax["bars"]
                    ]
                    heights = [bar_data.get("height", 0) for bar_data in ax["bars"]]
                    # Para bar plots, usar índices como x_data y heights como y_data
                    x_data.extend(range(len(categories)))
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

    def _generate_statistical_insights(self, statistics):
        insights = {}
        if "per_axis" in statistics and statistics["per_axis"]:
            axis_stats = statistics["per_axis"][0]
            if "mean" in axis_stats and axis_stats["mean"] is not None:
                insights["central_tendency"] = {
                    "mean": axis_stats["mean"],
                    "median": axis_stats.get("median"),
                    "mode": None,
                }
            if "std" in axis_stats and axis_stats["std"] is not None:
                insights["variability"] = {
                    "standard_deviation": axis_stats["std"],
                    "variance": axis_stats.get("std", 0) ** 2,
                }
        return insights

    def _generate_pattern_analysis(self, axes_list):
        pattern_info = {
            "pattern_type": None,
            "confidence_score": None,
            "equation_estimate": None,
            "shape_characteristics": {},
        }
        for ax in axes_list:
            if ax.get("pattern"):
                return ax["pattern"]
            elif ax.get("plot_type") == "line":
                pattern_info["pattern_type"] = "trend"
                pattern_info["confidence_score"] = 0.8
            elif ax.get("plot_type") == "scatter":
                pattern_info["pattern_type"] = "distribution"
                pattern_info["confidence_score"] = 0.7
        return pattern_info

    def _adapt_to_legacy_format(self, modern_output, axes_list):
        legacy_axes = []
        for ax in axes_list:
            plot_type = ax.get("plot_type", "unknown")
            if plot_type in ["line", "scatter", "bar", "histogram"]:
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
                    "plot_types": [{"type": plot_type}],
                    "pattern": ax.get("pattern", {}),
                    "domain_context": ax.get("domain_context", {}),
                    "stats": ax.get("statistics", {}),
                }
                # Agregar curve_points basado en el tipo
                if plot_type == "line" and "lines" in ax:
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
                elif plot_type == "scatter" and "collections" in ax:
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
                elif plot_type == "bar" and "bars" in ax:
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
                elif plot_type == "histogram" and "bins" in ax:
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
        return {
            "figure_type": "seaborn",
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

    def _is_histogram(self, ax):
        """
        Lógica migrada desde matplotlib_analyzer.py para detectar histogramas.
        Esta función usa la misma heurística robusta que funciona bien en Matplotlib.
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
            logger.warning(f"Error en detección de histograma: {e}")
            return True

    def _is_bar_plot(self, ax):
        """
        Lógica migrada desde matplotlib_analyzer.py para detectar bar plots.
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
            logger.warning(f"Error en detección de bar plot: {e}")
            return False
