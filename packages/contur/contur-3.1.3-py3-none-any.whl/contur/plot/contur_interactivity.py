import copy
import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
from contur.plot.contur_plot import conturPlot
from ttkbootstrap import Style
from contur.factories.likelihood_point import LikelihoodPoint
import tkinter.messagebox as mb


class Interactivity:
    """
    A small GUI controller to let the user pick which Contur plot to display
    (Hybrid, Overlay, Mesh, Levels, Dominant Pools, or Overlay+Pools), and to
    optionally filter out (exclude) specific analysis pools from the Dominant Pools view.
    """
    def __init__(self, plot_base, level=0):
        """
        Parameters
        ----------
        plot_base : ConturPlotBase
        """
        self.plot_base = plot_base
        self.level = level
        self.views = [
            'Hybrid', 'Overlay', 'Mesh',
            'Levels', 'Dominant Pools', 'Overlay+Pools'
        ]

        self._orig_points_data = [p.as_dict() for p in plot_base.points]
        self.omittedPools_per_view = {view: "" for view in self.views}

        self.xarg = plot_base.xarg
        self.yarg = plot_base.yarg
        self.logX = plot_base.axHolder.xLog
        self.logY = plot_base.axHolder.yLog
        self.xlabel = plot_base.axHolder.xLabel
        self.ylabel = plot_base.axHolder.yLabel

    def show(self):
        style = Style(theme="solar")
        self.root = style.master
        self.root.title("Contur Plot Navigator")
        self.root.option_add("*Font", ("Segoe UI", 11))
        self.root.configure(padx=20, pady=20)

        lf = ttk.LabelFrame(self.root, text="Select Contur Plot View", padding=20)
        lf.pack(fill="both", expand=True)

        self.combo = ttk.Combobox(lf, values=self.views, state="readonly")
        self.combo.current(0)
        self.combo.pack(fill="x", pady=(0, 10))

        btn_frame = ttk.Frame(lf)
        btn_frame.pack(pady=(0, 10))
        ttk.Button(btn_frame, text="Plot", command=self.on_plot, width=12).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Filter Pools", command=self.on_filter, width=12).grid(row=0, column=1, padx=5)

        self.root.mainloop()

    def on_plot(self):
        view = self.combo.get()
        omitted = self.omittedPools_per_view.get(view, "")

        self.plot_base.points = [LikelihoodPoint.from_dict(d) for d in self._orig_points_data]
        self.plot_base.omittedPools = omitted
        self.plot_base.build_grid(self.xarg, self.yarg)
        self.plot_base.build_axes_from_grid(
            self.xarg, self.yarg,
            logX=self.logX,
            logY=self.logY,
            xlabel=self.xlabel,
            ylabel=self.ylabel
        )

        p = conturPlot(
            saveAxes=True,
            interactive_mode=True,
            plotTitle=self.plot_base.plotTitle,
            iLevel=self.plot_base.iLevel,
            iOrder=self.plot_base.iOrder,
            iSigma=self.plot_base.iSigma,
            cpow=self.plot_base.cpow,
            style=self.plot_base.style,
            showcls=self.plot_base.showcls,
            show_legend=self.plot_base.show_legend,
            base_plot=self.plot_base
        )

        p.add_grid(
            self.plot_base.conturGrid,
            "combined",
            self.plot_base.outputPath,
            self.plot_base.axHolder
        )
        p.add_external_data_grids(self.plot_base.alt_grids)

        if view == 'Hybrid':
            p.plot_hybrid()
        elif view == 'Overlay':
            p.plot_mesh_overlay()
        elif view == 'Mesh':
            p.plot_mesh(make_cbar=True)
        elif view == 'Levels':
            p.plot_levels()
        elif view == 'Dominant Pools':
            p.plot_pool_names(self.plot_base, self.level)
        elif view == 'Overlay+Pools':
            p.plot_overlay_and_pools(self.plot_base, self.level)

        plt.show()

    def on_filter(self):
        view = self.combo.get()
        pool_selector_gui(
            parent=self.root,
            cpb=self.plot_base,
            level=self.level,
            current_omitted_pools=self.omittedPools_per_view[view],
            on_apply=lambda omitted: self.apply_filter_to_view(view, omitted)
        )

    def apply_filter_to_view(self, view, omitted):
        self.omittedPools_per_view[view] = omitted
        self.on_plot()


def pool_selector_gui(parent, cpb, level, current_omitted_pools, on_apply):
    all_pools = list(cpb.conturGridPools.keys())

    top = tk.Toplevel(parent)
    top.title("Exclude Pools")
    top.geometry("600x400")
    top.transient(parent)
    top.grab_set()
    top.lift()
    top.overrideredirect(False)
    tk.Label(top, text="Select Pools to Exclude", font=(None, 14, "bold")).pack(pady=10)

    var_dict = {}
    already_omitted = set(current_omitted_pools.split(',')) if current_omitted_pools else set()

    container = tk.Frame(top)
    container.pack(fill="both", expand=True, padx=10)

    canvas = tk.Canvas(container)
    canvas.pack(side="left", fill="both", expand=True)

    vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    vsb.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=vsb.set)

    list_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=list_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    list_frame.bind("<Configure>", on_frame_configure)

    for pool in all_pools:
        var = tk.BooleanVar(value=(pool in already_omitted))
        chk = tk.Checkbutton(
            list_frame,
            text=pool,
            variable=var,
            anchor='w',
            font=(None, 12)
        )
        chk.pack(fill='x', padx=10, pady=2)
        var_dict[pool] = var

    def _select_all():
        for v in var_dict.values():
            v.set(True)

    def _deselect_all():
        for v in var_dict.values():
            v.set(False)

    btn_frame = tk.Frame(top)
    btn_frame.pack(pady=5, fill="x", padx=20)
    tk.Button(btn_frame, text="Select All", command=_select_all).pack(side="left", expand=True)
    tk.Button(btn_frame, text="Deselect All", command=_deselect_all).pack(side="left", expand=True)

    def apply_selection():
        to_omit = [p for p, v in var_dict.items() if v.get()]
        if len(to_omit) == len(all_pools):
            mb.showwarning(
                title="Warning: No pools selected",
                message="You have excluded all pools. You must leave at least one pool unexcluded."
            )
            return
        omitted = ",".join(to_omit)
        top.destroy()
        on_apply(omitted)

    tk.Button(
        top,
        text="Apply",
        command=apply_selection,
        font=(None, 12)
    ).pack(pady=10, fill='x', padx=20)

