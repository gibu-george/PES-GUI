
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PESGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("PES GUI v2")

        self.pathways = []

        left = tk.Frame(root)
        left.pack(side="left", fill="y")

        right = tk.Frame(root)
        right.pack(side="right", fill="both", expand=True)

        # Scrollable pathway area
        self.canvas_frame = tk.Canvas(left, width=500)
        scrollbar = tk.Scrollbar(left, orient="vertical", command=self.canvas_frame.yview)

        self.inner = tk.Frame(self.canvas_frame)
        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas_frame.configure(scrollregion=self.canvas_frame.bbox("all"))
        )

        self.canvas_frame.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas_frame.configure(yscrollcommand=scrollbar.set)

        self.canvas_frame.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Button(self.inner, text="+ Add Pathway", command=self.add_pathway).pack(pady=5)

        settings = tk.LabelFrame(self.inner, text="Global Settings")
        settings.pack(fill="x", padx=5, pady=5)

        tk.Label(settings, text="Spacing").grid(row=0, column=0)
        self.spacing = tk.Entry(settings, width=10)
        self.spacing.insert(0, "3")
        self.spacing.grid(row=0, column=1)

        tk.Label(settings, text="Bar Width").grid(row=1, column=0)
        self.barwidth = tk.Entry(settings, width=10)
        self.barwidth.insert(0, "1.0")
        self.barwidth.grid(row=1, column=1)

        self.show_labels = tk.BooleanVar(value=False)
        tk.Checkbutton(settings, text="Show Energy Labels",
                       variable=self.show_labels).grid(row=2, column=0, columnspan=2)

        tk.Button(settings, text="Update Plot",
                  command=self.update_plot).grid(row=3, column=0, columnspan=2, sticky="ew")

        tk.Button(settings, text="Save PNG",
                  command=self.save_png).grid(row=4, column=0, sticky="ew")

        tk.Button(settings, text="Save PDF",
                  command=self.save_pdf).grid(row=4, column=1, sticky="ew")

        tk.Button(settings, text="Save Project",
                  command=self.save_project).grid(row=5, column=0, sticky="ew")

        tk.Button(settings, text="Load Project",
                  command=self.load_project).grid(row=5, column=1, sticky="ew")

        self.fig, self.ax = plt.subplots(figsize=(8,5))
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)

        self.add_pathway()
        self.add_pathway()

    def add_pathway(self):
        idx = len(self.pathways) + 1

        frame = tk.LabelFrame(self.inner, text=f"Pathway {idx}")
        frame.pack(fill="x", padx=5, pady=5)

        tk.Label(frame, text="Legend").pack(anchor="w")
        legend = tk.Entry(frame)
        legend.pack(fill="x")

        tk.Label(frame, text="Notes").pack(anchor="w")
        notes = tk.Entry(frame)
        notes.pack(fill="x")

        color = {"value": "black"}

        def choose_color():
            c = colorchooser.askcolor()[1]
            if c:
                color["value"] = c
                color_btn.config(bg=c)

        color_btn = tk.Button(frame, text="Choose Color", command=choose_color)
        color_btn.pack(fill="x", pady=2)

        tk.Label(frame, text="Energies (comma separated, use x for missing)").pack(anchor="w")
        energies = tk.Text(frame, height=4)
        energies.pack(fill="x")

        delete_btn = tk.Button(frame, text="Delete Pathway")
        delete_btn.pack(fill="x", pady=2)

        pathway = {
            "frame": frame,
            "legend": legend,
            "notes": notes,
            "color": color,
            "energies": energies
        }

        delete_btn.config(command=lambda p=pathway: self.delete_pathway(p))

        self.pathways.append(pathway)

    def delete_pathway(self, pathway):
        pathway["frame"].destroy()
        self.pathways.remove(pathway)

    def parse(self, text):
        vals = []
        for item in text.split(","):
            item = item.strip()
            if not item:
                continue
            if item.lower() == "x":
                vals.append("x")
            else:
                vals.append(float(item))
        return vals

    def update_plot(self):
        self.ax.clear()

        spacing = float(self.spacing.get() or 3)
        bar_width = float(self.barwidth.get() or 1.0)

        colors_default = ["black","red","blue","green","purple","orange","brown"]

        plotted = False

        for p_idx, pathway in enumerate(self.pathways):

            text = pathway["energies"].get("1.0", tk.END).strip()
            if not text:
                continue

            energies = self.parse(text)

            x = np.arange(len(energies))*spacing

            color = pathway["color"]["value"]
            if color == "black" and p_idx < len(colors_default):
                color = colors_default[p_idx]

            shift = p_idx * 0.25

            for i in range(len(energies)):

                if energies[i] == "x":
                    continue

                y = energies[i] + shift

                self.ax.plot(
                    [x[i]-bar_width/2, x[i]+bar_width/2],
                    [y,y],
                    color=color,
                    linewidth=3
                )

                if self.show_labels.get():
                    self.ax.text(x[i], y+1, f"{energies[i]:.2f}",
                                 ha="center", fontsize=8)

                if i < len(energies)-1 and energies[i+1] != "x":
                    self.ax.plot(
                        [x[i]+bar_width/2, x[i+1]-bar_width/2],
                        [y, energies[i+1]+shift],
                        linestyle="--",
                        color=color,
                        linewidth=0.8
                    )

            legend = pathway["legend"].get().strip()
            notes = pathway["notes"].get().strip()

            label = legend
            if notes:
                label += f" ({notes})"

            if label:
                self.ax.plot([], [], color=color, linewidth=3, label=label)

            plotted = True

        self.ax.set_ylabel(r'$\Delta G$ (kcal/mol)')
        self.ax.set_xlabel("Reaction Coordinate")
        self.ax.set_xticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        if plotted:
            self.ax.legend(frameon=False)

        self.fig.tight_layout()
        self.canvas_plot.draw()

    def save_png(self):
        f = filedialog.asksaveasfilename(defaultextension=".png")
        if f:
            self.fig.savefig(f, dpi=600)

    def save_pdf(self):
        f = filedialog.asksaveasfilename(defaultextension=".pdf")
        if f:
            self.fig.savefig(f)

    def save_project(self):
        data = {
            "spacing": self.spacing.get(),
            "barwidth": self.barwidth.get(),
            "pathways": []
        }

        for p in self.pathways:
            data["pathways"].append({
                "legend": p["legend"].get(),
                "notes": p["notes"].get(),
                "color": p["color"]["value"],
                "energies": p["energies"].get("1.0", tk.END).strip()
            })

        f = filedialog.asksaveasfilename(defaultextension=".json")
        if f:
            with open(f, "w") as fh:
                json.dump(data, fh, indent=2)

    def load_project(self):
        f = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not f:
            return

        with open(f) as fh:
            data = json.load(fh)

        for p in list(self.pathways):
            self.delete_pathway(p)

        self.spacing.delete(0, tk.END)
        self.spacing.insert(0, data.get("spacing", "3"))

        self.barwidth.delete(0, tk.END)
        self.barwidth.insert(0, data.get("barwidth", "1.0"))

        for item in data.get("pathways", []):
            self.add_pathway()
            p = self.pathways[-1]

            p["legend"].insert(0, item.get("legend",""))
            p["notes"].insert(0, item.get("notes",""))
            p["color"]["value"] = item.get("color","black")
            p["energies"].insert("1.0", item.get("energies",""))

        self.update_plot()

root = tk.Tk()
app = PESGUI(root)
root.mainloop()
