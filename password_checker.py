"""
Password Strength Checker — Enhanced Edition
=============================================
Features:
  • Live strength meter with coloured segments
  • Entropy & estimated crack-time display
  • 6-criteria checklist with icons
  • One-click password generator (length + charset toggles)
  • Copy-to-clipboard with flash feedback
  • Password history (last 5 entries, clearable, masked)
  • Improved bar chart: rounded caps, dashed grid, percent labels
  • Semicircular radial gauge with level label
  • Light / Dark theme toggle
  • Scrollable layout
"""

import re, math, random, string
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ── Palette ────────────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":         "#F4F6FB",
        "panel":      "#FFFFFF",
        "border":     "#DDE2EE",
        "text":       "#1A1D2E",
        "subtext":    "#6B7280",
        "hint":       "#9CA3AF",
        "input_bg":   "#FFFFFF",
        "input_fg":   "#1A1D2E",
        "accent":     "#5B4FE8",
        "accent2":    "#7C72FF",
        "weak":       "#E24B4A",
        "medium":     "#E88C30",
        "strong":     "#1D9E75",
        "vstrong":    "#5B4FE8",
        "seg_empty":  "#E4E8F0",
        "check_ok":   "#1D9E75",
        "check_off":  "#D1D8E5",
        "chart_bg":   "#FFFFFF",
        "chart_text": "#6B7280",
        "chart_grid": "#EEF1F7",
        "title_fg":   "#1A1D2E",
        "btn_fg":     "#FFFFFF",
        "hist_bg":    "#F8FAFD",
        "hist_fg":    "#1A1D2E",
        "copy_ok":    "#1D9E75",
        "gen_bg":     "#5B4FE8",
    },
    "dark": {
        "bg":         "#0D0F1A",
        "panel":      "#181B2A",
        "border":     "#2A2F45",
        "text":       "#E8EBF5",
        "subtext":    "#8B92A8",
        "hint":       "#5A6180",
        "input_bg":   "#1E2235",
        "input_fg":   "#E8EBF5",
        "accent":     "#7C72FF",
        "accent2":    "#9D95FF",
        "weak":       "#F87171",
        "medium":     "#FBBF24",
        "strong":     "#34D399",
        "vstrong":    "#A78BFA",
        "seg_empty":  "#252A3D",
        "check_ok":   "#34D399",
        "check_off":  "#2E3450",
        "chart_bg":   "#181B2A",
        "chart_text": "#8B92A8",
        "chart_grid": "#1E2235",
        "title_fg":   "#E8EBF5",
        "btn_fg":     "#FFFFFF",
        "hist_bg":    "#1E2235",
        "hist_fg":    "#E8EBF5",
        "copy_ok":    "#34D399",
        "gen_bg":     "#7C72FF",
    },
}

CRITERIA = [
    ("8+ characters",    "📏", lambda p: len(p) >= 8),
    ("Uppercase letter", "🔠", lambda p: bool(re.search(r"[A-Z]", p))),
    ("Lowercase letter", "🔡", lambda p: bool(re.search(r"[a-z]", p))),
    ("Contains number",  "🔢", lambda p: bool(re.search(r"[0-9]", p))),
    ("Special symbol",   "✦",  lambda p: bool(re.search(r"[^A-Za-z0-9]", p))),
    ("12+ characters",   "🛡",  lambda p: len(p) >= 12),
]

BAR_LABELS     = ["Length", "Uppercase", "Lowercase", "Numbers", "Symbols"]
BAR_COLS_LIGHT = ["#5B4FE8", "#1D9E75", "#185FA5", "#D97706", "#BE185D"]
BAR_COLS_DARK  = ["#7C72FF", "#34D399", "#60A5FA", "#FBBF24", "#F472B6"]

# ── Password helpers ───────────────────────────────────────────────────────────

def score_password(pw: str):
    checks = [fn(pw) for _, _, fn in CRITERIA]
    score  = sum(checks)
    if not pw:               return 0, checks, "—"
    if score <= 2:           return score, checks, "Weak"
    if score <= 4:           return score, checks, "Medium"
    if score == 5:           return score, checks, "Strong"
    return score, checks, "Very Strong"

