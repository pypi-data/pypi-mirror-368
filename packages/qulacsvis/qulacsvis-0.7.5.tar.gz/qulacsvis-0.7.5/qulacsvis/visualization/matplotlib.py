from typing import List, Optional, Tuple

import matplotlib
from matplotlib import patches
from matplotlib import pyplot as plt
from typing_extensions import Final

from ..models.circuit import CircuitData, ControlQubitInfo, GateData
from ..utils.gate import grouping_adjacent_gates, to_latex_style

MATPLOTLIB_INLINE_BACKENDS = {
    "module://ipykernel.pylab.backend_inline",
    "module://matplotlib_inline.backend_inline",
    "nbAgg",
}

GATE_DEFAULT_WIDTH = 1.0
GATE_DEFAULT_HEIGHT = 1.5

GATE_MARGIN_RIGHT: Final[float] = 0.25
GATE_MARGIN_LEFT: Final[float] = 0.25
GATE_MARGIN_BOTTOM: Final[float] = 0.25
GATE_MARGIN_TOP: Final[float] = 0.25

CIRCUIT_MARGIN = 0.5

PORDER_LINE: Final[int] = 2
PORDER_GATE: Final[int] = 3
PORDER_TEXT: Final[int] = 4


def _calc_gate_width(gate: GateData) -> float:
    width = GATE_DEFAULT_WIDTH
    try:
        to_latex_style(gate.name)
    except KeyError:
        char_width = 0.2
        max_line_width = max(len(s) for s in gate.name.splitlines())
        width += (max_line_width - 3) * char_width

    return width


