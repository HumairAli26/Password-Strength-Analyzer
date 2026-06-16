"""
Password Strength Checker
--------------------------
Checks whether a password is Weak, Medium, Strong, or Very Strong.
Features:
  - Light / Dark theme toggle
  - Live strength meter (4 segments)
  - Criteria checklist with animated ticks
  - Matplotlib bar chart + radial gauge embedded in the UI
"""

import re
import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Palette ────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":          "#F8F9FB",
        "panel":       "#FFFFFF",
        "border":      "#E2E6EC",
        "text":        "#1A1D23",
        "subtext":     "#6B7280",
        "input_bg":    "#F3F5F8",
        "input_fg":    "#1A1D23",
        "accent":      "#5B4FE8",
        "weak":        "#E24B4A",
        "medium":      "#E88C30",
        "strong":      "#1D9E75",
        "vstrong":     "#5B4FE8",
        "seg_empty":   "#E8EBF0",
        "check_ok":    "#1D9E75",
        "check_off":   "#CBD2DC",
        "chart_bg":    "#FFFFFF",
        "chart_text":  "#6B7280",
        "chart_grid":  "#F0F2F5",
        "toggle_on":   "#5B4FE8",
        "toggle_off":  "#CBD2DC",
        "title_fg":    "#1A1D23",
        "btn_fg":      "#FFFFFF",
    },
    "dark": {
        "bg":          "#0F1117",
        "panel":       "#1C1F2E",
        "border":      "#2E3347",
        "text":        "#E8EBF5",
        "subtext":     "#8B92A8",
        "input_bg":    "#252939",
        "input_fg":    "#E8EBF5",
        "accent":      "#7C72FF",
        "weak":        "#F87171",
        "medium":      "#FBBF24",
        "strong":      "#34D399",
        "vstrong":     "#A78BFA",
        "seg_empty":   "#2E3347",
        "check_ok":    "#34D399",
        "check_off":   "#3A3F52",
        "chart_bg":    "#1C1F2E",
        "chart_text":  "#8B92A8",
        "chart_grid":  "#252939",
        "toggle_on":   "#7C72FF",
        "toggle_off":  "#3A3F52",
        "title_fg":    "#E8EBF5",
        "btn_fg":      "#FFFFFF",
    },
}

CRITERIA_LABELS = [
    ("8+ characters",    lambda p: len(p) >= 8),
    ("Uppercase letter", lambda p: bool(re.search(r"[A-Z]", p))),
    ("Lowercase letter", lambda p: bool(re.search(r"[a-z]", p))),
    ("Contains a number",lambda p: bool(re.search(r"[0-9]", p))),
    ("Special symbol",   lambda p: bool(re.search(r"[^A-Za-z0-9]", p))),
    ("12+ characters",   lambda p: len(p) >= 12),
]

BAR_LABELS  = ["Length", "Uppercase", "Lowercase", "Numbers", "Symbols"]
BAR_COLORS_LIGHT = ["#5B4FE8", "#1D9E75", "#185FA5", "#BA7517", "#993556"]
BAR_COLORS_DARK  = ["#7C72FF", "#34D399", "#60A5FA", "#FBBF24", "#F472B6"]


def score_password(pw: str):
    checks = [fn(pw) for _, fn in CRITERIA_LABELS]
    score  = sum(checks)
    if not pw:
        return 0, checks, "—"
    if score <= 2:
        return score, checks, "Weak"
    if score <= 4:
        return score, checks, "Medium"
    if score == 5:
        return score, checks, "Strong"
    return score, checks, "Very Strong"


def bar_values(pw: str):
    length_score = min(1.0, len(pw) / 16)
    upper  = min(1.0, len(re.findall(r"[A-Z]", pw)) / max(1, len(pw) * 0.3))
    lower  = min(1.0, len(re.findall(r"[a-z]", pw)) / max(1, len(pw) * 0.3))
    digits = min(1.0, len(re.findall(r"[0-9]", pw)) / 3)
    syms   = min(1.0, len(re.findall(r"[^A-Za-z0-9]", pw)) / 2)
    return [length_score, upper, lower, digits, syms]


# ── Main App ───────────────────────────────────────────────────────────────────

class PasswordCheckerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Password Strength Checker")
        self.root.resizable(False, False)
        self.current_theme = "light"
        self.show_pw = False

        self._build_ui()
        self._apply_theme()

    # ── Build ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = self.root

        # outer frame
        self.outer = tk.Frame(root)
        self.outer.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Header bar ──
        self.header = tk.Frame(self.outer, height=56)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.title_lbl = tk.Label(
            self.header, text="🔐  Password Strength Checker",
            font=("Helvetica Neue", 15, "bold"), anchor="w"
        )
        self.title_lbl.pack(side="left", padx=20)

        # theme toggle button
        self.toggle_btn = tk.Button(
            self.header, text="☀  Light", width=10,
            relief="flat", cursor="hand2", bd=0,
            font=("Helvetica Neue", 11),
            command=self._toggle_theme
        )
        self.toggle_btn.pack(side="right", padx=20)

        # ── Main content panel ──
        self.panel = tk.Frame(self.outer, padx=28, pady=22)
        self.panel.pack(fill="both", expand=True)

        # Password input row
        self.pw_lbl = tk.Label(
            self.panel, text="Enter password", font=("Helvetica Neue", 11),
            anchor="w"
        )
        self.pw_lbl.pack(fill="x", pady=(0, 5))

        inp_frame = tk.Frame(self.panel, height=44)
        inp_frame.pack(fill="x")
        inp_frame.pack_propagate(False)

        self.inp_bg = tk.Frame(inp_frame)
        self.inp_bg.pack(fill="both", expand=True)

        self.pw_var = tk.StringVar()
        self.pw_var.trace_add("write", self._on_change)

        self.pw_entry = tk.Entry(
            self.inp_bg, textvariable=self.pw_var,
            show="•", font=("Courier New", 14), relief="flat",
            bd=0, highlightthickness=0
        )
        self.pw_entry.pack(side="left", fill="both", expand=True, padx=(14, 6), pady=10)

        self.eye_btn = tk.Button(
            self.inp_bg, text="👁", relief="flat", cursor="hand2",
            font=("Helvetica Neue", 13), bd=0, highlightthickness=0,
            command=self._toggle_pw_vis
        )
        self.eye_btn.pack(side="right", padx=(0, 10))

        # Strength meter (4 segments)
        self.meter_frame = tk.Frame(self.panel, height=8)
        self.meter_frame.pack(fill="x", pady=(12, 0))
        self.meter_frame.pack_propagate(False)

        self.seg_canvases = []
        for i in range(4):
            c = tk.Canvas(self.meter_frame, height=8, bd=0,
                          highlightthickness=0, relief="flat")
            c.pack(side="left", fill="x", expand=True,
                   padx=(0 if i == 3 else 4, 0))
            self.seg_canvases.append(c)

        # Strength label
        self.strength_lbl = tk.Label(
            self.panel, text="Enter a password to check",
            font=("Helvetica Neue", 12, "bold"), anchor="w"
        )
        self.strength_lbl.pack(fill="x", pady=(10, 6))

        # Divider
        self.div1 = tk.Frame(self.panel, height=1)
        self.div1.pack(fill="x", pady=(0, 14))

        # Criteria checklist — 2-column grid
        self.crit_lbl = tk.Label(
            self.panel, text="CRITERIA", font=("Helvetica Neue", 9),
            anchor="w"
        )
        self.crit_lbl.pack(fill="x", pady=(0, 8))

        self.crit_outer = tk.Frame(self.panel)
        self.crit_outer.pack(fill="x")

        self.crit_frames = []
        self.crit_dots   = []
        self.crit_texts  = []

        for i, (label, _) in enumerate(CRITERIA_LABELS):
            col = i % 2
            row = i // 2
            cf = tk.Frame(self.crit_outer)
            cf.grid(row=row, column=col, sticky="w", padx=(0, 16), pady=3)

            dot = tk.Label(cf, text="○", font=("Helvetica Neue", 13), width=2)
            dot.pack(side="left")
            txt = tk.Label(cf, text=label, font=("Helvetica Neue", 11))
            txt.pack(side="left")

            self.crit_frames.append(cf)
            self.crit_dots.append(dot)
            self.crit_texts.append(txt)

        # Divider
        self.div2 = tk.Frame(self.panel, height=1)
        self.div2.pack(fill="x", pady=(16, 14))

        # Charts section label
        self.chart_lbl = tk.Label(
            self.panel, text="ANALYSIS", font=("Helvetica Neue", 9), anchor="w"
        )
        self.chart_lbl.pack(fill="x", pady=(0, 10))

        # Matplotlib figure
        self.fig, (self.ax_bar, self.ax_gauge) = plt.subplots(
            1, 2, figsize=(6.6, 2.4),
            gridspec_kw={"width_ratios": [1.6, 1]}
        )
        self.fig.subplots_adjust(left=0.01, right=0.99, top=0.88,
                                  bottom=0.18, wspace=0.3)

        self.canvas_mpl = FigureCanvasTkAgg(self.fig, master=self.panel)
        self.canvas_mpl.get_tk_widget().pack(fill="x")

        self._draw_charts("", 0, [False]*6, "—")

    # ── Theme ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme()
        pw = self.pw_var.get()
        score, checks, level = score_password(pw)
        self._update_ui(pw, score, checks, level)

    def _apply_theme(self):
        t = THEMES[self.current_theme]
        is_dark = self.current_theme == "dark"

        self.root.configure(bg=t["bg"])
        self.outer.configure(bg=t["bg"])

        self.header.configure(bg=t["panel"])
        self.title_lbl.configure(bg=t["panel"], fg=t["title_fg"])
        self.toggle_btn.configure(
            bg=t["toggle_on"] if is_dark else t["accent"],
            fg=t["btn_fg"],
            text="🌙  Dark" if is_dark else "☀  Light"
        )

        self.panel.configure(bg=t["bg"])
        self.pw_lbl.configure(bg=t["bg"], fg=t["subtext"])
        self.inp_bg.configure(bg=t["input_bg"],
                               highlightbackground=t["border"],
                               highlightthickness=1)
        self.pw_entry.configure(bg=t["input_bg"], fg=t["input_fg"],
                                 insertbackground=t["text"])
        self.eye_btn.configure(bg=t["input_bg"], activebackground=t["input_bg"])

        for c in self.seg_canvases:
            c.configure(bg=t["bg"])

        self.strength_lbl.configure(bg=t["bg"], fg=t["subtext"])
        self.div1.configure(bg=t["border"])
        self.div2.configure(bg=t["border"])

        self.crit_lbl.configure(bg=t["bg"], fg=t["subtext"])
        self.crit_outer.configure(bg=t["bg"])
        self.chart_lbl.configure(bg=t["bg"], fg=t["subtext"])

        for cf, dot, txt in zip(self.crit_frames, self.crit_dots, self.crit_texts):
            cf.configure(bg=t["bg"])
            dot.configure(bg=t["bg"], fg=t["check_off"])
            txt.configure(bg=t["bg"], fg=t["subtext"])

    # ── Logic ──────────────────────────────────────────────────────────────────

    def _on_change(self, *_):
        pw = self.pw_var.get()
        score, checks, level = score_password(pw)
        self._update_ui(pw, score, checks, level)

    def _toggle_pw_vis(self):
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "•")
        self.eye_btn.config(text="🙈" if self.show_pw else "👁")

    def _update_ui(self, pw, score, checks, level):
        t = THEMES[self.current_theme]

        # color for current level
        color_map = {
            "Weak":        t["weak"],
            "Medium":      t["medium"],
            "Strong":      t["strong"],
            "Very Strong": t["vstrong"],
            "—":           t["subtext"],
        }
        lvl_color = color_map.get(level, t["subtext"])

        # meter
        segs_lit = {0: 0, "—": 0, "Weak": 1, "Medium": 2,
                    "Strong": 3, "Very Strong": 4}.get(level if pw else 0, 0)
        for i, c in enumerate(self.seg_canvases):
            fill = lvl_color if i < segs_lit else t["seg_empty"]
            c.delete("all")
            w = c.winfo_width() or 120
            c.create_rectangle(0, 0, w, 8, fill=fill, outline="", width=0)

        # strength label
        icons = {"Weak": "⚠", "Medium": "~", "Strong": "✓", "Very Strong": "✓✓"}
        if pw:
            txt = f"{icons.get(level,'')}  {level}"
        else:
            txt = "Enter a password to check"
        self.strength_lbl.config(text=txt, fg=lvl_color if pw else t["subtext"])

        # criteria dots
        for i, (met, dot, txt_lbl) in enumerate(
                zip(checks, self.crit_dots, self.crit_texts)):
            dot.config(text="●" if met else "○",
                       fg=t["check_ok"] if met else t["check_off"])
            txt_lbl.config(fg=t["text"] if met else t["subtext"])

        # charts
        self._draw_charts(pw, score, checks, level)

    # ── Charts ─────────────────────────────────────────────────────────────────

    def _draw_charts(self, pw, score, checks, level):
        t   = THEMES[self.current_theme]
        is_dark = self.current_theme == "dark"
        bar_colors = BAR_COLORS_DARK if is_dark else BAR_COLORS_LIGHT

        vals = bar_values(pw) if pw else [0.0] * 5

        # ── Bar chart ──
        ax = self.ax_bar
        ax.clear()
        ax.set_facecolor(t["chart_bg"])
        self.fig.patch.set_facecolor(t["chart_bg"])

        y_pos = np.arange(len(BAR_LABELS))
        bars  = ax.barh(y_pos, [v * 100 for v in vals],
                        color=bar_colors, height=0.55,
                        left=0)

        # subtle background track bars
        ax.barh(y_pos, [100] * 5, color=t["seg_empty"],
                height=0.55, left=0, zorder=0)
        # replot data bars on top
        ax.barh(y_pos, [v * 100 for v in vals],
                color=bar_colors, height=0.55, left=0, zorder=1)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(BAR_LABELS, fontsize=8.5,
                           color=t["chart_text"], fontfamily="sans-serif")
        ax.set_xlim(0, 112)
        ax.set_ylim(-0.6, 4.6)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(["0", "25", "50", "75", "100"],
                           fontsize=7.5, color=t["chart_text"])
        ax.set_title("Criteria breakdown", fontsize=9, fontweight="bold",
                     color=t["chart_text"], pad=6)
        ax.tick_params(axis="both", length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.grid(axis="x", color=t["chart_grid"], linewidth=0.5, zorder=0)

        # value labels on bars
        for i, v in enumerate(vals):
            pct = int(v * 100)
            ax.text(min(pct + 2, 104), i, f"{pct}%",
                    va="center", fontsize=7.5, color=t["chart_text"])

        # ── Radial gauge ──
        ax2 = self.ax_gauge
        ax2.clear()
        ax2.set_facecolor(t["chart_bg"])
        ax2.set_aspect("equal")
        ax2.set_xlim(-1.2, 1.2)
        ax2.set_ylim(-1.0, 1.3)
        ax2.axis("off")
        ax2.set_title("Score", fontsize=9, fontweight="bold",
                      color=t["chart_text"], pad=4)

        # background arc
        theta_bg = np.linspace(np.pi, 0, 200)
        ax2.plot(np.cos(theta_bg), np.sin(theta_bg),
                 color=t["seg_empty"], linewidth=14, solid_capstyle="round",
                 zorder=1)

        # foreground arc
        color_map = {
            "Weak":        THEMES[self.current_theme]["weak"],
            "Medium":      THEMES[self.current_theme]["medium"],
            "Strong":      THEMES[self.current_theme]["strong"],
            "Very Strong": THEMES[self.current_theme]["vstrong"],
            "—":           t["seg_empty"],
        }
        arc_color = color_map.get(level, t["seg_empty"])
        frac = score / 6
        if frac > 0:
            theta_fg = np.linspace(np.pi, np.pi - frac * np.pi, 200)
            ax2.plot(np.cos(theta_fg), np.sin(theta_fg),
                     color=arc_color, linewidth=14,
                     solid_capstyle="round", zorder=2)

        # center score text
        ax2.text(0, 0.08, str(score), ha="center", va="center",
                 fontsize=30, fontweight="bold",
                 color=arc_color if pw else t["subtext"],
                 fontfamily="sans-serif")
        ax2.text(0, -0.3, "out of 6", ha="center", va="center",
                 fontsize=8, color=t["chart_text"])

        self.canvas_mpl.draw()


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("680x700")
    root.minsize(580, 620)
    app = PasswordCheckerApp(root)
    root.mainloop()
