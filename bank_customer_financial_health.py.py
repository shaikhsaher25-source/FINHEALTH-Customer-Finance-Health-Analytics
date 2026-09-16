import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

# Modern Color Palette
PALETTE = {
    "bg_main": "#f1f5f9",          # Light slate canvas
    "sidebar": "#3f4f66",          # Medium slate-blue sidebar
    "sidebar_card": "#516281",     # Lighter accent surface
    "text_dark": "#0f172a",        # Primary dark typography
    "text_muted": "#64748b",       # Secondary slate text (used on light backgrounds)
    "sidebar_muted": "#cbd5e1",    # Secondary text for the medium-toned sidebar
    "text_light": "#f8fafc",       # Primary light typography
    "accent_indigo": "#6366f1",    # Indigo action color
    "accent_hover": "#4f46e5",     # Darker indigo hover
    "accent_emerald": "#10b981",   # Emerald success
    "card_bg": "#ffffff",          # Pure white card background
    "border": "#cbd5e1",           # Border divider
    "chart_series": ["#6366f1", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"]
}


class ModernBankAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FinHealth Pro | Customer Analytics & Credit Risk")
        self.root.geometry("1420x860")
        self.root.config(bg=PALETTE["bg_main"])

        self.data = None
        self.setup_ui()
        self.auto_load_default()

    def auto_load_default(self):
        """Auto-detect bank_customer_data_2.csv or bank_customer_data.csv."""
        for target in ["bank_customer_data_2.csv", "bank_customer_data.csv"]:
            if os.path.exists(target):
                self.load_dataset_from_path(target)
                break

    def setup_ui(self):
        # Master horizontal layout
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left Sidebar (320px)
        sidebar = tk.Frame(self.root, bg=PALETTE["sidebar"], width=320)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)

        # Right Content Area
        self.content_area = tk.Frame(self.root, bg=PALETTE["bg_main"])
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(1, weight=1)

        # Setup Header in Content Area
        header_frame = tk.Frame(self.content_area, bg=PALETTE["bg_main"])
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        tk.Label(
            header_frame, text="Bank Customer Financial Health Analysis",
            font=("Segoe UI", 18, "bold"), bg=PALETTE["bg_main"], fg=PALETTE["text_dark"]
        ).pack(anchor=tk.W)
        
        tk.Label(
            header_frame, text="Real-time aggregation, rating distributions, and individual credit risk profiles",
            font=("Segoe UI", 10), bg=PALETTE["bg_main"], fg=PALETTE["text_muted"]
        ).pack(anchor=tk.W)

        # Setup Components
        self.setup_sidebar(sidebar)
        
        # Display Card in Content Area
        self.display_card = tk.Frame(self.content_area, bg=PALETTE["card_bg"], relief=tk.FLAT, bd=0)
        self.display_card.grid(row=1, column=0, sticky="nsew")
        self.show_welcome_state()

    def setup_sidebar(self, parent):
        # App Badge
        brand_frame = tk.Frame(
            parent, bg=PALETTE["accent_indigo"], padx=14, pady=14,
            highlightbackground=PALETTE["accent_hover"], highlightthickness=2
        )
        brand_frame.pack(fill=tk.X, padx=14, pady=(16, 12))
        
        tk.Label(
            brand_frame, text="✦ FINHEALTH ANALYTICS",
            font=("Segoe UI", 15, "bold"), bg=PALETTE["accent_indigo"], fg="white"
        ).pack(anchor=tk.W)

        # Data Management
        tk.Label(
            parent, text="DATA SOURCE", font=("Segoe UI", 10, "bold"),
            bg=PALETTE["sidebar"], fg=PALETTE["sidebar_muted"]
        ).pack(anchor=tk.W, padx=16, pady=(10, 4))

        load_btn = tk.Button(
            parent, text="Import CSV Dataset", command=self.load_csv,
            bg=PALETTE["accent_indigo"], fg="white", activebackground=PALETTE["accent_hover"],
            activeforeground="white", font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT, cursor="hand2", pady=7
        )
        load_btn.pack(fill=tk.X, padx=16, pady=4)

        self.data_status = tk.Label(
            parent, text="No dataset loaded", bg=PALETTE["sidebar"],
            fg=PALETTE["sidebar_muted"], font=("Segoe UI", 10, "italic")
        )
        self.data_status.pack(anchor=tk.W, padx=16, pady=2)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=12)

        # Navigation Options
        tk.Label(
            parent, text="ANALYTICAL VIEWS", font=("Segoe UI", 10, "bold"),
            bg=PALETTE["sidebar"], fg=PALETTE["sidebar_muted"]
        ).pack(anchor=tk.W, padx=16, pady=(4, 6))

        self.option_var = tk.StringVar(value="1")
        options = [
            ("Overall Bank Performance", "1"),
            ("Credit Rating Distribution", "2"),
            ("Customer Detailed Stats", "3"),
            ("Compare vs Bank Baseline", "4"),
            ("Credit Trend & Grade", "5")
        ]

        for label, val in options:
            rb = tk.Radiobutton(
                parent, text=label, variable=self.option_var, value=val,
                bg=PALETTE["sidebar"], fg=PALETTE["text_light"], selectcolor=PALETTE["sidebar_card"],
                activebackground=PALETTE["sidebar"], activeforeground=PALETTE["accent_indigo"],
                font=("Segoe UI", 11), command=self.on_option_selected, cursor="hand2", padx=4, pady=4
            )
            rb.pack(anchor=tk.W, padx=16)

        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=16, pady=12)

        # Dynamic Customer Selector
        self.customer_panel = tk.Frame(parent, bg=PALETTE["sidebar"])

        tk.Label(
            self.customer_panel, text="SELECT CUSTOMER", font=("Segoe UI", 10, "bold"),
            bg=PALETTE["sidebar"], fg=PALETTE["sidebar_muted"]
        ).pack(anchor=tk.W, padx=16, pady=(0, 4))

        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(
            self.customer_panel, textvariable=self.customer_var, state="readonly", font=("Segoe UI", 10)
        )
        self.customer_combo.pack(fill=tk.X, padx=16, pady=4)

        # Metric Filter
        self.sub_frame = tk.Frame(self.customer_panel, bg=PALETTE["sidebar"])
        tk.Label(
            self.sub_frame, text="STATISTIC FILTER", font=("Segoe UI", 9, "bold"),
            bg=PALETTE["sidebar"], fg=PALETTE["sidebar_muted"]
        ).pack(anchor=tk.W, padx=16, pady=(8, 2))

        self.sub_option_var = tk.StringVar(value="all")
        sub_opts = [("Summary Card", "all"), ("Average Score", "avg"), ("Top Parameter", "max"), ("Lowest Parameter", "min")]
        for s_label, s_val in sub_opts:
            s_rb = tk.Radiobutton(
                self.sub_frame, text=s_label, variable=self.sub_option_var, value=s_val,
                bg=PALETTE["sidebar"], fg=PALETTE["text_light"], selectcolor=PALETTE["sidebar_card"],
                activebackground=PALETTE["sidebar"], font=("Segoe UI", 9), cursor="hand2"
            )
            s_rb.pack(anchor=tk.W, padx=22, pady=1)

        self.action_btn = tk.Button(
            parent, text="Render Analysis", command=self.generate_report,
            bg=PALETTE["accent_emerald"], fg="white", activebackground="#059669",
            activeforeground="white", font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT, cursor="hand2", pady=8
        )
        self.action_btn.pack(fill=tk.X, padx=16, pady=(16, 8))

    def on_option_selected(self):
        choice = self.option_var.get()
        if choice in ["1", "2"]:
            self.customer_panel.pack_forget()
        else:
            self.customer_panel.pack(fill=tk.X, before=self.action_btn)
            if choice == "3":
                self.sub_frame.pack(fill=tk.X)
            else:
                self.sub_frame.pack_forget()
            self.update_customer_dropdown()

    def update_customer_dropdown(self):
        if self.data is not None:
            id_col, name_col = self.data.columns[0], self.data.columns[1]
            records = [f"{row[id_col]} - {row[name_col]}" for _, row in self.data.iterrows()]
            self.customer_combo['values'] = records
            if records and not self.customer_var.get():
                self.customer_combo.current(0)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if file_path:
            self.load_dataset_from_path(file_path)

    def load_dataset_from_path(self, path):
        try:
            self.data = pd.read_csv(path)
            num_records = len(self.data)
            num_metrics = len(self.data.columns) - 2
            total_nans = self.data.iloc[:, 2:].isna().sum().sum()
            
            info = f"✔ {num_records} rows | {num_metrics} metrics"
            if total_nans > 0:
                info += f" ({total_nans} NaNs detected)"
                
            self.data_status.config(text=info, fg=PALETTE["accent_emerald"])
            self.update_customer_dropdown()
            self.generate_report()
        except Exception as err:
            messagebox.showerror("Import Error", f"Unable to read CSV file:\n{err}")

    def clear_display(self):
        for widget in self.display_card.winfo_children():
            widget.destroy()

    def show_welcome_state(self):
        self.clear_display()
        box = tk.Frame(self.display_card, bg=PALETTE["card_bg"])
        box.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Label(box, text="📈", font=("Segoe UI", 48), bg=PALETTE["card_bg"]).pack()
        tk.Label(box, text="No Report Selected", font=("Segoe UI", 16, "bold"),
                 bg=PALETTE["card_bg"], fg=PALETTE["text_dark"]).pack(pady=4)
        tk.Label(box, text="Load a CSV file and select an analysis option from the sidebar to begin.",
                 font=("Segoe UI", 10), bg=PALETTE["card_bg"], fg=PALETTE["text_muted"]).pack()

    def get_customer_vector(self):
        if self.data is None:
            return None, None, None
        selection = self.customer_var.get()
        if not selection:
            messagebox.showwarning("Selection Required", "Please choose a customer from the dropdown.")
            return None, None, None

        cid = int(selection.split(" - ")[0])
        row = self.data[self.data[self.data.columns[0]] == cid]
        if row.empty:
            return None, None, None

        return cid, row.iloc[0, 1], row.iloc[0, 2:]

    def generate_report(self):
        if self.data is None:
            messagebox.showwarning("Warning", "Please import a CSV dataset first.")
            return

        choice = self.option_var.get()
        dispatch = {
            "1": self.render_overall_performance,
            "2": self.render_rating_distribution,
            "3": self.render_customer_statistics,
            "4": self.render_comparison,
            "5": self.render_trend_and_rating
        }
        handler = dispatch.get(choice)
        if handler:
            handler()

    def format_plot(self, ax, fig):
        fig.patch.set_facecolor(PALETTE["card_bg"])
        ax.set_facecolor(PALETTE["card_bg"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(PALETTE["border"])
        ax.spines['bottom'].set_color(PALETTE["border"])
        ax.grid(axis='y', linestyle='--', alpha=0.3, color=PALETTE["border"])
        ax.tick_params(colors="black", labelsize=11)

    # 1. Overall Bank Performance
    def render_overall_performance(self):
        self.clear_display()
        metric_cols = self.data.columns[2:]
        matrix = self.data[metric_cols].to_numpy(dtype=float)

        means = np.nanmean(matrix, axis=0)
        stds = np.nanstd(matrix, axis=0)
        overall_avg = np.nanmean(matrix)

        fig = Figure(figsize=(9, 4.8), dpi=105)
        ax = fig.add_subplot(111)
        self.format_plot(ax, fig)

        x = np.arange(len(metric_cols))
        bars = ax.bar(x, means, yerr=stds, capsize=4, color=PALETTE["accent_indigo"], alpha=0.88, edgecolor='none')

        for b in bars:
            h = b.get_height()
            ax.text(b.get_x() + b.get_width()/2., h + 3, f"{h:.1f}", ha='center', va='bottom',
                    fontsize=10, fontweight='bold', color="black")

        ax.axhline(overall_avg, color=PALETTE["accent_emerald"], linestyle='--', linewidth=1.5,
                   label=f"Bank Benchmark: {overall_avg:.1f}")
        ax.set_xticks(x)
        ax.set_xticklabels(metric_cols, rotation=25, ha='right', fontsize=11, color="black")
        ax.set_ylabel("Average Score (0-100)", fontsize=12, fontweight='bold', color="black")
        ax.set_title("Bank-Wide Parameter Benchmark (NaN-Adjusted)", fontsize=14, fontweight='bold',
                     color="black", pad=14)
        ax.set_ylim(0, 115)
        ax.legend(frameon=False, loc="upper right")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.display_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    # 2. Credit Rating Distribution
    def render_rating_distribution(self):
        self.clear_display()
        flat_scores = self.data.iloc[:, 2:].to_numpy(dtype=float).flatten()
        valid_scores = flat_scores[~np.isnan(flat_scores)]

        bins = [0, 60, 70, 80, 90, 101]
        labels = ['Very Poor (<60)', 'Poor (60-69)', 'Fair (70-79)', 'Good (80-89)', 'Excellent (90-100)']
        counts, _ = np.histogram(valid_scores, bins=bins)
        colors = ['#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#10b981']

        fig = Figure(figsize=(9, 4.8), dpi=105)
        ax = fig.add_subplot(111)
        self.format_plot(ax, fig)

        bars = ax.bar(labels, counts, color=colors, alpha=0.88, edgecolor='none')
        total = np.sum(counts)

        for b in bars:
            h = b.get_height()
            pct = (h / total) * 100 if total > 0 else 0
            ax.text(b.get_x() + b.get_width()/2., h + (total * 0.015), f"{int(h)}\n({pct:.1f}%)",
                    ha='center', va='bottom', fontsize=10, fontweight='bold', color="black")

        ax.set_ylabel("Count of Metric Evaluations", fontsize=12, fontweight='bold', color="black")
        ax.set_title("Credit Rating Tier Distribution (All Financial Parameters)", fontsize=14,
                     fontweight='bold', color="black", pad=14)
        ax.set_xticklabels(labels, fontsize=11, color="black")
        ax.set_ylim(0, max(counts) * 1.25)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.display_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    # 3. Customer Statistics
    def render_customer_statistics(self):
        self.clear_display()
        cid, name, series = self.get_customer_vector()
        if series is None:
            return

        values = series.to_numpy(dtype=float)
        mode = self.sub_option_var.get()

        mean_val = np.nanmean(values)
        valid_idx = np.where(~np.isnan(values))[0]

        card = tk.Frame(self.display_card, bg=PALETTE["card_bg"], padx=24, pady=24)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text=f"Customer Financial Profile: {name}", font=("Segoe UI", 14, "bold"),
                 bg=PALETTE["card_bg"], fg=PALETTE["text_dark"]).pack(anchor=tk.W, pady=(0, 2))
        tk.Label(card, text=f"Account ID: {cid} | Analysis Type: {mode.upper()}", font=("Segoe UI", 9),
                 bg=PALETTE["card_bg"], fg=PALETTE["text_muted"]).pack(anchor=tk.W, pady=(0, 16))

        # KPI Badges Frame
        kpi_frame = tk.Frame(card, bg=PALETTE["bg_main"], padx=14, pady=14)
        kpi_frame.pack(fill=tk.X, pady=(0, 16))

        if len(valid_idx) > 0:
            max_pos = valid_idx[np.argmax(values[valid_idx])]
            min_pos = valid_idx[np.argmin(values[valid_idx])]
            top_param = f"{series.index[max_pos]} ({values[max_pos]:.1f})"
            low_param = f"{series.index[min_pos]} ({values[min_pos]:.1f})"
        else:
            top_param, low_param = "N/A", "N/A"

        metrics_show = []
        if mode in ["all", "avg"]:
            metrics_show.append(("Mean Health Score", f"{mean_val:.2f} / 100", PALETTE["accent_indigo"]))
        if mode in ["all", "max"]:
            metrics_show.append(("Strongest Metric", top_param, PALETTE["accent_emerald"]))
        if mode in ["all", "min"]:
            metrics_show.append(("Areas for Improvement", low_param, "#ef4444"))

        for i, (title, val_str, color) in enumerate(metrics_show):
            box = tk.Frame(kpi_frame, bg=PALETTE["card_bg"], padx=12, pady=10, relief=tk.GROOVE, bd=1)
            box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
            tk.Label(box, text=title, font=("Segoe UI", 8, "bold"), bg=PALETTE["card_bg"], fg=PALETTE["text_muted"]).pack(anchor=tk.W)
            tk.Label(box, text=val_str, font=("Segoe UI", 11, "bold"), bg=PALETTE["card_bg"], fg=color).pack(anchor=tk.W, pady=(4, 0))

        # Parameter Table
        if mode == "all":
            table_frame = tk.Frame(card, bg=PALETTE["card_bg"])
            table_frame.pack(fill=tk.BOTH, expand=True)

            tk.Label(table_frame, text="Individual Metric Score Breakdown", font=("Segoe UI", 10, "bold"),
                     bg=PALETTE["card_bg"], fg=PALETTE["text_dark"]).pack(anchor=tk.W, pady=(8, 4))

            for p_name, score in series.items():
                row = tk.Frame(table_frame, bg=PALETTE["card_bg"], pady=3)
                row.pack(fill=tk.X)
                val_text = f"{score:.1f}" if not np.isnan(score) else "Missing (NaN)"
                color_text = PALETTE["text_dark"] if not np.isnan(score) else "#ef4444"

                tk.Label(row, text=f"•  {p_name}", font=("Segoe UI", 9), bg=PALETTE["card_bg"],
                         fg=PALETTE["text_muted"], width=30, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=val_text, font=("Segoe UI", 9, "bold"), bg=PALETTE["card_bg"],
                         fg=color_text).pack(side=tk.LEFT)

    # 4. Compare vs Bank Average
    def render_comparison(self):
        self.clear_display()
        cid, name, series = self.get_customer_vector()
        if series is None:
            return

        params = list(series.index)
        cust_scores = series.to_numpy(dtype=float)
        bank_means = np.nanmean(self.data[params].to_numpy(dtype=float), axis=0)

        # Replace NaNs with 0 for rendering comparison bars cleanly
        plot_cust = np.nan_to_num(cust_scores, nan=0.0)

        fig = Figure(figsize=(9, 4.8), dpi=105)
        ax = fig.add_subplot(111)
        self.format_plot(ax, fig)

        x = np.arange(len(params))
        width = 0.35

        b1 = ax.bar(x - width/2, plot_cust, width, label=name, color=PALETTE["accent_indigo"], alpha=0.9)
        b2 = ax.bar(x + width/2, bank_means, width, label="Bank Benchmark", color=PALETTE["border"], alpha=0.9)

        ax.set_xticks(x)
        ax.set_xticklabels(params, rotation=25, ha='right', fontsize=11, color="black")
        ax.set_ylabel("Score", fontsize=12, fontweight='bold', color="black")
        ax.set_title(f"Score Comparison: {name} vs. Bank Average", fontsize=14, fontweight='bold',
                     color="black", pad=14)
        ax.set_ylim(0, 115)
        ax.legend(frameon=False, loc="upper right", fontsize=10)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.display_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

    # 5. Credit Rating & Score Trend
    def render_trend_and_rating(self):
        self.clear_display()
        cid, name, series = self.get_customer_vector()
        if series is None:
            return

        scores = series.to_numpy(dtype=float)
        avg_score = np.nanmean(scores)

        grade = ("A (Tier 1 Prime)" if avg_score >= 90 else
                 "B (Tier 2 Good)" if avg_score >= 80 else
                 "C (Tier 3 Moderate)" if avg_score >= 70 else
                 "D (Tier 4 Watchlist)" if avg_score >= 60 else "E (High Risk)")

        fig = Figure(figsize=(9, 4.8), dpi=105)
        ax = fig.add_subplot(111)
        self.format_plot(ax, fig)

        params = list(series.index)
        ax.plot(params, scores, marker='o', color=PALETTE["accent_indigo"], linewidth=2.4,
                markersize=6, label="Score Trajectory")
        ax.axhline(80, color=PALETTE["accent_emerald"], linestyle=':', linewidth=1.4, label="Good Standing (80)")
        ax.axhline(60, color='#ef4444', linestyle=':', linewidth=1.4, label="Risk Cutoff (60)")

        for i, s in enumerate(scores):
            if not np.isnan(s):
                ax.text(i, s + 3, f"{s:.0f}", ha='center', fontsize=10, fontweight='bold', color="black")

        ax.set_xticks(range(len(params)))
        ax.set_xticklabels(params, rotation=25, ha='right', fontsize=11, color="black")
        ax.set_ylim(0, 115)
        ax.set_title(f"Performance Profile: {name}  |  Credit Rating: {grade}",
                     fontsize=14, fontweight='bold', color="black", pad=14)
        ax.legend(frameon=False, loc="lower left", fontsize=10)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.display_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=12, pady=12)


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernBankAnalysisGUI(root)
    root.mainloop()
