# %%
# Pkgs avail in default py
from copy import deepcopy
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta

# Plotting
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.axes._axes import Axes as AxisType
from matplotlib.colors import to_rgba

# %%


DEFAULT_MARKERSIZE = 750
DEFAULT_LINEWIDTH = 25
DEFAULT_TEXTCOLOR = 'k'
DEFAULT_SPAN_EDGE_HEIGHT = 0.2
DEFAULT_MARKER = 'd'
LUMINANCE_THRESHOLD = 0.8


def set_default_markersize(size: float):
    global DEFAULT_MARKERSIZE
    DEFAULT_MARKERSIZE = size


def set_default_linewidth(linewidth: float):
    global DEFAULT_LINEWIDTH
    DEFAULT_LINEWIDTH = linewidth


def set_default_textcolor(textcolor: float):
    global DEFAULT_TEXTCOLOR
    DEFAULT_TEXTCOLOR = textcolor


def set_default_edge_height(edge_height: float):
    global DEFAULT_SPAN_EDGE_HEIGHT
    DEFAULT_SPAN_EDGE_HEIGHT = edge_height


def set_default_marker(marker: float):
    global DEFAULT_MARKER
    DEFAULT_MARKER = marker


def set_luminance_threshold(luminance: float):
    global LUMINANCE_THRESHOLD
    LUMINANCE_THRESHOLD = luminance

# %%