def bar_values(pw: str):
    if not pw:
        return [0.0] * 5
    n = len(pw)
    return [
        min(1.0, n / 16),
        min(1.0, len(re.findall(r"[A-Z]", pw)) / max(1, n * 0.3)),
        min(1.0, len(re.findall(r"[a-z]", pw)) / max(1, n * 0.3)),
        min(1.0, len(re.findall(r"[0-9]", pw)) / 3),
        min(1.0, len(re.findall(r"[^A-Za-z0-9]", pw)) / 2),
    ]

def entropy_bits(pw: str) -> float:
    if not pw: return 0.0
    pool = 0
    if re.search(r"[a-z]", pw): pool += 26
    if re.search(r"[A-Z]", pw): pool += 26
    if re.search(r"[0-9]", pw): pool += 10
    if re.search(r"[^A-Za-z0-9]", pw): pool += 32
    return len(pw) * math.log2(pool) if pool else 0.0

def crack_time_label(bits: float) -> str:
    if bits == 0: return "—"
    s = (2 ** bits) / 1e10          # 10 billion guesses/sec (fast offline)
    if s < 1:          return "< 1 second"
    if s < 60:         return f"{int(s)} seconds"
    if s < 3600:       return f"{int(s/60)} minutes"
    if s < 86400:      return f"{int(s/3600)} hours"
    if s < 2_592_000:  return f"{int(s/86400)} days"
    if s < 31_536_000: return f"{int(s/2_592_000)} months"
    if s < 3.156e9:    return f"{int(s/31_536_000)} years"
    if s < 3.156e12:   return f"{int(s/3.156e9)}K years"
    if s < 3.156e15:   return f"{int(s/3.156e12)}M years"
    return "Centuries+"

def generate_password(length=16, upper=True, digits=True, symbols=True) -> str:
    pool = list(string.ascii_lowercase)
    guaranteed = [random.choice(string.ascii_lowercase)]
    if upper:
        pool += list(string.ascii_uppercase)
        guaranteed.append(random.choice(string.ascii_uppercase))
    if digits:
        pool += list(string.digits)
        guaranteed.append(random.choice(string.digits))
    if symbols:
        sym = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        pool += list(sym)
        guaranteed.append(random.choice(sym))
    rest = [random.choice(pool) for _ in range(length - len(guaranteed))]
    combo = guaranteed + rest
    random.shuffle(combo)
    return "".join(combo)

# ── App ────────────────────────────────────────────────────────────────────────