class MPLCircuitlDrawer:
    """
    Drawing a circuit using Matplotlib.

    Parameters
    ----------
    circuit : CircuitData
        A quantum circuit to be drawn.
    dpi : int optional default=72
        The resolution of the figure.
    scale : float optional default=0.6
        The scale of the figure.

    Attributes
    ----------
    _figure : matplotlib.figure.Figure
        The figure of the circuit.
    _ax : matplotlib.axes.Axes
        The axes of the figure.
    _circuit : CircuitData
        The quantum circuit to be drawn.
    _fig_scale_factor : float
        The scale factor of the figure.

    Examples
    --------
    >>> from qulacs import QuantumCircuit
    >>> from qulacsvis.qulacs.circuit import to_model
    >>> from qulacsvis.visualization import MPLCircuitlDrawer
    >>> import matplotlib.pyplot as plt
    >>>
    >>> circuit = QuantumCircuit(3)
    >>> circuit.add_X_gate(0)
    >>> circuit.add_Y_gate(1)
    >>> circuit.add_Z_gate(2)
    >>>
    >>> drawer = MPLCircuitlDrawer(to_model(circuit))
    >>> drawer.draw()
    >>> plt.show()
    """

    def __init__(
        self,
        circuit: CircuitData,
        *,
        dpi: int = 72,
        scale: float = 0.6,
    ):
        self._figure = plt.figure(dpi=dpi)
        self._figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
        self._ax = self._figure.add_subplot(111)
        self._ax.set_aspect("equal")
        self._ax.axis("off")

        self._circuit = circuit
        self._fig_scale_factor = scale
        self._layer_width: List[float] = []

    def _calc_layer_width(self) -> None:
        circuit_qubit_count = self._circuit.qubit_count
        circuit_layer_count = self._circuit.layer_count

        for layer in range(circuit_layer_count):
            max_width = 0.0

            for qubit in range(circuit_qubit_count):
                gate = self._circuit.gates[qubit][layer]
                max_width = max(max_width, _calc_gate_width(gate))

            self._layer_width.append(max_width)

        # When the input is an empty quantum circuit
        if self._layer_width == []:
            self._layer_width = [GATE_DEFAULT_WIDTH]

    def draw(
        self, *, debug: bool = False, filename: Optional[str] = None
    ) -> matplotlib.figure.Figure:
        """
        Draw the circuit.

        Parameters
        ----------
        debug : bool optional default=False
            If True, draw the circuit with the axes of the figure.
        filename : Optional[str] optional default=None
            File name to save the drawing mpl image

        Returns
        -------
        self._figure : matplotlib.figure.Figure
            The figure of the circuit.
        """
        if debug:
            self._ax.axis("on")
            self._ax.grid()

        circuit_qubit_count = self._circuit.qubit_count
        circuit_layer_count = self._circuit.layer_count

        self._calc_layer_width()

        # X/Y coordinates of the area where the circuit will be drawn.
        # Used to resize the figure.
        # In particular, the X coordinate is also used
        # as the right end (max_x) and left end (min_x) coordinates of the circuit wire.
        circuit_max_x = (
            sum(self._layer_width)
            + circuit_layer_count * (GATE_MARGIN_RIGHT + GATE_MARGIN_LEFT)
            - self._layer_width[0] / 2
        )
        circuit_min_x = -self._layer_width[0] / 2 - GATE_MARGIN_LEFT - GATE_MARGIN_RIGHT
        circuit_max_y = (
            circuit_qubit_count
            * (GATE_DEFAULT_HEIGHT + GATE_MARGIN_TOP + GATE_MARGIN_BOTTOM)
            - GATE_MARGIN_TOP
            - GATE_MARGIN_BOTTOM
            - GATE_DEFAULT_HEIGHT / 2
        )

        # Determine the size of the figure (drawing size of the circuit + margins)
        QUBIT_LABEL_WIDTH = 2
        self._ax.set_xlim(
            circuit_min_x - QUBIT_LABEL_WIDTH, circuit_max_x + CIRCUIT_MARGIN
        )
        self._ax.set_ylim(
            circuit_max_y + CIRCUIT_MARGIN,
            -GATE_DEFAULT_HEIGHT / 2 - CIRCUIT_MARGIN,
        )

        # Enlarge/reduce the shape while keeping the aspect ratio
        fig_width = abs(self._ax.get_xlim()[1] - self._ax.get_xlim()[0])
        fig_heigth = abs(self._ax.get_ylim()[1] - self._ax.get_ylim()[0])
        self._figure.set_size_inches(
            fig_width * self._fig_scale_factor, fig_heigth * self._fig_scale_factor
        )

        # Draw a Qubit label for the number of Qubits in the quantum circuit and a wire
        for qubit in range(circuit_qubit_count):
            line_ypos = qubit * (
                GATE_DEFAULT_HEIGHT + GATE_MARGIN_TOP + GATE_MARGIN_BOTTOM
            )
            self._text(
                circuit_min_x - 1,
                line_ypos,
                r"$q_{" + str(qubit) + r"}$",
                fontsize=30,
            )

            self._line(
                (circuit_min_x, line_ypos),
                (
                    circuit_max_x,
                    line_ypos,
                ),
            )

        # x-coordinate of the layer currently being drawn
        layer_xpos = 0.0

        # Draw a gate for each layer
        for layer in range(circuit_layer_count):
            for qubit in range(circuit_qubit_count):
                gate = self._circuit.gates[qubit][layer]
                qubit_ypos = qubit * (
                    GATE_DEFAULT_HEIGHT + GATE_MARGIN_TOP + GATE_MARGIN_BOTTOM
                )

                if gate.name == "ghost":
                    continue
                elif gate.name == "wire":
                    continue
                elif gate.name == "CNOT":
                    self._cnot(gate, (layer_xpos, qubit_ypos))
                elif gate.name == "Toffoli":
                    self._cnot(gate, (layer_xpos, qubit_ypos))
                elif gate.name == "SWAP":
                    self._swap(gate, (layer_xpos, qubit_ypos))
                elif len(gate.target_bits) > 1:
                    self._multi_gate(gate, (layer_xpos, qubit_ypos))
                else:
                    self._gate_with_size(gate, (layer_xpos, qubit_ypos), 1)

            # Determine the x-coordinate of the next layer
            if layer < circuit_layer_count - 1:
                layer_xpos += (
                    (self._layer_width[layer] + self._layer_width[layer + 1]) * 0.5
                    + GATE_MARGIN_RIGHT
                    + GATE_MARGIN_LEFT
                )

        if filename:
            self._figure.savefig(
                filename,
                # need some options?
            )

        if matplotlib.get_backend() in MATPLOTLIB_INLINE_BACKENDS:
            matplotlib.pyplot.close(self._figure)
        return self._figure

    def _line(
        self,
        from_xy: Tuple[float, float],
        to_xy: Tuple[float, float],
        lc: str = "k",
        ls: str = "-",
        lw: float = 2.0,
        zorder: int = PORDER_LINE,
    ) -> None:
        """
        Draw a line.

        Parameters
        ----------
        from_xy : Tuple[float, float]
            The position of the start point.
        to_xy : Tuple[float, float]
            The position of the end point.
        lc : str optional default="k"
            The color of the line.
        ls : str optional default="-"
            The style of the line.
        lw : float optional default=2.0
            The width of the line.
        zorder : int optional default=PORDER_LINE
            The zorder of the line.
        """

        from_x, from_y = from_xy
        to_x, to_y = to_xy
        self._ax.plot(
            [from_x, to_x],
            [from_y, to_y],
            color=lc,
            linestyle=ls,
            linewidth=lw,
            zorder=zorder,
        )

    def _text(
        self,
        x: float,
        y: float,
        text: str,
        horizontalalignment: str = "center",
        verticalalignment: str = "center",
        fontsize: int = 20,
        color: str = "k",
        clip_on: bool = True,
        zorder: int = PORDER_TEXT,
    ) -> None:
        """
        Draw a text.

        Parameters
        ----------
        x : float
            The x position of the text.
        y : float
            The y position of the text.
        text : str
            The text to be drawn.
        horizontalalignment : str optional default="center"
            The horizontal alignment of the text.
        verticalalignment : str optional default="center"
            The vertical alignment of the text.
        fontsize : int optional default=20
            The font size of the text.
        color : str optional default="k"
            The color of the text.
        clip_on : bool optional default=True
            If True, the text will be clipped.
        zorder : int optional default=PORDER_TEXT
            The zorder of the text.

        Notes
        -----
        The fontsize will be adjusted by _fig_scale_factor.
        """

        self._ax.text(
            x,
            y,
            text,
            horizontalalignment=horizontalalignment,
            verticalalignment=verticalalignment,
            fontsize=fontsize * self._fig_scale_factor,
            color=color,
            clip_on=clip_on,
            zorder=zorder,
        )

    def _gate_with_size(
        self, gate: GateData, xy: Tuple[float, float], multi_gate_size: int
    ) -> None:
        """
        Draw a gate with a specified size.

        Parameters
        ----------
        gate : GateData
            The gate data to be drawn.
        xy : Tuple[float, float]
            The position of the gate with the smallest index among the target bits.
        multi_gate_size : int
            The size of the gate.
        """

        xpos, ypos = xy
        gate_width = _calc_gate_width(gate)

        # Find the midpoint of the y-coordinate of the gate with size
        ypos = (
            ypos
            + (
                ypos
                + (multi_gate_size - 1)
                * (GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP)
            )
        ) * 0.5
        multi_gate_height = GATE_DEFAULT_HEIGHT * multi_gate_size + (
            GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
        ) * (multi_gate_size - 1)
        box = patches.Rectangle(
            # The gate is centered.
            xy=(xpos - 0.5 * gate_width, ypos - 0.5 * multi_gate_height),
            width=gate_width,
            height=multi_gate_height,
            facecolor="w",
            edgecolor="k",
            linewidth=2.4,
            zorder=PORDER_GATE,
        )
        self._ax.add_patch(box)

        if gate.name == "":
            latex_style_gate_str = ""
        else:
            try:
                latex_style_gate_str = f"${to_latex_style(gate.name)}$"
            except KeyError:
                latex_style_gate_str = gate.name

        self._text(xpos, ypos, latex_style_gate_str)
        self._control_bits(gate.control_bit_infos, (xpos, ypos))

    def _multi_gate(self, gate: GateData, xy: Tuple[float, float]) -> None:
        """
        Draw a multi-gate. (e.g., DensityMatrixGate)

        Parameters
        ----------
        gate : GateData
            The gate data to be drawn.
        xy : Tuple[float, float]
            The position of the gate with the smallest index among the target bits.
        """

        xpos, ypos = xy

        multi_gate_data = GateData(gate.name)

        groups_of_adjacent_gates = grouping_adjacent_gates(gate.target_bits)

        for i, adjacent_gates in enumerate(groups_of_adjacent_gates):
            group_x = xpos
            group_y = adjacent_gates[0] * (
                GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
            )
            self._gate_with_size(
                multi_gate_data, (group_x, group_y), len(adjacent_gates)
            )
            if i == 0:
                # Show the name only for the first group (multi_gate) and hide the rest
                multi_gate_data.name = ""

        # Gray line connecting the gates
        ypos = min(gate.target_bits) * (
            GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
        )
        to_ypos = max(gate.target_bits) * (
            GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
        )
        self._line((xpos, ypos), (xpos, to_ypos), lw=10, lc="gray")

        self._control_bits(gate.control_bit_infos, (xpos, ypos))

    def _cnot(self, gate: GateData, xy: Tuple[float, float]) -> None:
        """
        Draw a CNOT gate.

        Parameters
        ----------
        gate : GateData
            The gate data to be drawn.
        xy : Tuple[float, float]
            The position of the gate indicating the target bit of CNOT.

        Raise
        -----
        ValueError
            If the gate does not have a control bit.
        """

        if gate.control_bit_infos is None:
            raise ValueError("control_bit_infos is None")
        elif gate.control_bit_infos == []:
            raise ValueError("control_bit_infos is empty")

        self._not_mark(xy)
        self._control_bits(gate.control_bit_infos, xy)

    def _not_mark(self, xy: Tuple[float, float]) -> None:
        """
        Draw a "NOT" mark used in CNOT etc.

        Parameters
        ----------
        xy : Tuple[float, float]
            The position of the gate indicating the target bit of NOT.
        """
        xpos, ypos = xy
        TARGET_QUBIT_RADIUS: Final[float] = 0.4

        target = patches.Circle(
            xy=(xpos, ypos),
            radius=TARGET_QUBIT_RADIUS,
            fc="w",
            ec="k",
            zorder=PORDER_GATE,
        )
        self._ax.add_patch(target)
        # draw target qubit's "+" mark
        # |
        self._line(
            (xpos, ypos - TARGET_QUBIT_RADIUS),
            (xpos, ypos + TARGET_QUBIT_RADIUS),
            zorder=PORDER_TEXT,
        )
        # -
        self._line(
            (xpos - TARGET_QUBIT_RADIUS, ypos),
            (xpos + TARGET_QUBIT_RADIUS, ypos),
            zorder=PORDER_TEXT,
        )

    def _control_bits(
        self, control_bit_infos: List[ControlQubitInfo], xy_from: Tuple[float, float]
    ) -> None:
        """
        Draw control bits.

        Parameters
        ----------
        control_bit_infos : List[ControlQubitInfo]
            The control bits to be drawn.
        xy_from : Tuple[float, float]
            The position of the gate from which the control bits are connected.
        """

        for info in control_bit_infos:
            control_bit = info.index
            to_ypos = control_bit * (
                GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
            )
            to_xpos = xy_from[0]

            self._line(
                xy_from,
                (to_xpos, to_ypos),
            )
            if info.control_value == 0:
                ctl = patches.Circle(
                    xy=(to_xpos, to_ypos),
                    radius=0.15,
                    fc="w",
                    ec="k",
                    linewidth=2.0,
                    zorder=PORDER_GATE,
                )
            else:
                ctl = patches.Circle(
                    xy=(to_xpos, to_ypos),
                    radius=0.15,
                    fc="k",
                    ec="w",
                    linewidth=0,
                    zorder=PORDER_GATE,
                )
            self._ax.add_patch(ctl)

    def _swap(self, gate: GateData, xy: Tuple[float, float]) -> None:
        """
        Draw a SWAP gate.

        Parameters
        ----------
        gate : GateData
            The gate data to be drawn.
        xy : Tuple[float, float]
            The position of the gate with the smaller index among the target bits.
        """

        xpos, ypos = xy
        TARGET_QUBIT_MARK_SIZE: Final[float] = 0.2

        for target_bit in gate.target_bits:
            to_ypos = target_bit * (
                GATE_DEFAULT_HEIGHT + GATE_MARGIN_BOTTOM + GATE_MARGIN_TOP
            )
            self._line(
                (xpos, ypos),
                (xpos, to_ypos),
            )
            # draw target qubit's "x" mark
            # \
            self._line(
                (xpos - TARGET_QUBIT_MARK_SIZE, to_ypos - TARGET_QUBIT_MARK_SIZE),
                (xpos + TARGET_QUBIT_MARK_SIZE, to_ypos + TARGET_QUBIT_MARK_SIZE),
            )
            # /
            self._line(
                (xpos + TARGET_QUBIT_MARK_SIZE, to_ypos - TARGET_QUBIT_MARK_SIZE),
                (xpos - TARGET_QUBIT_MARK_SIZE, to_ypos + TARGET_QUBIT_MARK_SIZE),
            )