class TextAlignment(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


def hflip_align(align: TextAlignment):
    match align:
        case TextAlignment.CENTER:
            return align
        case TextAlignment.RIGHT:
            return TextAlignment.LEFT
        case TextAlignment.LEFT:
            return TextAlignment.RIGHT
        case _:
            ValueError(f"Unknown text alignment {align}")


def get_text_align(align_str: str):
    try:
        return TextAlignment(align_str)
    except ValueError:
        raise ValueError(
            f'Invalid text alignment. Given {align_str}, valid inputs {[k.lower() for k in TextAlignment.__members__.keys()]}')


def determine_textcolor(background_color: str, alignment: TextAlignment):
    if alignment == TextAlignment.RIGHT:
        return 'k'
    rgba = list(to_rgba(background_color))
    rgb = [c + (1-c)*(1-rgba[3]) for c in rgba[:3]]
    luminance = 0.2126*rgb[0] + 0.7152*rgb[1] + 0.0722*rgb[2]
    if luminance < LUMINANCE_THRESHOLD:
        textcolor = "w"
    else:
        textcolor = "k"
    return textcolor

# %%


@dataclass
class Element:
    textalignment: TextAlignment  # alignment of text
    textcolor: tuple[int]  # Color of the text
    elementcolor: tuple[int]  # Color of the element
    level_increment: float  # In [0,1]
    zorder_delta: float
    text: str
    offset: timedelta
    v_offset: float
    style: str  # See plt.text.style
    weight: str  # See plt.text.weight

    def __init__(self, text: str, color: str, textalignment: str = 'center', zorder_delta: float = 0., textcolor: str = None, level_increment: float = 0.5, offset: timedelta = timedelta(0), v_offset: float = 0., style='normal', weight='normal'):
        if textcolor is None:
            textcolor = DEFAULT_TEXTCOLOR
        self.textalignment = get_text_align(textalignment)
        self.textcolor = to_rgba(textcolor)
        self.elementcolor = to_rgba(color)
        if level_increment < 0 or level_increment > 1:
            ValueError(
                f"Expected level_increment in [0,1], got {level_increment}")
        self.level_increment = level_increment
        self.text = text
        self.offset = offset
        self.zorder_delta = zorder_delta
        self.v_offset = v_offset
        self.style = style
        self.weight = weight


@dataclass
class Span(Element):
    start: datetime
    end: datetime
    edge_height: float
    lw: float

    def __init__(self, start: datetime, end: datetime, text: str, color: str, lw: float = None, edge_height: float = None, **kwargs):
        if edge_height is None:
            edge_height = DEFAULT_SPAN_EDGE_HEIGHT
        super().__init__(text, color, **kwargs)
        self.start = start
        self.end = end
        self.edge_height = edge_height
        self.lw = lw


@dataclass
class Period(Element):
    start: datetime
    end: datetime
    lw: float
    ls: str

    def __init__(self, start: datetime, end: datetime, text: str, color: str, lw: float = None, ls: str = 'solid', **kwargs):
        if lw is None:
            lw = DEFAULT_LINEWIDTH
        # Color determines the background of the text
        super().__init__(text, color, **kwargs)
        if 'textcolor' not in kwargs:
            self.textcolor = determine_textcolor(color, self.textalignment)
        self.start = start
        self.end = end
        self.lw = lw
        self.ls = ls


@dataclass
class Event(Element):
    date: datetime
    marker: str
    markersize: float

    def __init__(self, date: datetime, text: str, marker: str = None, markersize: float = None, **kwargs):
        if marker is None:
            marker = DEFAULT_MARKER
        if markersize is None:
            markersize = DEFAULT_MARKERSIZE
        super().__init__(text, **kwargs)
        self.date = date
        self.marker = marker
        self.markersize = markersize

# %%


def get_fig_ax(figsize_or_ax):
    fig, ax = None, figsize_or_ax
    if type(ax) is not AxisType:
        figsize = figsize_or_ax
        if type(figsize) is not tuple:
            figsize = (figsize, figsize)
        # Create the figure
        fig, ax = plt.subplots(figsize=figsize)
    return fig, ax


def add_quarters(ax: AxisType, fontsize: float):
    dayloc = matplotlib.dates.MonthLocator(bymonth=(1, 4, 7, 10), bymonthday=1)
    ax.xaxis.set_major_locator(dayloc)
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d'))
    tick_locs = ax.get_xticks()
    ax.set_xticks(tick_locs)

    # Re-format the quarterly ticks
    ticks = []
    for tick in ax.get_xticklabels():
        text = tick._text
        text = text.split("-")
        if text[1] == "01":
            ticks.append("Q1" + "\n" + text[0])
        elif text[1] == "04":
            ticks.append("Q2" + "\n" + text[0])
        elif text[1] == "07":
            ticks.append("Q3" + "\n" + text[0])
        elif text[1] == "10":
            ticks.append("Q4" + "\n" + text[0])

    if len(ticks) > 0:
        ax.set_xticklabels(ticks, fontsize=fontsize)


def add_span(fontsize: float, ax: AxisType, level: float, span: Span):
    ax.plot(
        [span.start, span.end],
        [level, level],
        color=span.elementcolor,
        solid_capstyle='round',
        zorder=10 + span.zorder_delta,
        lw=span.lw
    )

    if span.edge_height > 0.:
        ax.plot(
            [span.start, span.start],
            [level-span.edge_height, level+span.edge_height],
            color=span.elementcolor,
            zorder=10 + span.zorder_delta,
            lw=span.lw
        )

        ax.plot(
            [span.end, span.end],
            [level-span.edge_height, level+span.edge_height],
            color=span.elementcolor,
            zorder=10 + span.zorder_delta,
            lw=span.lw
        )

    ax.text(
        (span.end - span.start) /
        2 + span.start,
        level + span.v_offset,
        span.text,
        ha=span.textalignment.value,
        va="center",
        color=span.textcolor,
        backgroundcolor="w",
        fontsize=fontsize,
        zorder=30,
        style=span.style,
        weight=span.weight
    )


def add_period(fontsize: float, ax: AxisType, level: float, period: Period):
    ax.plot(
        [period.start, period.end],
        [level, level],
        lw=period.lw,
        ls=period.ls,
        color=period.elementcolor,
        solid_capstyle='round',
        zorder=10 + period.zorder_delta)

    textpos = get_textpos_period(period)
    textalignment = hflip_align(period.textalignment)

    ax.text(
        textpos,
        level + period.v_offset,
        period.text,
        ha=textalignment.value,
        va="center",
        color=period.textcolor,
        fontsize=fontsize,
        zorder=30,
        style=period.style,
        weight=period.weight)


def add_event(fontsize: float, ax: AxisType, level: float, event: Event):
    ax.scatter(
        event.date,
        level,
        marker=event.marker,
        color=event.elementcolor,
        s=event.markersize,
        zorder=20 + event.zorder_delta)

    textpos = event.date + event.offset
    textalignment = hflip_align(event.textalignment)

    ax.text(
        textpos,
        level + event.v_offset,
        event.text,
        ha=textalignment.value,
        va="center",
        color=event.textcolor,
        fontsize=fontsize,
        zorder=30 + event.zorder_delta,
        style=event.style,
        weight=event.weight)


def get_textpos_period(element: Period):
    align = element.textalignment
    match align:
        case TextAlignment.CENTER:
            return (element.end - element.start) / 2 + element.start + element.offset
        case TextAlignment.LEFT:
            return element.start + element.offset
        case TextAlignment.RIGHT:
            return element.end + element.offset
        case _:
            ValueError(f"Unknown text alignment {align}")


def format_axis(ax: AxisType, zlevel_min: float, zlevel_max: float):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.set_yticks([])

    # Scale the y limits
    ax.set_ylim([zlevel_min-0.5, zlevel_max+0.5])
    ax.invert_yaxis()


def get_limits(data):
    timeline_min = datetime.max
    timeline_max = datetime.min
    zlevel_min = 0
    zlevel_max = float('-inf')

    level = 0

    for element in data:
        increment = element.level_increment
        zlevel_max = max(zlevel_max, level)

        level += increment

        if type(element) is Period:
            timeline_min = min(timeline_min, element.start)
            timeline_max = max(timeline_max, element.end)

        elif type(element) is Event:
            timeline_min = min(timeline_min, element.date)
            timeline_max = max(timeline_max, element.date)
    return zlevel_min, zlevel_max, timeline_min, timeline_max


# %%
def chart(data: list[Element], figsize_or_ax: float | tuple[float] | AxisType, fontsize=12):
    """

    This function creates a Gantt Chart based on a dictionary of dictionaries
    which each describe an element in the chart. The arguments are:

    Parameters
    ----------
    data : dict
        A dictionary of elements in the Gantt chart. The structure is detailed
        below.
    figsize : tuple, optional
        The size of the figure, passed to matplotlib. The default is (12,8).
    fontsize : scalar, optional
        Font size for labels and text in the chart. The default is 12.
    """
    # Get plotting
    fig, ax = get_fig_ax(figsize_or_ax)

    data = deepcopy(data)

    # Get the timeline limits
    zlevel_min, zlevel_max, _, _ = get_limits(data)

    format_axis(ax, zlevel_min, zlevel_max)

    level = 0

    for element in data:
        if type(element) is Span:
            add_span(fontsize, ax, level, element)

        elif type(element) is Period:
            add_period(fontsize, ax, level, element)

        elif type(element) is Event:
            add_event(fontsize, ax, level, element)

        level += element.level_increment

    # Set quarterly ticks
    add_quarters(ax, fontsize)
    if fig is None:
        return

    return fig, ax