class App:
    def __init__(self, root: tk.Tk):
        self.root       = root
        self.theme      = "light"
        self.show_pw    = False
        self.history    = []          # list of (pw, level)
        self._copy_job  = None
        self._cb_refs   = []          # checkbutton widget refs
        self._build()
        self._apply_theme()
        self.root.after(100, lambda: self._update("", 0, [False]*6, "—"))

    # ── BUILD ──────────────────────────────────────────────────────────────────

    def _build(self):

        # ── Header ──────────────────────────────────────────────────────────
        self.header = tk.Frame(self.root, height=58)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.hdr_title = tk.Label(
            self.header, text="🔐  Password Strength Checker",
            font=("Helvetica Neue", 16, "bold"), anchor="w")
        self.hdr_title.pack(side="left", padx=22)

        self.theme_btn = tk.Button(
            self.header, text="🌙  Dark", width=10,
            relief="flat", cursor="hand2", bd=0,
            font=("Helvetica Neue", 11),
            command=self._toggle_theme)
        self.theme_btn.pack(side="right", padx=18, pady=10)

        # ── Scrollable area ─────────────────────────────────────────────────
        self.vscroll = tk.Scrollbar(self.root, orient="vertical")
        self.vscroll.pack(side="right", fill="y")

        self.scr_canvas = tk.Canvas(
            self.root, bd=0, highlightthickness=0,
            yscrollcommand=self.vscroll.set)
        self.scr_canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.config(command=self.scr_canvas.yview)

        self.main = tk.Frame(self.scr_canvas)
        self._main_id = self.scr_canvas.create_window(
            (0, 0), window=self.main, anchor="nw")

        self.main.bind("<Configure>",
            lambda e: self.scr_canvas.configure(
                scrollregion=self.scr_canvas.bbox("all")))
        self.scr_canvas.bind("<Configure>",
            lambda e: self.scr_canvas.itemconfig(
                self._main_id, width=e.width))
        self.scr_canvas.bind_all("<MouseWheel>",
            lambda e: self.scr_canvas.yview_scroll(
                int(-1*(e.delta/120)), "units"))

        PX = 24   # horizontal padding for cards

        # ── Input card ──────────────────────────────────────────────────────
        self.input_card = self._card(self.main)
        self.input_card.pack(fill="x", padx=PX, pady=(20, 0))

        self.pw_label = tk.Label(
            self.input_card, text="Password",
            font=("Helvetica Neue", 11), anchor="w")
        self.pw_label.pack(fill="x", padx=16, pady=(14, 6))

        # input inner frame (acts as bordered box)
        self.inp_wrap = tk.Frame(self.input_card, height=48)
        self.inp_wrap.pack(fill="x", padx=16)
        self.inp_wrap.pack_propagate(False)

        self.inp_inner = tk.Frame(self.inp_wrap)
        self.inp_inner.pack(fill="both", expand=True)

        self.pw_var = tk.StringVar()
        self.pw_var.trace_add("write", self._on_pw_change)

        self.pw_entry = tk.Entry(
            self.inp_inner, textvariable=self.pw_var,
            show="•", font=("Courier New", 14),
            relief="flat", bd=0, highlightthickness=0)
        self.pw_entry.pack(
            side="left", fill="both", expand=True,
            padx=(14, 0), pady=12)

        self.eye_btn = tk.Button(
            self.inp_inner, text="👁", relief="flat", cursor="hand2",
            font=("Helvetica Neue", 14), bd=0, highlightthickness=0,
            command=self._toggle_vis)
        self.eye_btn.pack(side="right", padx=6)

        self.copy_btn = tk.Button(
            self.inp_inner, text="⎘ Copy", relief="flat", cursor="hand2",
            font=("Helvetica Neue", 10), bd=0, highlightthickness=0,
            padx=8, command=self._copy_pw)
        self.copy_btn.pack(side="right", padx=4)

        # strength meter (4 rounded segments)
        self.meter_frame = tk.Frame(self.input_card, height=6)
        self.meter_frame.pack(fill="x", padx=16, pady=(10, 0))
        self.meter_frame.pack_propagate(False)
        self.segs = []
        for i in range(4):
            c = tk.Canvas(self.meter_frame, height=6,
                          bd=0, highlightthickness=0)
            c.pack(side="left", fill="x", expand=True,
                   padx=(0, 4 if i < 3 else 0))
            self.segs.append(c)

        # strength label + entropy on same row
        self.str_row = tk.Frame(self.input_card)
        self.str_row.pack(fill="x", padx=16, pady=(8, 0))

        self.str_lbl = tk.Label(
            self.str_row, text="Enter a password",
            font=("Helvetica Neue", 12, "bold"), anchor="w")
        self.str_lbl.pack(side="left")

        self.entropy_lbl = tk.Label(
            self.str_row, text="",
            font=("Helvetica Neue", 10), anchor="e")
        self.entropy_lbl.pack(side="right")

        # crack time row
        self.crack_row = tk.Frame(self.input_card)
        self.crack_row.pack(fill="x", padx=16, pady=(4, 14))

        self.crack_icon = tk.Label(
            self.crack_row, text="⏱", font=("Helvetica Neue", 11))
        self.crack_icon.pack(side="left")

        self.crack_lbl = tk.Label(
            self.crack_row, text="Est. crack time: —",
            font=("Helvetica Neue", 10), anchor="w")
        self.crack_lbl.pack(side="left", padx=(4, 0))

        # ── Generator card ───────────────────────────────────────────────────
        self.gen_card = self._card(self.main)
        self.gen_card.pack(fill="x", padx=PX, pady=(14, 0))

        gen_hdr = tk.Frame(self.gen_card)
        gen_hdr.pack(fill="x", padx=16, pady=(14, 8))

        self.gen_hdr_lbl = tk.Label(
            gen_hdr, text="⚡  Generate Password",
            font=("Helvetica Neue", 11, "bold"))
        self.gen_hdr_lbl.pack(side="left")

        self.gen_btn = tk.Button(
            gen_hdr, text="Generate", relief="flat", cursor="hand2",
            font=("Helvetica Neue", 10, "bold"), bd=0,
            padx=14, pady=5, command=self._generate)
        self.gen_btn.pack(side="right")

        # options row
        opt_row = tk.Frame(self.gen_card)
        opt_row.pack(fill="x", padx=16, pady=(0, 14))

        self.opt_row = opt_row   # save ref for theming

        tk.Label(opt_row, text="Length:",
                 font=("Helvetica Neue", 10)).pack(side="left")
        self._store(opt_row.winfo_children()[-1])

        self.gen_len = tk.IntVar(value=16)
        self.len_val_lbl = tk.Label(
            opt_row, text="16",
            font=("Helvetica Neue", 10, "bold"), width=3)
        self.len_val_lbl.pack(side="left", padx=(4, 0))

        self.len_slider = tk.Scale(
            opt_row, from_=8, to=32, orient="horizontal",
            variable=self.gen_len, showvalue=False, length=130,
            bd=0, highlightthickness=0, relief="flat",
            command=lambda v: self.len_val_lbl.config(text=v))
        self.len_slider.pack(side="left", padx=(6, 16))

        self.use_upper   = tk.BooleanVar(value=True)
        self.use_digits  = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        for var, lbl in [(self.use_upper, "A–Z"),
                         (self.use_digits, "0–9"),
                         (self.use_symbols, "!@#")]:
            cb = tk.Checkbutton(
                opt_row, text=lbl, variable=var,
                font=("Helvetica Neue", 10),
                relief="flat", bd=0, cursor="hand2",
                highlightthickness=0)
            cb.pack(side="left", padx=(0, 10))
            self._store(cb)

        # ── Criteria card ────────────────────────────────────────────────────
        self.crit_card = self._card(self.main)
        self.crit_card.pack(fill="x", padx=PX, pady=(14, 0))

        self.crit_hdr_lbl = tk.Label(
            self.crit_card, text="REQUIREMENTS",
            font=("Helvetica Neue", 9))
        self.crit_hdr_lbl.pack(fill="x", padx=16, pady=(14, 8), anchor="w")

        self.crit_grid = tk.Frame(self.crit_card)
        self.crit_grid.pack(fill="x", padx=16, pady=(0, 14))
        self.crit_grid.columnconfigure(0, weight=1)
        self.crit_grid.columnconfigure(1, weight=1)

        self.c_frames = []
        self.c_icons  = []
        self.c_checks = []
        self.c_texts  = []

        for i, (label, icon, _) in enumerate(CRITERIA):
            r, c = divmod(i, 2)
            cf = tk.Frame(self.crit_grid)
            cf.grid(row=r, column=c, sticky="w", pady=4, padx=(0, 8))

            ic = tk.Label(cf, text=icon,
                          font=("Helvetica Neue", 13), width=2)
            ic.pack(side="left")
            ck = tk.Label(cf, text="○",
                          font=("Helvetica Neue", 12), width=2)
            ck.pack(side="left")
            tx = tk.Label(cf, text=label,
                          font=("Helvetica Neue", 11))
            tx.pack(side="left")

            self.c_frames.append(cf)
            self.c_icons.append(ic)
            self.c_checks.append(ck)
            self.c_texts.append(tx)

        # ── Charts card ──────────────────────────────────────────────────────
        self.chart_card = self._card(self.main)
        self.chart_card.pack(fill="x", padx=PX, pady=(14, 0))

        self.chart_hdr_lbl = tk.Label(
            self.chart_card, text="ANALYSIS",
            font=("Helvetica Neue", 9))
        self.chart_hdr_lbl.pack(
            fill="x", padx=16, pady=(14, 8), anchor="w")

        self.fig = plt.figure(figsize=(6.8, 2.6))
        gs = self.fig.add_gridspec(
            1, 2, width_ratios=[1.65, 1],
            left=0.01, right=0.98,
            top=0.85, bottom=0.14, wspace=0.28)
        self.ax_bar   = self.fig.add_subplot(gs[0])
        self.ax_gauge = self.fig.add_subplot(gs[1])

        self.mpl_canvas = FigureCanvasTkAgg(
            self.fig, master=self.chart_card)
        self.mpl_canvas.get_tk_widget().pack(
            fill="x", padx=8, pady=(0, 8))

        # ── History card ─────────────────────────────────────────────────────
        self.hist_card = self._card(self.main)
        self.hist_card.pack(fill="x", padx=PX, pady=(14, 24))

        hist_hdr = tk.Frame(self.hist_card)
        hist_hdr.pack(fill="x", padx=16, pady=(14, 8))
        self.hist_hdr_frame = hist_hdr

        self.hist_hdr_lbl = tk.Label(
            hist_hdr, text="📋  Recent Passwords",
            font=("Helvetica Neue", 11, "bold"))
        self.hist_hdr_lbl.pack(side="left")

        self.clear_btn = tk.Button(
            hist_hdr, text="Clear", relief="flat", cursor="hand2",
            font=("Helvetica Neue", 10), bd=0,
            padx=10, pady=4, command=self._clear_history)
        self.clear_btn.pack(side="right")

        self.hist_inner = tk.Frame(self.hist_card)
        self.hist_inner.pack(fill="x", padx=16, pady=(0, 14))

        self.hist_rows = []
        for _ in range(5):
            row = tk.Frame(self.hist_inner, height=34)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            mask = tk.Label(row, text="",
                            font=("Courier New", 11), anchor="w")
            mask.pack(side="left", fill="both", expand=True,
                      padx=(10, 4), pady=6)

            badge = tk.Label(row, text="",
                             font=("Helvetica Neue", 9, "bold"),
                             padx=8, pady=2)
            badge.pack(side="right", padx=(4, 10), pady=8)

            self.hist_rows.append((row, mask, badge))

        self._draw_charts("", 0, [False]*6, "—")

    # helper: create a card frame with border
    def _card(self, parent):
        return tk.Frame(parent, bd=0,
                        highlightthickness=1, relief="flat")

    # store widget ref for theme sweeping
    def _store(self, w):
        self._cb_refs.append(w)

    # ── THEME ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()
        pw = self.pw_var.get()
        sc, ch, lv = score_password(pw)
        self._update(pw, sc, ch, lv)

    def _apply_theme(self):
        t       = THEMES[self.theme]
        is_dark = self.theme == "dark"

        self.root.configure(bg=t["bg"])
        self.scr_canvas.configure(bg=t["bg"])
        self.main.configure(bg=t["bg"])

        # header
        self.header.configure(bg=t["panel"])
        self.hdr_title.configure(bg=t["panel"], fg=t["title_fg"])
        self.theme_btn.configure(
            bg=t["accent"], fg=t["btn_fg"],
            activebackground=t["accent2"],
            activeforeground=t["btn_fg"],
            text="☀  Light" if is_dark else "🌙  Dark")

        # cards
        for card in (self.input_card, self.gen_card,
                      self.crit_card, self.chart_card, self.hist_card):
            card.configure(bg=t["panel"],
                           highlightbackground=t["border"])

        # ── input card widgets ──
        self.pw_label.configure(bg=t["panel"], fg=t["subtext"])
        self.inp_wrap.configure(bg=t["panel"])
        self.inp_inner.configure(
            bg=t["input_bg"],
            highlightbackground=t["border"],
            highlightthickness=1)
        self.pw_entry.configure(
            bg=t["input_bg"], fg=t["input_fg"],
            insertbackground=t["text"])
        self.eye_btn.configure(
            bg=t["input_bg"], fg=t["subtext"],
            activebackground=t["input_bg"],
            activeforeground=t["text"])
        self.copy_btn.configure(
            bg=t["input_bg"], fg=t["accent"],
            activebackground=t["input_bg"],
            activeforeground=t["accent2"])
        self.meter_frame.configure(bg=t["panel"])
        for c in self.segs:
            c.configure(bg=t["panel"])
        self.str_row.configure(bg=t["panel"])
        self.str_lbl.configure(bg=t["panel"], fg=t["subtext"])
        self.entropy_lbl.configure(bg=t["panel"], fg=t["subtext"])
        self.crack_row.configure(bg=t["panel"])
        self.crack_icon.configure(bg=t["panel"], fg=t["subtext"])
        self.crack_lbl.configure(bg=t["panel"], fg=t["subtext"])

        # ── generator card widgets ──
        self.gen_card.configure(bg=t["panel"])
        self.gen_hdr_lbl.configure(bg=t["panel"], fg=t["title_fg"])
        self.gen_btn.configure(
            bg=t["gen_bg"], fg=t["btn_fg"],
            activebackground=t["accent2"],
            activeforeground=t["btn_fg"])
        self.opt_row.configure(bg=t["panel"])
        self.len_val_lbl.configure(bg=t["panel"], fg=t["accent"])
        self.len_slider.configure(
            bg=t["panel"], fg=t["text"],
            troughcolor=t["seg_empty"],
            activebackground=t["accent"])
        for child in self.opt_row.winfo_children():
            cls = type(child).__name__
            if cls == "Label":
                child.configure(bg=t["panel"], fg=t["subtext"])
            elif cls == "Checkbutton":
                child.configure(
                    bg=t["panel"], fg=t["text"],
                    selectcolor=t["input_bg"],
                    activebackground=t["panel"],
                    activeforeground=t["accent"])

        # ── criteria card widgets ──
        self.crit_card.configure(bg=t["panel"])
        self.crit_hdr_lbl.configure(bg=t["panel"], fg=t["subtext"])
        self.crit_grid.configure(bg=t["panel"])
        for cf, ic, ck, tx in zip(
                self.c_frames, self.c_icons, self.c_checks, self.c_texts):
            cf.configure(bg=t["panel"])
            ic.configure(bg=t["panel"])
            ck.configure(bg=t["panel"], fg=t["check_off"])
            tx.configure(bg=t["panel"], fg=t["subtext"])

        # ── chart card widgets ──
        self.chart_card.configure(bg=t["panel"])
        self.chart_hdr_lbl.configure(bg=t["panel"], fg=t["subtext"])

        # ── history card widgets ──
        self.hist_card.configure(bg=t["panel"])
        self.hist_hdr_frame.configure(bg=t["panel"])
        self.hist_hdr_lbl.configure(bg=t["panel"], fg=t["title_fg"])
        self.clear_btn.configure(
            bg=t["panel"], fg=t["subtext"],
            activebackground=t["panel"])
        self.hist_inner.configure(bg=t["panel"])
        for row, mask, badge in self.hist_rows:
            row.configure(bg=t["hist_bg"],
                          highlightbackground=t["border"],
                          highlightthickness=1)
            mask.configure(bg=t["hist_bg"], fg=t["hist_fg"])
            badge.configure(bg=t["hist_bg"])

        self._refresh_history()

    # ── LOGIC ──────────────────────────────────────────────────────────────────

    def _on_pw_change(self, *_):
        pw = self.pw_var.get()
        sc, ch, lv = score_password(pw)
        self._update(pw, sc, ch, lv)

    def _toggle_vis(self):
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "•")
        self.eye_btn.config(text="🙈" if self.show_pw else "👁")

    def _copy_pw(self):
        pw = self.pw_var.get()
        if not pw:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        t = THEMES[self.theme]
        self.copy_btn.configure(text="✓ Copied!", fg=t["copy_ok"])
        if self._copy_job:
            self.root.after_cancel(self._copy_job)
        self._copy_job = self.root.after(
            1800,
            lambda: self.copy_btn.configure(text="⎘ Copy", fg=t["accent"]))

    def _generate(self):
        pw = generate_password(
            length=self.gen_len.get(),
            upper=self.use_upper.get(),
            digits=self.use_digits.get(),
            symbols=self.use_symbols.get())
        self.pw_var.set(pw)
        self.pw_entry.icursor("end")

    def _update(self, pw, score, checks, level):
        t = THEMES[self.theme]
        col_map = {
            "Weak":        t["weak"],
            "Medium":      t["medium"],
            "Strong":      t["strong"],
            "Very Strong": t["vstrong"],
            "—":           t["subtext"],
        }
        lc = col_map.get(level, t["subtext"])

        # segments
        n_lit = {"—":0,"Weak":1,"Medium":2,
                 "Strong":3,"Very Strong":4}.get(level if pw else "—", 0)
        for i, c in enumerate(self.segs):
            fill = lc if i < n_lit else t["seg_empty"]
            c.delete("all")
            w = c.winfo_width() or 140
            c.create_rectangle(0, 1, w, 5,
                               fill=fill, outline="", width=0)

        # strength label
        icons = {"Weak":"⚠ ","Medium":"~ ","Strong":"✓ ","Very Strong":"✓✓ "}
        self.str_lbl.configure(
            text=(icons.get(level,"") + level) if pw else "Enter a password",
            fg=lc if pw else t["subtext"])

        # entropy
        bits = entropy_bits(pw)
        self.entropy_lbl.configure(
            text=f"~{bits:.0f} bits entropy" if pw else "")

        # crack time
        self.crack_lbl.configure(
            text=f"Est. crack time: {crack_time_label(bits)}",
            fg=lc if pw else t["subtext"])
        self.crack_icon.configure(fg=lc if pw else t["subtext"])

        # criteria dots
        for met, ck, tx in zip(checks, self.c_checks, self.c_texts):
            ck.configure(
                text="●" if met else "○",
                fg=t["check_ok"] if met else t["check_off"])
            tx.configure(fg=t["text"] if met else t["subtext"])

        # history
        if pw and (not self.history or self.history[-1][0] != pw):
            self.history.append((pw, level))
            if len(self.history) > 5:
                self.history = self.history[-5:]
            self._refresh_history()

        self._draw_charts(pw, score, checks, level)

    # ── HISTORY ────────────────────────────────────────────────────────────────

    def _refresh_history(self):
        t = THEMES[self.theme]
        badge_cols = {
            "Weak":       (t["weak"],    "#FEE2E2" if self.theme=="light" else "#3B1515"),
            "Medium":     (t["medium"],  "#FEF3C7" if self.theme=="light" else "#3B2800"),
            "Strong":     (t["strong"],  "#D1FAE5" if self.theme=="light" else "#0D3322"),
            "Very Strong":(t["vstrong"], "#EDE9FE" if self.theme=="light" else "#1E1A3D"),
            "—":          (t["subtext"], t["hist_bg"]),
        }
        recent = list(reversed(self.history))
        for i, (row, mask, badge) in enumerate(self.hist_rows):
            if i < len(recent):
                pw, lv = recent[i]
                if len(pw) > 4:
                    m = pw[:2] + "•" * max(0, len(pw)-4) + pw[-2:]
                else:
                    m = "•" * len(pw)
                mask.configure(text=m, fg=t["hist_fg"])
                fg, bg = badge_cols.get(lv, (t["subtext"], t["hist_bg"]))
                badge.configure(text=lv, fg=fg, bg=bg)
            else:
                mask.configure(text="—", fg=t["hint"])
                badge.configure(text="", bg=t["hist_bg"])

    def _clear_history(self):
        self.history.clear()
        self._refresh_history()

    # ── CHARTS ─────────────────────────────────────────────────────────────────

    def _draw_charts(self, pw, score, checks, level):
        t  = THEMES[self.theme]
        bc = BAR_COLS_DARK if self.theme == "dark" else BAR_COLS_LIGHT
        col_map = {
            "Weak":        t["weak"],
            "Medium":      t["medium"],
            "Strong":      t["strong"],
            "Very Strong": t["vstrong"],
            "—":           t["seg_empty"],
        }
        lc   = col_map.get(level, t["seg_empty"])
        vals = bar_values(pw)
        pcts = [v * 100 for v in vals]

        self.fig.patch.set_facecolor(t["chart_bg"])

        # ── Bar chart ────────────────────────────────────────────────────────
        ax = self.ax_bar
        ax.clear()
        ax.set_facecolor(t["chart_bg"])

        y    = np.arange(len(BAR_LABELS))
        h    = 0.52

        for i, (yi, pct, col) in enumerate(zip(y, pcts, bc)):
            # track
            ax.barh(yi, 100, height=h, color=t["seg_empty"],
                    left=0, zorder=1, linewidth=0)
            # data
            if pct > 0:
                ax.barh(yi, pct, height=h, color=col,
                        left=0, zorder=2, linewidth=0)
                # rounded end-cap
                ax.plot(pct, yi, "o", color=col,
                        markersize=h * 22, zorder=3, clip_on=False)
            # left start-cap
            ax.plot(0, yi, "o", color=t["seg_empty"],
                    markersize=h * 22, zorder=2)
            if pct > 0:
                ax.plot(0, yi, "o", color=col,
                        markersize=h * 22, zorder=3)
            # percent label
            ax.text(102, yi, f"{int(pct)}%",
                    va="center", fontsize=8,
                    color=t["chart_text"],
                    fontfamily="monospace")

        ax.set_yticks(y)
        ax.set_yticklabels(BAR_LABELS, fontsize=9, color=t["chart_text"])
        ax.set_xlim(-2, 118)
        ax.set_ylim(-0.7, len(BAR_LABELS) - 0.3)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(
            ["0", "25", "50", "75", "100"],
            fontsize=7.5, color=t["chart_text"])
        ax.set_title("Criteria breakdown", fontsize=9.5,
                     fontweight="bold", color=t["chart_text"],
                     pad=7, loc="left")
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.grid(axis="x", color=t["chart_grid"],
                linewidth=0.7, linestyle="--",
                alpha=0.8, zorder=0)
        ax.set_axisbelow(True)

        # ── Gauge ────────────────────────────────────────────────────────────
        ax2 = self.ax_gauge
        ax2.clear()
        ax2.set_facecolor(t["chart_bg"])
        ax2.set_aspect("equal")
        ax2.set_xlim(-1.25, 1.25)
        ax2.set_ylim(-1.05, 1.35)
        ax2.axis("off")
        ax2.set_title("Score", fontsize=9.5, fontweight="bold",
                      color=t["chart_text"], pad=5)

        # tick notches
        for i in range(7):
            a = np.pi - (i / 6) * np.pi
            ax2.plot(
                [0.88*np.cos(a), 0.96*np.cos(a)],
                [0.88*np.sin(a), 0.96*np.sin(a)],
                color=t["chart_grid"], lw=1.5, zorder=1)

        # background arc
        th = np.linspace(np.pi, 0, 300)
        ax2.plot(np.cos(th), np.sin(th),
                 color=t["seg_empty"], lw=15,
                 solid_capstyle="round", zorder=2)

        # coloured arc
        frac = score / 6
        if frac > 0:
            th_f = np.linspace(np.pi, np.pi - frac * np.pi, 300)
            ax2.plot(np.cos(th_f), np.sin(th_f),
                     color=lc, lw=15,
                     solid_capstyle="round", zorder=3)

        # inner circle (clean face)
        ax2.add_patch(
            plt.Circle((0, 0), 0.68,
                       color=t["chart_bg"], zorder=4))

        # score number
        ax2.text(0, 0.12, str(score),
                 ha="center", va="center",
                 fontsize=32, fontweight="bold",
                 color=lc if pw else t["chart_text"],
                 zorder=5)
        ax2.text(0, -0.22, "/ 6",
                 ha="center", va="center",
                 fontsize=10, color=t["chart_text"], zorder=5)
        if pw:
            ax2.text(0, -0.52, level,
                     ha="center", va="center",
                     fontsize=9, fontweight="bold",
                     color=lc, zorder=5)

        self.mpl_canvas.draw()


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Password Strength Checker")
    root.geometry("740x860")
    root.minsize(680, 720)
    App(root)
    root.mainloop()
