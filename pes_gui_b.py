import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np


class PESGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Reaction Energy Profile Builder")

        # ==========================================
        # Controls
        # ==========================================

        tk.Label(root, text="Pathway 1 Energies\n(comma separated, use x for missing points").grid(row=0, column=0)

        self.e1 = tk.Text(root, width=50, height=4)
        self.e1.grid(row=1, column=0)

        tk.Label(root, text="Pathway 2 Energies\n(example: 0.0, 5.4, x, 12.8").grid(row=2, column=0)

        self.e2 = tk.Text(root, width=50, height=4)
        self.e2.grid(row=3, column=0)

        tk.Label(root, text="Legend 1").grid(row=4, column=0)
        self.legend1 = tk.Entry(root)
        self.legend1.grid(row=5, column=0)

        tk.Label(root, text="Legend 2").grid(row=6, column=0)
        self.legend2 = tk.Entry(root)
        self.legend2.grid(row=7, column=0)

        tk.Label(root, text="Spacing\n(default = 1").grid(row=8, column=0)
        self.spacing = tk.Entry(root)
        self.spacing.grid(row=9, column=0)

        tk.Label(root, text="Bar Width\n(default = 0.5").grid(row=10, column=0)
        self.barwidth = tk.Entry(root)
        self.barwidth.grid(row=11, column=0)

        tk.Button(
            root,
            text="Update Plot",
            command=self.update_plot
        ).grid(row=12, column=0)

        tk.Button(
            root,
            text="Save PNG",
            command=self.save_png
        ).grid(row=13, column=0)

        # ==========================================
        # Figure
        # ==========================================

        self.fig, self.ax = plt.subplots(figsize=(8,5))

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=root
        )

        self.canvas.get_tk_widget().grid(
            row=0,
            column=1,
            rowspan=20
        )

        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas.draw()

    def parse(self, text):

        vals = []

        for x in text.split(","):

            x = x.strip()

            if not x:
                continue

            if x.lower() == "x":
                vals.append("x")
            else:
                vals.append(float(x))

        return vals

    def update_plot(self):

        self.ax.clear()

        e1_text = self.e1.get("1.0", tk.END).strip()

        if not e1_text:
            return

        e1 = self.parse(e1_text)

        e2 = self.parse(
            self.e2.get("1.0", tk.END)
        )

        spacing = float(self.spacing.get() or 3)

        bar_width = float(self.barwidth.get() or 1.0)

        x = np.arange(len(e1))*spacing

        # =====================
        # Pathway 1
        # =====================

        for i in range(len(e1)):

            if e1[i] == "x":
                continue

            self.ax.plot(
                [x[i]-bar_width/2,
                 x[i]+bar_width/2],
                [e1[i], e1[i]],
                color="black",
                linewidth=3
            )

            if i < len(e1)-1:

                if e1[i+1] != "x":

                    self.ax.plot(
                        [x[i]+bar_width/2,
                         x[i+1]-bar_width/2],
                        [e1[i],
                         e1[i+1]],
                        "k--",
                        linewidth=0.8
                    )

        # =====================
        # Pathway 2
        # =====================

        shift = 0.25

        for i in range(len(e2)):

            if e2[i] == "x":
                continue

            y = e2[i] + shift

            self.ax.plot(
                [x[i]-bar_width/2,
                 x[i]+bar_width/2],
                [y, y],
                color="red",
                linewidth=3
            )

            if i < len(e2)-1:

                if e2[i+1] != "x":

                    self.ax.plot(
                        [x[i]+bar_width/2,
                         x[i+1]-bar_width/2],
                        [y,
                         e2[i+1]+shift],
                        "--",
                        color="red",
                        linewidth=0.8
                    )

        self.ax.set_ylabel(r'$\Delta G$ (kcal/mol)')

        self.ax.set_xlabel("Reaction Coordinate")

        self.ax.set_xticks([])

        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.plot(
            [],
            [],
            color="black",
            linewidth=3,
            label=self.legend1.get()
        )

        self.ax.plot(
            [],
            [],
            color="red",
            linewidth=3,
            label=self.legend2.get()
        )

        self.ax.legend(frameon=False)

        self.fig.tight_layout()

        self.canvas.draw()

    def save_png(self):

        filename = filedialog.asksaveasfilename(
            defaultextension=".png"
        )

        if filename:
            self.fig.savefig(
                filename,
                dpi=600
            )


root = tk.Tk()

app = PESGUI(root)

root.mainloop()
