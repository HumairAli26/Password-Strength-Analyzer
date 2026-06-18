"""
Password Strength Checker — Professional Edition
=================================================
• Polished card-based layout with subtle shadows via border stacking
• Gradient-style header with accent colour
• Live 4-segment pill meter
• Entropy + crack-time estimates
• 6-criteria checklist with pass/fail icons
• Password generator (length slider + charset toggles)
• Copy-to-clipboard with flash feedback
• Password history (last 5, masked, coloured badges)
• Bar chart: wide left margin so labels are always fully visible
• Semicircular score gauge
• Light / Dark theme toggle
• Smooth scrollable layout
"""

import re, math, random, string
import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# ── Colour Palettes ────────────────────────────────────────────────────────────

THEMES = {
    "light": {
        "bg":          "#EEF1F8",
        "panel":       "#FFFFFF",
        "panel2":      "#F8FAFD",
        "border":      "#DDE3F0",
        "border2":     "#C8D0E7",
        "text":        "#0F1629",
        "subtext":     "#5A6478",
        "hint":        "#9EA8BC",
        "input_bg":    "#F4F6FB",
        "input_fg":    "#0F1629",
        "accent":      "#4F46E5",
        "accent_lt":   "#6366F1",
        "accent_dim":  "#EEF2FF",
        "weak":        "#DC2626",
        "medium":      "#D97706",
        "strong":      "#059669",
        "vstrong":     "#4F46E5",
        "seg_empty":   "#E2E8F0",
        "check_ok":    "#059669",
        "check_off":   "#CBD5E1",
        "chart_bg":    "#FFFFFF",
        "chart_text":  "#374151",
        "chart_grid":  "#F1F5F9",
        "title_fg":    "#0F1629",
        "btn_fg":      "#FFFFFF",
        "hist_bg":     "#F8FAFD",
        "hist_row":    "#FFFFFF",
        "hist_fg":     "#0F1629",
        "copy_ok":     "#059669",
        "gen_bg":      "#4F46E5",
        "hdr_bg":      "#4F46E5",
        "hdr_fg":      "#FFFFFF",
        "hdr_sub":     "#C7D2FE",
        "tag_weak":    ("#DC2626", "#FEE2E2"),
        "tag_med":     ("#D97706", "#FEF3C7"),
        "tag_str":     ("#059669", "#D1FAE5"),
        "tag_vstr":    ("#4F46E5", "#EDE9FE"),
        "scroll_bg":   "#DDE3F0",
        "meter_r":     8,
    },
    "dark": {
        "bg":          "#080B14",
        "panel":       "#111525",
        "panel2":      "#161A2E",
        "border":      "#1F2540",
        "border2":     "#2A3050",
        "text":        "#EEF2FF",
        "subtext":     "#8892AA",
        "hint":        "#485068",
        "input_bg":    "#1A1F38",
        "input_fg":    "#EEF2FF",
        "accent":      "#818CF8",
        "accent_lt":   "#A5B4FC",
        "accent_dim":  "#1E2444",
        "weak":        "#F87171",
        "medium":      "#FCD34D",
        "strong":      "#34D399",
        "vstrong":     "#A78BFA",
        "seg_empty":   "#1F2540",
        "check_ok":    "#34D399",
        "check_off":   "#2A3050",
        "chart_bg":    "#111525",
        "chart_text":  "#8892AA",
        "chart_grid":  "#1A1F38",
        "title_fg":    "#EEF2FF",
        "btn_fg":      "#FFFFFF",
        "hist_bg":     "#111525",
        "hist_row":    "#161A2E",
        "hist_fg":     "#EEF2FF",
        "copy_ok":     "#34D399",
        "gen_bg":      "#6366F1",
        "hdr_bg":      "#111525",
        "hdr_fg":      "#EEF2FF",
        "hdr_sub":     "#485068",
        "tag_weak":    ("#F87171", "#3B0E0E"),
        "tag_med":     ("#FCD34D", "#3B2800"),
        "tag_str":     ("#34D399", "#0A2E1E"),
        "tag_vstr":    ("#A78BFA", "#1C1748"),
        "scroll_bg":   "#1F2540",
        "meter_r":     8,
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

# Chart bar labels + colour sets — light and dark
BAR_LABELS     = ["Length", "Uppercase", "Lowercase", "Numbers", "Symbols"]
BAR_COLS_LIGHT = ["#4F46E5", "#059669", "#0284C7", "#D97706", "#BE185D"]
BAR_COLS_DARK  = ["#818CF8", "#34D399", "#38BDF8", "#FCD34D", "#F472B6"]

# ── Password helpers ───────────────────────────────────────────────────────────

def score_password(pw):
    checks = [fn(pw) for _, _, fn in CRITERIA]
    s = sum(checks)
    if not pw:  return 0, checks, "—"
    if s <= 2:  return s, checks, "Weak"
    if s <= 4:  return s, checks, "Medium"
    if s == 5:  return s, checks, "Strong"
    return s, checks, "Very Strong"

def bar_values(pw):
    if not pw: return [0.0] * 5
    n = len(pw)
    return [
        min(1.0, n / 16),
        min(1.0, len(re.findall(r"[A-Z]", pw)) / max(1, n * 0.3)),
        min(1.0, len(re.findall(r"[a-z]", pw)) / max(1, n * 0.3)),
        min(1.0, len(re.findall(r"[0-9]", pw)) / 3),
        min(1.0, len(re.findall(r"[^A-Za-z0-9]", pw)) / 2),
    ]

def entropy_bits(pw):
    if not pw: return 0.0
    pool = 0
    if re.search(r"[a-z]", pw): pool += 26
    if re.search(r"[A-Z]", pw): pool += 26
    if re.search(r"[0-9]", pw): pool += 10
    if re.search(r"[^A-Za-z0-9]", pw): pool += 32
    return len(pw) * math.log2(pool) if pool else 0.0

def crack_time(bits):
    if bits == 0: return "—"
    s = (2 ** bits) / 1e10
    thresholds = [
        (1,         "< 1 second"),
        (60,        "{:.0f} seconds"),
        (3600,      "{:.0f} minutes",   60),
        (86400,     "{:.0f} hours",     3600),
        (2592000,   "{:.0f} days",      86400),
        (31536000,  "{:.0f} months",    2592000),
        (3.156e9,   "{:.0f} years",     31536000),
        (3.156e12,  "{:.0f}K years",    3.156e9),
        (3.156e15,  "{:.0f}M years",    3.156e12),
    ]
    for row in thresholds:
        limit = row[0]
        if s < limit:
            fmt = row[1]
            if "{" not in fmt:
                return fmt
            div = row[2]
            return fmt.format(s / div)
    return "Centuries+"

def gen_pw(length=16, upper=True, digits=True, symbols=True):
    pool = list(string.ascii_lowercase)
    must = [random.choice(string.ascii_lowercase)]
    if upper:
        pool += list(string.ascii_uppercase)
        must.append(random.choice(string.ascii_uppercase))
    if digits:
        pool += list(string.digits)
        must.append(random.choice(string.digits))
    if symbols:
        sym = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        pool += list(sym)
        must.append(random.choice(sym))
    rest = [random.choice(pool) for _ in range(length - len(must))]
    pw = must + rest
    random.shuffle(pw)
    return "".join(pw)

# ── Main App ───────────────────────────────────────────────────────────────────

class App:
    def __init__(self, root):
        self.root    = root
        self.theme   = "light"
        self.show_pw = False
        self.history = []
        self._cpjob  = None
        self._cbs    = []
        self._sec_labels = []
        self._sec_seps   = []

        self._build()
        self._apply_theme()
        self.root.after(150, lambda: self._update("", 0, [False]*6, "—"))

    # ── BUILD ──────────────────────────────────────────────────────────────────

    def _build(self):
        PX = 22   # horizontal card padding from window edge

        # ── Header ──────────────────────────────────────────────────────────
        self.hdr = tk.Frame(self.root, height=70)
        self.hdr.pack(fill="x")
        self.hdr.pack_propagate(False)

        # left side: icon + title stack
        hdr_l = tk.Frame(self.hdr)
        hdr_l.pack(side="left", padx=22, fill="y")
        self.hdr_l = hdr_l

        self.hdr_icon = tk.Label(hdr_l, text="🔐",
                                  font=("Segoe UI Emoji", 22))
        self.hdr_icon.pack(side="left", padx=(0, 12))

        hdr_txt = tk.Frame(hdr_l)
        hdr_txt.pack(side="left", fill="y")
        self.hdr_txt = hdr_txt

        self.hdr_title = tk.Label(hdr_txt, text="Password Strength Checker",
                                   font=("Segoe UI", 15, "bold"), anchor="w")
        self.hdr_title.pack(anchor="w", pady=(14, 0))

        self.hdr_sub = tk.Label(hdr_txt, text="Analyse · Generate · Stay Secure",
                                 font=("Segoe UI", 9), anchor="w")
        self.hdr_sub.pack(anchor="w")

        # right: theme pill button
        self.theme_btn = tk.Button(self.hdr, text="🌙  Dark Mode",
            relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10), padx=16, pady=7,
            command=self._toggle_theme)
        self.theme_btn.pack(side="right", padx=22, pady=16)

        # thin accent stripe under header
        self.hdr_stripe = tk.Frame(self.root, height=3)
        self.hdr_stripe.pack(fill="x")

        # ── Scroll setup ─────────────────────────────────────────────────────
        self.vscroll = tk.Scrollbar(self.root, orient="vertical", width=10)
        self.vscroll.pack(side="right", fill="y")

        self.canvas = tk.Canvas(self.root, bd=0, highlightthickness=0,
                                yscrollcommand=self.vscroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.vscroll.config(command=self.canvas.yview)

        self.main = tk.Frame(self.canvas)
        self._wid = self.canvas.create_window((0, 0), window=self.main,
                                               anchor="nw")

        self.main.bind("<Configure>",
            lambda e: self.canvas.config(
                scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
            lambda e: self.canvas.itemconfig(self._wid, width=e.width))
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(
                int(-1 * (e.delta / 120)), "units"))

        # ── Section 1 — Password ─────────────────────────────────────────────
        self._sec_hdr(self.main, "🔑  PASSWORD", PX, top=20)

        self.input_card = self._card(self.main)
        self.input_card.pack(fill="x", padx=PX, pady=(0, 0))

        # label row: "Enter password" left, bits right
        top_row = tk.Frame(self.input_card)
        top_row.pack(fill="x", padx=20, pady=(18, 8))
        self.pw_label = tk.Label(top_row, text="Enter your password",
                                  font=("Segoe UI", 10), anchor="w")
        self.pw_label.pack(side="left")
        self.entropy_lbl = tk.Label(top_row, text="",
                                     font=("Segoe UI", 9, "bold"), anchor="e")
        self.entropy_lbl.pack(side="right")

        # input field with embedded buttons
        self.inp_wrap = tk.Frame(self.input_card, height=52)
        self.inp_wrap.pack(fill="x", padx=20)
        self.inp_wrap.pack_propagate(False)

        self.inp_inner = tk.Frame(self.inp_wrap)
        self.inp_inner.pack(fill="both", expand=True)

        self.pw_var = tk.StringVar()
        self.pw_var.trace_add("write", self._on_change)

        self.pw_entry = tk.Entry(self.inp_inner, textvariable=self.pw_var,
            show="•", font=("Consolas", 14),
            relief="flat", bd=0, highlightthickness=0)
        self.pw_entry.pack(side="left", fill="both", expand=True,
                           padx=(16, 0), pady=14)

        self.copy_btn = tk.Button(self.inp_inner, text=" ⎘ Copy ",
            relief="flat", cursor="hand2", bd=0, highlightthickness=0,
            font=("Segoe UI", 9, "bold"), padx=6, pady=5,
            command=self._copy)
        self.copy_btn.pack(side="right", padx=(0, 8))

        self.eye_btn = tk.Button(self.inp_inner, text="👁",
            relief="flat", cursor="hand2", bd=0, highlightthickness=0,
            font=("Segoe UI Emoji", 13), command=self._toggle_vis)
        self.eye_btn.pack(side="right", padx=4)

        # strength meter: 4 pill segments
        self.meter_wrap = tk.Frame(self.input_card, height=10)
        self.meter_wrap.pack(fill="x", padx=20, pady=(10, 0))
        self.meter_wrap.pack_propagate(False)
        self.segs = []
        for i in range(4):
            c = tk.Canvas(self.meter_wrap, height=10, bd=0,
                          highlightthickness=0)
            c.pack(side="left", fill="x", expand=True,
                   padx=(0, 6 if i < 3 else 0))
            self.segs.append(c)

        # strength + crack time row
        mid_row = tk.Frame(self.input_card)
        mid_row.pack(fill="x", padx=20, pady=(12, 0))

        self.str_lbl = tk.Label(mid_row, text="Enter a password to begin",
            font=("Segoe UI", 12, "bold"), anchor="w")
        self.str_lbl.pack(side="left")

        crack_f = tk.Frame(mid_row)
        crack_f.pack(side="right")
        self.crack_icon_lbl = tk.Label(crack_f, text="⏱",
                                        font=("Segoe UI Emoji", 11))
        self.crack_icon_lbl.pack(side="left")
        self.crack_lbl = tk.Label(crack_f, text="",
                                   font=("Segoe UI", 9))
        self.crack_lbl.pack(side="left", padx=(4, 0))
        self.crack_row = crack_f
        self.mid_row   = mid_row

        tk.Frame(self.input_card, height=18).pack()   # bottom padding

        # ── Section 2 — Generator ────────────────────────────────────────────
        self._sec_hdr(self.main, "⚡  GENERATOR", PX, top=18)

        self.gen_card = self._card(self.main)
        self.gen_card.pack(fill="x", padx=PX, pady=(0, 0))

        gen_hdr_row = tk.Frame(self.gen_card)
        gen_hdr_row.pack(fill="x", padx=20, pady=(18, 10))

        self.gen_title = tk.Label(gen_hdr_row,
            text="Create a strong password automatically",
            font=("Segoe UI", 10), anchor="w")
        self.gen_title.pack(side="left")

        self.gen_btn = tk.Button(gen_hdr_row, text="  Generate ›  ",
            relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 10, "bold"), padx=14, pady=7,
            command=self._generate)
        self.gen_btn.pack(side="right")

        # length row
        len_row = tk.Frame(self.gen_card)
        len_row.pack(fill="x", padx=20, pady=(0, 6))
        self.gen_card_len_row = len_row

        self.len_title = tk.Label(len_row, text="Length:",
                                   font=("Segoe UI", 10))
        self.len_title.pack(side="left")

        self.gen_len = tk.IntVar(value=16)
        self.len_val = tk.Label(len_row, text="16",
                                 font=("Segoe UI", 10, "bold"), width=3)
        self.len_val.pack(side="left", padx=(6, 0))

        self.len_slider = tk.Scale(len_row, from_=8, to=32,
            orient="horizontal", variable=self.gen_len,
            showvalue=False, length=180, bd=0,
            highlightthickness=0, relief="flat",
            command=lambda v: self.len_val.config(text=v))
        self.len_slider.pack(side="left", padx=(8, 24))

        # checkboxes row
        cb_row = tk.Frame(self.gen_card)
        cb_row.pack(fill="x", padx=20, pady=(0, 18))
        self.cb_row = cb_row

        self.use_upper   = tk.BooleanVar(value=True)
        self.use_digits  = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        for var, label in [(self.use_upper,   "Uppercase  A–Z"),
                           (self.use_digits,  "Numbers  0–9"),
                           (self.use_symbols, "Symbols  !@#")]:
            cb = tk.Checkbutton(cb_row, text=label, variable=var,
                font=("Segoe UI", 10), relief="flat", bd=0,
                cursor="hand2", highlightthickness=0)
            cb.pack(side="left", padx=(0, 20))
            self._cbs.append(cb)

        # ── Section 3 — Requirements ─────────────────────────────────────────
        self._sec_hdr(self.main, "✅  REQUIREMENTS", PX, top=18)

        self.crit_card = self._card(self.main)
        self.crit_card.pack(fill="x", padx=PX, pady=(0, 0))

        self.crit_grid = tk.Frame(self.crit_card)
        self.crit_grid.pack(fill="x", padx=20, pady=(16, 16))
        self.crit_grid.columnconfigure(0, weight=1)
        self.crit_grid.columnconfigure(1, weight=1)

        self.c_frames = []
        self.c_icons  = []
        self.c_checks = []
        self.c_texts  = []

        for i, (label, icon, _) in enumerate(CRITERIA):
            r, c = divmod(i, 2)
            # each criterion is its own small card row
            cf = tk.Frame(self.crit_grid, height=38)
            cf.grid(row=r, column=c, sticky="ew", pady=4,
                    padx=(0, 8 if c == 0 else 0))
            cf.pack_propagate(False)

            inner = tk.Frame(cf)
            inner.pack(fill="both", expand=True, padx=8)

            ic = tk.Label(inner, text=icon,
                          font=("Segoe UI Emoji", 13), width=2)
            ic.pack(side="left")
            ck = tk.Label(inner, text="○",
                          font=("Segoe UI", 13, "bold"), width=2)
            ck.pack(side="left", padx=(2, 0))
            tx = tk.Label(inner, text=label,
                          font=("Segoe UI", 10))
            tx.pack(side="left", padx=(2, 0))

            self.c_frames.append((cf, inner))
            self.c_icons.append(ic)
            self.c_checks.append(ck)
            self.c_texts.append(tx)

        # ── Section 4 — Analysis ─────────────────────────────────────────────
        self._sec_hdr(self.main, "📊  ANALYSIS", PX, top=18)

        self.chart_card = self._card(self.main)
        self.chart_card.pack(fill="x", padx=PX, pady=(0, 0))

        # ------------------------------------------------------------------ #
        #  CHART GEOMETRY — key fix for readable bar labels:
        #  left=0.22 gives plenty of room for the 9-character labels like
        #  "Uppercase" and "Lowercase" without any clipping.
        # ------------------------------------------------------------------ #
        self.fig = plt.figure(figsize=(7.4, 3.0))
        gs = self.fig.add_gridspec(
            1, 2,
            width_ratios=[1.8, 1],
            left=0.22,    # ← wide left margin = labels always visible
            right=0.97,
            top=0.82,
            bottom=0.14,
            wspace=0.30,
        )
        self.ax_bar   = self.fig.add_subplot(gs[0])
        self.ax_gauge = self.fig.add_subplot(gs[1])

        self.mpl_canvas = FigureCanvasTkAgg(self.fig, master=self.chart_card)
        self.mpl_canvas.get_tk_widget().pack(
            fill="x", padx=14, pady=(12, 14))

        # ── Section 5 — History ──────────────────────────────────────────────
        self._sec_hdr(self.main, "🕘  RECENT HISTORY", PX, top=18)

        self.hist_card = self._card(self.main)
        self.hist_card.pack(fill="x", padx=PX, pady=(0, 0))

        hist_top = tk.Frame(self.hist_card)
        hist_top.pack(fill="x", padx=20, pady=(16, 8))
        self.hist_hdr_frame = hist_top

        self.hist_title = tk.Label(hist_top, text="Last 5 passwords checked",
                                    font=("Segoe UI", 10), anchor="w")
        self.hist_title.pack(side="left")

        self.clear_btn = tk.Button(hist_top, text="Clear All",
            relief="flat", cursor="hand2", bd=0,
            font=("Segoe UI", 9), padx=10, pady=4,
            command=self._clear_hist)
        self.clear_btn.pack(side="right")

        self.hist_inner = tk.Frame(self.hist_card)
        self.hist_inner.pack(fill="x", padx=20, pady=(0, 16))

        self.hist_rows = []
        for idx in range(5):
            row = tk.Frame(self.hist_inner, height=38)
            row.pack(fill="x", pady=(0, 4))
            row.pack_propagate(False)

            inner = tk.Frame(row)
            inner.pack(fill="both", expand=True, padx=2)

            num_lbl = tk.Label(inner, text=f"#{idx+1}",
                               font=("Segoe UI", 9, "bold"), width=3,
                               anchor="center")
            num_lbl.pack(side="left", padx=(10, 8), pady=8)

            divider = tk.Frame(inner, width=1)
            divider.pack(side="left", fill="y", pady=6)

            pw_lbl = tk.Label(inner, text="—",
                              font=("Consolas", 10), anchor="w")
            pw_lbl.pack(side="left", fill="both", expand=True,
                        padx=(10, 8), pady=8)

            badge = tk.Label(inner, text="",
                             font=("Segoe UI", 8, "bold"),
                             padx=10, pady=3)
            badge.pack(side="right", padx=(0, 10), pady=9)

            self.hist_rows.append((row, inner, num_lbl, divider,
                                   pw_lbl, badge))

        tk.Frame(self.main, height=32).pack()

        self._draw_charts("", 0, [False]*6, "—")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _card(self, parent):
        """Card with a subtle outer shadow effect via stacked frames."""
        shadow = tk.Frame(parent, bd=0, highlightthickness=1)
        inner  = tk.Frame(shadow, bd=0, highlightthickness=1)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        # pack is done by caller on shadow
        shadow._inner = inner   # expose inner for packing children
        return shadow

    def _sec_hdr(self, parent, text, px, top=14):
        """Section heading with a horizontal rule."""
        f = tk.Frame(parent)
        f.pack(fill="x", padx=px, pady=(top, 6))
        lbl = tk.Label(f, text=text,
                       font=("Segoe UI", 8, "bold"), anchor="w")
        lbl.pack(side="left")
        sep = tk.Frame(f, height=1)
        sep.pack(side="left", fill="x", expand=True, padx=(10, 0), pady=5)
        self._sec_labels.append(lbl)
        self._sec_seps.append(sep)

    # Override pack on _card shadows so children go into inner
    def _pack_into(self, card, widget, **kw):
        widget.pack(in_=card._inner, **kw)

    # ── THEME ──────────────────────────────────────────────────────────────────

    def _toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self._apply_theme()
        pw = self.pw_var.get()
        sc, ch, lv = score_password(pw)
        self._update(pw, sc, ch, lv)

    def _apply_theme(self):
        t    = THEMES[self.theme]
        dark = self.theme == "dark"

        self.root.configure(bg=t["bg"])
        self.canvas.configure(bg=t["bg"])
        self.main.configure(bg=t["bg"])
        self.vscroll.configure(bg=t["scroll_bg"],
                                troughcolor=t["bg"],
                                activebackground=t["accent"])

        # header
        for w in (self.hdr, self.hdr_l, self.hdr_txt):
            w.configure(bg=t["hdr_bg"])
        self.hdr_icon.configure(bg=t["hdr_bg"], fg=t["hdr_fg"])
        self.hdr_title.configure(bg=t["hdr_bg"], fg=t["hdr_fg"])
        self.hdr_sub.configure(bg=t["hdr_bg"], fg=t["hdr_sub"])
        self.hdr_stripe.configure(bg=t["accent"])
        self.theme_btn.configure(
            bg="#FFFFFF" if dark else "#3730A3",
            fg="#111827" if dark else "#FFFFFF",
            activebackground="#F1F5F9" if dark else "#312E81",
            activeforeground="#111827" if dark else "#FFFFFF",
            text="☀  Light Mode" if dark else "🌙  Dark Mode")

        # section headers
        for lbl in self._sec_labels:
            lbl.configure(bg=t["bg"], fg=t["subtext"])
        for sep in self._sec_seps:
            sep.configure(bg=t["border"])
        # background frames
        for w in self.main.winfo_children():
            if isinstance(w, tk.Frame) and w not in (
                    self.input_card, self.gen_card, self.crit_card,
                    self.chart_card, self.hist_card):
                w.configure(bg=t["bg"])

        # ── input card ──
        self.input_card.configure(
            bg=t["panel"], highlightbackground=t["border2"])
        self.input_card._inner.configure(
            bg=t["panel"], highlightbackground=t["border"])
        for w in self._iter_children(self.input_card):
            if isinstance(w, tk.Frame):
                w.configure(bg=t["panel"])
        self.pw_label.configure(bg=t["panel"], fg=t["subtext"])
        self.entropy_lbl.configure(bg=t["panel"], fg=t["accent"])
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
            bg=t["accent"], fg=t["btn_fg"],
            activebackground=t["accent_lt"],
            activeforeground=t["btn_fg"])
        self.meter_wrap.configure(bg=t["panel"])
        for c in self.segs:
            c.configure(bg=t["panel"])
        self.str_lbl.configure(bg=t["panel"], fg=t["subtext"])
        self.mid_row.configure(bg=t["panel"])
        self.crack_row.configure(bg=t["panel"])
        self.crack_icon_lbl.configure(bg=t["panel"], fg=t["subtext"])
        self.crack_lbl.configure(bg=t["panel"], fg=t["subtext"])

        # ── generator card ──
        self.gen_card.configure(
            bg=t["panel"], highlightbackground=t["border2"])
        self.gen_card._inner.configure(
            bg=t["panel"], highlightbackground=t["border"])
        for w in self._iter_children(self.gen_card):
            if isinstance(w, tk.Frame):
                w.configure(bg=t["panel"])
        self.gen_title.configure(bg=t["panel"], fg=t["subtext"])
        self.gen_btn.configure(
            bg=t["gen_bg"], fg=t["btn_fg"],
            activebackground=t["accent_lt"],
            activeforeground=t["btn_fg"])
        self.len_title.configure(bg=t["panel"], fg=t["subtext"])
        self.len_val.configure(bg=t["panel"], fg=t["accent"])
        self.len_slider.configure(
            bg=t["panel"], fg=t["text"],
            troughcolor=t["seg_empty"],
            activebackground=t["accent"])
        self.gen_card_len_row.configure(bg=t["panel"])
        self.cb_row.configure(bg=t["panel"])
        for cb in self._cbs:
            cb.configure(
                bg=t["panel"], fg=t["text"],
                selectcolor=t["accent_dim"],
                activebackground=t["panel"],
                activeforeground=t["accent"])

        # ── criteria card ──
        self.crit_card.configure(
            bg=t["panel"], highlightbackground=t["border2"])
        self.crit_card._inner.configure(
            bg=t["panel"], highlightbackground=t["border"])
        self.crit_grid.configure(bg=t["panel"])
        for (cf, inner), ic, ck, tx in zip(
                self.c_frames, self.c_icons, self.c_checks, self.c_texts):
            cf.configure(bg=t["panel2"],
                         highlightbackground=t["border"],
                         highlightthickness=1)
            inner.configure(bg=t["panel2"])
            ic.configure(bg=t["panel2"])
            ck.configure(bg=t["panel2"], fg=t["check_off"])
            tx.configure(bg=t["panel2"], fg=t["subtext"])

        # ── chart card ──
        self.chart_card.configure(
            bg=t["panel"], highlightbackground=t["border2"])
        self.chart_card._inner.configure(
            bg=t["panel"], highlightbackground=t["border"])

        # ── history card ──
        self.hist_card.configure(
            bg=t["panel"], highlightbackground=t["border2"])
        self.hist_card._inner.configure(
            bg=t["panel"], highlightbackground=t["border"])
        self.hist_hdr_frame.configure(bg=t["panel"])
        self.hist_title.configure(bg=t["panel"], fg=t["subtext"])
        self.clear_btn.configure(
            bg=t["panel"], fg=t["subtext"],
            activebackground=t["panel"])
        self.hist_inner.configure(bg=t["panel"])
        for row, inner, num_lbl, div, pw_lbl, badge in self.hist_rows:
            row.configure(bg=t["hist_row"],
                          highlightbackground=t["border"],
                          highlightthickness=1)
            inner.configure(bg=t["hist_row"])
            num_lbl.configure(bg=t["hist_row"], fg=t["accent"])
            div.configure(bg=t["border"])
            pw_lbl.configure(bg=t["hist_row"], fg=t["hist_fg"])
            badge.configure(bg=t["hist_row"])

        self._refresh_hist()

    def _iter_children(self, widget):
        """Flat iteration over all descendants."""
        result = []
        for child in widget.winfo_children():
            result.append(child)
            result.extend(self._iter_children(child))
        return result

    # ── LOGIC ──────────────────────────────────────────────────────────────────

    def _on_change(self, *_):
        pw = self.pw_var.get()
        sc, ch, lv = score_password(pw)
        self._update(pw, sc, ch, lv)

    def _toggle_vis(self):
        self.show_pw = not self.show_pw
        self.pw_entry.config(show="" if self.show_pw else "•")
        self.eye_btn.config(text="🙈" if self.show_pw else "👁")

    def _copy(self):
        pw = self.pw_var.get()
        if not pw:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        t = THEMES[self.theme]
        self.copy_btn.configure(text=" ✓ Copied! ", bg=t["copy_ok"])
        if self._cpjob:
            self.root.after_cancel(self._cpjob)
        self._cpjob = self.root.after(
            1800,
            lambda: self.copy_btn.configure(
                text=" ⎘ Copy ", bg=t["accent"]))

    def _generate(self):
        pw = gen_pw(
            self.gen_len.get(),
            self.use_upper.get(),
            self.use_digits.get(),
            self.use_symbols.get())
        self.pw_var.set(pw)
        self.pw_entry.icursor("end")

    def _update(self, pw, score, checks, level):
        t = THEMES[self.theme]
        cmap = {
            "Weak":        t["weak"],
            "Medium":      t["medium"],
            "Strong":      t["strong"],
            "Very Strong": t["vstrong"],
            "—":           t["subtext"],
        }
        lc = cmap.get(level, t["subtext"])

        # pill meter segments
        n_lit = {"—":0,"Weak":1,"Medium":2,
                 "Strong":3,"Very Strong":4}.get(level if pw else "—", 0)
        for i, c in enumerate(self.segs):
            fill = lc if i < n_lit else t["seg_empty"]
            c.delete("all")
            W = c.winfo_width() or 160
            H = 10
            r = H // 2
            # draw rounded pill
            c.create_arc(0, 0, 2*r, H, start=90, extent=180,
                         fill=fill, outline="")
            c.create_arc(W-2*r, 0, W, H, start=-90, extent=180,
                         fill=fill, outline="")
            c.create_rectangle(r, 0, W-r, H, fill=fill, outline="")

        # strength label
        ico = {"Weak":"⚠  ","Medium":"◑  ","Strong":"✓  ","Very Strong":"✓✓ "}
        self.str_lbl.configure(
            text=(ico.get(level,"") + level) if pw else "Enter a password to begin",
            fg=lc if pw else t["subtext"])

        # entropy badge
        bits = entropy_bits(pw)
        self.entropy_lbl.configure(
            text=f"~{bits:.0f} bits  " if pw else "")

        # crack time
        ct = crack_time(bits)
        self.crack_lbl.configure(
            text=f"  Estimated crack time: {ct}" if pw else "",
            fg=lc if pw else t["subtext"])
        self.crack_icon_lbl.configure(
            fg=lc if pw else t["subtext"])

        # criteria rows
        for met, (cf, inner), ic, ck, tx in zip(
                checks, self.c_frames, self.c_icons,
                self.c_checks, self.c_texts):
            bg = t["panel2"]
            ck.configure(
                text="✓" if met else "○",
                fg=t["check_ok"] if met else t["check_off"])
            tx.configure(
                fg=t["text"] if met else t["subtext"])
            if met:
                cf.configure(highlightbackground=t["check_ok"])
            else:
                cf.configure(highlightbackground=t["border"])

        # history
        if pw and (not self.history or self.history[-1][0] != pw):
            self.history.append((pw, level))
            if len(self.history) > 5:
                self.history = self.history[-5:]
            self._refresh_hist()

        self._draw_charts(pw, score, checks, level)

    # ── HISTORY ────────────────────────────────────────────────────────────────

    def _refresh_hist(self):
        t    = THEMES[self.theme]
        tags = {
            "Weak":        t["tag_weak"],
            "Medium":      t["tag_med"],
            "Strong":      t["tag_str"],
            "Very Strong": t["tag_vstr"],
        }
        recent = list(reversed(self.history))
        for i, (row, inner, num_lbl, div, pw_lbl, badge) in enumerate(
                self.hist_rows):
            bg = t["hist_row"]
            row.configure(bg=bg, highlightbackground=t["border"])
            inner.configure(bg=bg)
            num_lbl.configure(bg=bg, fg=t["accent"])
            div.configure(bg=t["border"])
            pw_lbl.configure(bg=bg)
            badge.configure(bg=bg)

            if i < len(recent):
                pw, lv = recent[i]
                masked = (pw[:2] + "•" * max(0, len(pw)-4) + pw[-2:]
                          if len(pw) > 4 else "•" * len(pw))
                pw_lbl.configure(text=masked, fg=t["hist_fg"])
                fg, bbg = tags.get(lv, (t["subtext"], bg))
                badge.configure(text=lv, fg=fg, bg=bbg)
            else:
                pw_lbl.configure(text="—", fg=t["hint"])
                badge.configure(text="")

    def _clear_hist(self):
        self.history.clear()
        self._refresh_hist()

    # ── CHARTS ─────────────────────────────────────────────────────────────────

    def _draw_charts(self, pw, score, checks, level):
        t  = THEMES[self.theme]
        bc = BAR_COLS_DARK if self.theme == "dark" else BAR_COLS_LIGHT
        cmap = {
            "Weak":        t["weak"],
            "Medium":      t["medium"],
            "Strong":      t["strong"],
            "Very Strong": t["vstrong"],
            "—":           t["seg_empty"],
        }
        lc   = cmap.get(level, t["seg_empty"])
        vals = bar_values(pw)
        pcts = [v * 100 for v in vals]

        self.fig.patch.set_facecolor(t["chart_bg"])

        # ── Bar chart ────────────────────────────────────────────────────────
        ax = self.ax_bar
        ax.clear()
        ax.set_facecolor(t["chart_bg"])

        n = len(BAR_LABELS)
        y = np.arange(n)
        h = 0.48

        for i, (yi, pct, col) in enumerate(zip(y, pcts, bc)):
            # track
            ax.barh(yi, 100, height=h, color=t["seg_empty"],
                    left=0, zorder=1, linewidth=0)
            if pct > 0:
                # fill
                ax.barh(yi, pct, height=h, color=col,
                        left=0, zorder=2, linewidth=0)
                # right cap
                ax.plot(pct, yi, "o", color=col,
                        markersize=h * 24, zorder=3, clip_on=False)
            # left cap
            ax.plot(0, yi, "o", color=t["seg_empty"],
                    markersize=h * 24, zorder=2)
            if pct > 0:
                ax.plot(0, yi, "o", color=col,
                        markersize=h * 24, zorder=3)
            # percent label
            ax.text(102, yi, f"{int(pct)}%",
                    va="center", fontsize=8.5, fontweight="bold",
                    color=t["chart_text"], fontfamily="monospace")

        # ── Y-axis: large, bold, well-padded labels ──────────────────────────
        ax.set_yticks(y)
        ax.set_yticklabels(
            BAR_LABELS,
            fontsize=10,        # large enough to read easily
            fontweight="bold",
            color=t["chart_text"],
        )
        # pad=8 pushes labels away from the bars so they never overlap
        ax.tick_params(axis="y", pad=8, length=0)

        ax.set_xlim(-1, 120)
        ax.set_ylim(-0.65, n - 0.35)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xticklabels(["0", "25%", "50%", "75%", "100%"],
                            fontsize=8, color=t["chart_text"])
        ax.tick_params(axis="x", length=0)
        ax.set_title("Criteria Breakdown", fontsize=10, fontweight="bold",
                     color=t["chart_text"], pad=8, loc="left")
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.grid(axis="x", color=t["chart_grid"], linewidth=0.8,
                linestyle="--", alpha=0.9, zorder=0)
        ax.set_axisbelow(True)

        # ── Gauge ────────────────────────────────────────────────────────────
        ax2 = self.ax_gauge
        ax2.clear()
        ax2.set_facecolor(t["chart_bg"])
        ax2.set_aspect("equal")
        ax2.set_xlim(-1.3, 1.3)
        ax2.set_ylim(-1.15, 1.45)
        ax2.axis("off")
        ax2.set_title("Strength Score", fontsize=10, fontweight="bold",
                      color=t["chart_text"], pad=5)

        # notch ticks at each score boundary
        for i in range(7):
            a = np.pi - (i / 6) * np.pi
            ax2.plot([0.85*np.cos(a), 0.97*np.cos(a)],
                     [0.85*np.sin(a), 0.97*np.sin(a)],
                     color=t["chart_grid"], lw=2.0, zorder=1)

        # background arc
        th = np.linspace(np.pi, 0, 300)
        ax2.plot(np.cos(th), np.sin(th),
                 color=t["seg_empty"], lw=18,
                 solid_capstyle="round", zorder=2)

        # coloured score arc
        if score > 0:
            frac = score / 6
            th_f = np.linspace(np.pi, np.pi - frac * np.pi, 300)
            ax2.plot(np.cos(th_f), np.sin(th_f),
                     color=lc, lw=18,
                     solid_capstyle="round", zorder=3)

        # face circle
        ax2.add_patch(
            plt.Circle((0, 0), 0.71, color=t["chart_bg"], zorder=4))

        # centre text
        ax2.text(0, 0.15, str(score),
                 ha="center", va="center", fontsize=36, fontweight="bold",
                 color=lc if pw else t["chart_text"], zorder=5)
        ax2.text(0, -0.22, "out of 6",
                 ha="center", va="center", fontsize=9,
                 color=t["chart_text"], zorder=5)
        if pw:
            ax2.text(0, -0.56, level,
                     ha="center", va="center", fontsize=9,
                     fontweight="bold", color=lc, zorder=5)

        self.mpl_canvas.draw()


# ── Entry ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Password Strength Checker")
    root.geometry("800x920")
    root.minsize(720, 760)
    App(root)
    root.mainloop()