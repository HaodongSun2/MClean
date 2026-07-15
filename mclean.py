"""
MClean v2.2 — Classic Win9x Retro  |  Haodong Sun
"""
import os, sys, subprocess, threading, tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
import platform, winreg, json, re

# ── Palette ─────────────────────────────────────────
C_FACE = "#D4D0C8"; C_HIGHLIGHT = "#FFFFFF"; C_SHADOW = "#808080"
C_DARKSHADOW = "#404040"; C_WINDOW = "#FFFFFF"; C_WINDOWTEXT = "#000000"
C_ACTIVECAP = "#0A246A"; C_CAPTEXT = "#FFFFFF"; C_LARGE_WARN = "#FFE0E0"
_FONT_SYS = ("Microsoft YaHei UI", 9); _FONT_FIXED = ("Consolas", 9)

# ════════════════════════════════════════════════════
#  i18n  strings
# ════════════════════════════════════════════════════
STRINGS = {
    "en": {
        "title":         "MClean",
        "subtitle":      "Software Uninstall Tool",
        "menu_file":     "  File  ",    "menu_view": "  View  ",    "menu_help": "  Help  ",
        "about_title":   "About MClean",
        "about_text":    "MClean v2.2\nClassic Windows Style\n\n"
                         "Analyze system · Identify bloatware\n"
                         "Invoke native Windows uninstall.\n\n"
                         "Producer  Haodong Sun",
        "btn_refresh":   "  Refresh  ", "btn_uninst": "  Uninstall  ",
        "btn_lang":      "EN",
        "find_label":    "Find: ",
        "group_sys":     " System ",    "group_sum": " Summary ",
        "group_sw":      " Installed Software ",
        "col_name":      "Software Name", "col_ver": "Version",
        "col_pub":       "Publisher",     "col_size":"Size", "col_arch":"Arch",
        "status_ready":  " Ready",
        "scanning":      "Scanning installed software...",
        "pg_idle":       "Idle",          "pg_init": "Initializing...",
        "pg_reg":        "Scanning registry...", "pg_render": "Rendering...",
        "done":          "Done — {n} programs found",
        "no_cmd":        "No uninstall command for:\n{name}",
        "confirm_title": "MClean — Confirm",
        "confirm":       "Uninstall this program?\n\n  {name}\n\nCommand:\n  {cmd}",
        "launched":      "Launched:\n{name}",
        "failed":        "Failed: {e}",
        "sel_first":     "Select a program first.",
        "warn_large":    "  !  {n} large program(s) ({gb:.1f} GB)",
        "items":         "{n} items  ",
        "stat_listed":   "  Listed:        ",
        "stat_sized":    "  Size recorded: ",
        "stat_large":    "  Large (>=1 GB): ",
        "stat_total":    "  Total:         ",
        "producer":      "Haodong Sun",
        "os":  "OS",  "arch_l": "Architecture", "cpu": "CPU", "host": "Host",
        "drv": "Drive {d}:",
        "drv_free": "{free:.1f} GB free / {total:.1f} GB",
    },
    "zh": {
        "title":         "MClean",
        "subtitle":      "软件卸载工具",
        "menu_file":     "  文件  ",    "menu_view": "  视图  ",    "menu_help": "  帮助  ",
        "about_title":   "关于 MClean",
        "about_text":    "MClean v2.2\n经典 Windows 复古风格\n\n"
                         "系统分析 · 大体积识别\n"
                         "调用 Windows 原生卸载\n\n"
                         "制作人  Haodong Sun",
        "btn_refresh":   "  刷新列表  ", "btn_uninst": "  卸载选中  ",
        "btn_lang":      "中",
        "find_label":    "搜索: ",
        "group_sys":     " 系统信息 ",   "group_sum": " 统计信息 ",
        "group_sw":      " 已安装软件 ",
        "col_name":      "软件名称",     "col_ver": "版本",
        "col_pub":       "发行商",       "col_size":"大小", "col_arch":"架构",
        "status_ready":  " 就绪",
        "scanning":      "正在扫描已安装软件...",
        "pg_idle":       "空闲",         "pg_init": "初始化中...",
        "pg_reg":        "扫描注册表中...", "pg_render": "渲染列表中...",
        "done":          "完成 — 共 {n} 款软件",
        "no_cmd":        "未提供卸载命令：\n{name}",
        "confirm_title": "MClean — 确认卸载",
        "confirm":       "确定要卸载以下软件吗？\n\n  {name}\n\n卸载命令：\n  {cmd}",
        "launched":      "已启动卸载程序：\n{name}",
        "failed":        "卸载失败：{e}",
        "sel_first":     "请先在列表中选择一款软件。",
        "warn_large":    "  ！检测到 {n} 款大体积软件（{gb:.1f} GB）",
        "items":         "共 {n} 项  ",
        "stat_listed":   "  已列出：        ",
        "stat_sized":    "  有体积记录：    ",
        "stat_large":    "  大体积(≥1 GB)： ",
        "stat_total":    "  合计体积：      ",
        "producer":      "制作人  Haodong Sun",
        "os":  "系统",   "arch_l": "架构",  "cpu": "处理器", "host": "主机名",
        "drv":  "磁盘 {d}:",
        "drv_free": "空闲 {free:.1f} GB / 共 {total:.1f} GB",
    },
}

# ════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════

def _get_windows_version():
    ver = sys.getwindowsversion()
    m10 = {10240:"1507",10586:"1511",14393:"1607",15063:"1703",16299:"1709",
           17134:"1803",17763:"1809",18362:"1903",18363:"1909",19041:"2004",
           19042:"20H2",19043:"21H1",19044:"21H2",19045:"22H2"}
    m11 = {22000:"21H2",22621:"22H2",22631:"23H2",
           26100:"24H2",26120:"24H2",26200:"24H2"}
    win_name = "Windows 11" if ver.build >= 22000 else f"Windows {ver.major}"
    r = m11.get(ver.build) if ver.build >= 22000 else m10.get(ver.build)
    if not r: r = f"Build {ver.build}"
    e = {2:"Home",48:"Pro",125:"Education",4:"Enterprise",101:"Home Single Language"}
    edition = e.get(ver.product_type,'')
    return f"{win_name} {r} ({edition})" if edition else f"{win_name} {r}"


def get_system_info(tr):
    info = {tr("os"): _get_windows_version(), tr("arch_l"): platform.architecture()[0],
            tr("cpu"): platform.processor() or "Unknown", tr("host"): platform.node()}
    for d in "CDEFGHIJ":
        p = Path(f"{d}:\\")
        if p.exists():
            try:
                s = os.statvfs(str(p)); total = s.f_frsize*s.f_blocks
                free = s.f_frsize*s.f_bavail
                info[tr("drv",d=d)] = tr("drv_free", free=free/(1024**3), total=total/(1024**3))
            except Exception: pass
    return info

SIZE_KEYS = ["EstimatedSize","Size","InstallSize","WindowsInstaller"]

def _reg_str(k,n):
    try: return (winreg.QueryValueEx(k,n)[0] or "").strip()
    except OSError: return ""

def _read_uninstall_key(root, path, arch=""):
    out = []
    try:
        with winreg.OpenKey(root, path) as base:
            i = 0
            while True:
                try:
                    nm = winreg.EnumKey(base,i)
                    with winreg.OpenKey(base,nm) as k:
                        dn = _reg_str(k,"DisplayName")
                        if not dn: i+=1; continue
                        ver = _reg_str(k,"DisplayVersion")
                        pub = _reg_str(k,"Publisher")
                        u   = _reg_str(k,"UninstallString") or _reg_str(k,"QuietUninstallString")
                        sz  = 0
                        for sk in SIZE_KEYS:
                            try:
                                v = winreg.QueryValueEx(k,sk)[0]
                                if v: sz=int(v); break
                            except OSError: pass
                        out.append({"name":dn,"version":ver,"publisher":pub,
                                     "size_kb":sz,"uninstall_string":u,"arch":arch})
                    i+=1
                except OSError: break
    except OSError: pass
    return out

def _scan_store_apps():
    """Scan Store/AppX/MSIX packages via winget (no elevation needed)."""
    try:
        result = subprocess.run(
            ["winget","list"],
            capture_output=True,text=True,timeout=30,encoding="utf-8",errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode!=0 or not result.stdout.strip():
            return []
        lines = result.stdout.splitlines()
        out = []
        header_found = False
        for line in lines:
            line = line.strip()
            if not line or line.startswith("-"):
                continue
            if not header_found:
                if "Name" in line and "Id" in line:
                    header_found = True
                continue
            # winget uses 2+ spaces to separate columns
            cols = re.split(r' {2,}', line)
            if len(cols) < 2:
                continue
            name = cols[0].strip()
            raw_id = cols[1].strip() if len(cols) > 1 else ""
            version = cols[2].strip() if len(cols) > 2 else ""
            # available = cols[3].strip() if len(cols) > 3 else ""
            source = cols[-1].strip() if len(cols) > 3 else ""
            if not name or not raw_id:
                continue
            # Only include Store, MSIX and AppX packages (not ARP or pure winget)
            id_upper = raw_id.upper()
            is_store = any(tag in id_upper for tag in ["MSIX\\", "MSSTORE", "8WEKYB3D8BBWE", 
                           ".APPX", "APPX\\", "MICROSOFT."])
            # Also include Windows Store apps identified by source
            is_store = is_store or source.lower() == "msstore" or source.lower() == "winget"
            if not is_store:
                continue
            # Determine uninstall method
            uninstall_cmd = ""
            tag = "Store"
            if "MSIX\\" in id_upper or "APPX\\" in id_upper or "8WEKYB3D8BBWE" in id_upper:
                # MSIX/AppX - use winget with name (ID contains MSIX path, not winget ID)
                uninstall_cmd = f'winget uninstall --name "{name}"'
                tag = "AppX/MSIX"
            elif source.lower() == "msstore":
                uninstall_cmd = f'winget uninstall --id {raw_id} --source msstore'
                tag = "Store"
            elif source.lower() == "winget":
                uninstall_cmd = f'winget uninstall --id {raw_id} --source winget'
                tag = "Winget"
            out.append({"name":name,"version":version,
                         "publisher":source or "Microsoft Store",
                         "size_kb":0,
                         "uninstall_string":uninstall_cmd,
                         "arch":tag,
                         "store_id":raw_id})
        return out
    except Exception:
        return []

def scan_installed_software(cb=None):
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall","64-bit"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall","32-bit"),
        (winreg.HKEY_CURRENT_USER,  r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall","User"),
    ]
    items = []
    for root,path,tag in roots:
        if cb: cb(f"Scanning {tag}...")
        items.extend(_read_uninstall_key(root,path,tag))
    if cb: cb("Scanning Microsoft Store...")
    items.extend(_scan_store_apps())
    return items

def uninstall_software(item, tr):
    name = item["name"]; cmd = item.get("uninstall_string","")
    if not cmd:
        messagebox.showinfo("MClean", tr("no_cmd", name=name)); return False
    if cmd.lower().startswith("msiexec") and "/i" in cmd.lower():
        cmd = cmd.replace("/I","/X").replace("/i","/x")
    try:
        if messagebox.askyesno(tr("confirm_title"), tr("confirm",name=name,cmd=cmd)):
            subprocess.Popen(cmd, shell=True)
            messagebox.showinfo("MClean", tr("launched",name=name)); return True
    except Exception as e:
        messagebox.showerror("MClean", tr("failed", e=e))
    return False

# ════════════════════════════════════════════════════
#  GroupBox
# ════════════════════════════════════════════════════

class GroupBox(tk.Frame):
    def __init__(self, parent, text="", **kw):
        super().__init__(parent, bg=C_FACE, bd=0, **kw)
        outer = tk.Frame(self, bg=C_FACE, bd=0); outer.pack(fill="both",expand=True)
        tk.Frame(outer,bg=C_SHADOW,width=1).pack(side="top",fill="x")
        tk.Frame(outer,bg=C_SHADOW,width=1).pack(side="left",fill="y")
        self._inner = tk.Frame(outer, bg=C_FACE, bd=0)
        self._inner.pack(side="left",fill="both",expand=True,padx=4,pady=4)
        tk.Frame(outer,bg=C_HIGHLIGHT,width=1).pack(side="right",fill="y")
        tk.Frame(outer,bg=C_HIGHLIGHT,width=1).pack(side="bottom",fill="x")
        self._lbl = None
        if text:
            self._lbl = tk.Label(self._inner, text=f" {text} ", font=_FONT_SYS,
                                  bg=C_FACE, fg=C_WINDOWTEXT)
            self._lbl.pack(anchor="w", pady=(0,5))
    def set_text(self, text):
        if not self._lbl:
            self._lbl = tk.Label(self._inner, font=_FONT_SYS, bg=C_FACE, fg=C_WINDOWTEXT)
            self._lbl.pack(anchor="w", pady=(0,5))
        self._lbl.config(text=f" {text} ")

# ════════════════════════════════════════════════════
#  MClean
# ════════════════════════════════════════════════════

class MClean:
    def __init__(self):
        self.root = tk.Tk(); self.root.geometry("1060x700")
        self.root.minsize(840,540); self.root.configure(bg=C_FACE)
        self._lang = "zh"
        self._set_icon()
        self.root.attributes("-alpha",0.0); self.root.update(); self._fade_in(0.0)
        self.software_items=[]; self.filtered_items=[]; self._sort_col="size_kb"
        self._sort_rev=True; self._scan_thread=None
        self._anim_syms=["/","—","\\","|"]; self._anim_idx=0; self._anim_on=False
        self._build_ui(); self._apply_lang()
        self._pending_scan = True  # triggered when fade-in completes (inside mainloop)

    def S(self, key, **kw):
        return STRINGS[self._lang][key].format(**kw)

    # ── Icon ──────────────────────────────────────
    def _set_icon(self):
        cand = []
        if getattr(sys,'frozen',False): cand.append(os.path.join(sys._MEIPASS,"MClean.ico"))
        cand.append(os.path.join(os.path.expanduser("~"),"Desktop","MClean.ico"))
        cand.append("MClean.ico")
        for p in cand:
            if p and os.path.isfile(p):
                try: self.root.iconbitmap(p); break
                except Exception: continue

    def _fade_in(self, cur):
        cur = min(cur+0.08,1.0)
        try: self.root.attributes("-alpha",cur)
        except Exception: self.root.attributes("-alpha",1.0); return
        if cur<1.0: self.root.after(20, lambda: self._fade_in(cur))
        else:
            self.root.attributes("-alpha",1.0)
            if getattr(self, '_pending_scan', False):
                self._pending_scan = False
                self._start_scan()

    # ══════════════════════════════════════════════
    #  _build_ui  (layout only — no translated text)
    # ══════════════════════════════════════════════

    def _build_ui(self):
        # Title bar
        tb = tk.Frame(self.root,bg=C_ACTIVECAP,height=36); tb.pack(fill="x"); tb.pack_propagate(False)
        tk.Frame(tb,bg="#1A4AB0",height=4).place(x=0,y=0,relwidth=1)
        tk.Frame(tb,bg="#0A2866",height=2).place(x=0,y=34,relwidth=1)
        self._lbl_app = tk.Label(tb, font=("Microsoft YaHei UI",10,"bold"),
                                  fg=C_CAPTEXT,bg=C_ACTIVECAP)
        self._lbl_app.pack(side="left",padx=8,pady=8)
        self._lbl_sub = tk.Label(tb, font=("Microsoft YaHei UI",8),fg="#C0C0C0",bg=C_ACTIVECAP)
        self._lbl_sub.pack(side="left",pady=8)

        # Menu bar
        mb = tk.Frame(self.root,bg=C_FACE,height=22,bd=0); mb.pack(fill="x"); mb.pack_propagate(False)
        self._btn_menu_file = tk.Button(mb,font=("Microsoft YaHei UI",8),
            relief="flat",bd=0,bg=C_FACE,fg=C_WINDOWTEXT,
            activebackground=C_HIGHLIGHT,activeforeground=C_WINDOWTEXT,padx=6,pady=0)
        self._btn_menu_file.pack(side="left")
        self._btn_menu_view = tk.Button(mb,font=("Microsoft YaHei UI",8),
            relief="flat",bd=0,bg=C_FACE,fg=C_WINDOWTEXT,
            activebackground=C_HIGHLIGHT,activeforeground=C_WINDOWTEXT,padx=6,pady=0)
        self._btn_menu_view.pack(side="left")
        self._btn_menu_help = tk.Button(mb,font=("Microsoft YaHei UI",8),
            relief="flat",bd=0,bg=C_FACE,fg=C_WINDOWTEXT,
            activebackground=C_HIGHLIGHT,activeforeground=C_WINDOWTEXT,padx=6,pady=0,
            command=lambda: messagebox.showinfo(self.S("about_title"),self.S("about_text")))
        self._btn_menu_help.pack(side="left")
        tk.Frame(self.root,bg=C_SHADOW,height=1).pack(fill="x")

        # Toolbar
        bar = tk.Frame(self.root,bg=C_FACE,height=40,bd=0); bar.pack(fill="x",padx=6,pady=(4,0)); bar.pack_propagate(False)
        self._btn_ref = tk.Button(bar,font=_FONT_SYS,relief="raised",bd=2,
            bg=C_FACE,fg=C_WINDOWTEXT,activebackground=C_FACE,padx=8,pady=2,command=self._refresh)
        self._btn_ref.pack(side="left",padx=1)
        self._btn_un = tk.Button(bar,font=_FONT_SYS,relief="raised",bd=2,
            bg=C_FACE,fg=C_WINDOWTEXT,activebackground=C_FACE,padx=8,pady=2,command=self._on_uninstall_click)
        self._btn_un.pack(side="left",padx=1)
        tk.Frame(bar,bg=C_SHADOW,width=1).pack(side="left",fill="y",padx=10,pady=6)
        self._lbl_find = tk.Label(bar,font=_FONT_SYS,bg=C_FACE,fg=C_WINDOWTEXT)
        self._lbl_find.pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *a: self._apply_filter())
        self._entry_search = tk.Entry(bar,textvariable=self.search_var,
            font=_FONT_SYS,relief="sunken",bg=C_WINDOW,fg=C_WINDOWTEXT,bd=1,width=28)
        self._entry_search.pack(side="left",padx=4,ipady=2)
        # lang switch button (rightmost in toolbar)
        self._btn_lang = tk.Button(bar, font=("Microsoft YaHei UI",8,"bold"),
            relief="raised",bd=2,bg=C_FACE,fg=C_WINDOWTEXT,activebackground=C_FACE,
            padx=6,pady=2,command=self._toggle_lang)
        self._btn_lang.pack(side="right",padx=4)

        # Main
        main = tk.Frame(self.root,bg=C_FACE,bd=0); main.pack(fill="both",expand=True,padx=6,pady=4)

        # Left
        left = tk.Frame(main,bg=C_FACE,width=250); left.pack(side="left",fill="y",padx=(0,4)); left.pack_propagate(False)

        self._g_sys = GroupBox(left); self._g_sys.pack(fill="x",pady=(0,4))
        self._sys_text = tk.Text(self._g_sys._inner,font=_FONT_FIXED,
            bg=C_WINDOW,fg=C_WINDOWTEXT,relief="sunken",bd=1,wrap="word",height=10,padx=6,pady=4)
        self._sys_text.pack(fill="both",expand=True)

        self._g_stat = GroupBox(left); self._g_stat.pack(fill="x",pady=(0,4))
        self._stat_text = tk.Text(self._g_stat._inner,font=_FONT_FIXED,
            bg=C_WINDOW,fg=C_WINDOWTEXT,relief="sunken",bd=1,wrap="word",height=5,padx=6,pady=4)
        self._stat_text.pack(fill="both",expand=True)

        pgf = tk.Frame(left,bg=C_FACE,bd=0); pgf.pack(fill="x",pady=(0,4))
        self._pg_canvas = tk.Canvas(pgf,height=14,bg=C_FACE,highlightthickness=0,bd=0); self._pg_canvas.pack(fill="x")
        self._pg_label = tk.Label(pgf,font=("Microsoft YaHei UI",8),bg=C_FACE,fg=C_WINDOWTEXT,anchor="w")
        self._pg_label.pack(fill="x"); self._draw_progress(0.0)

        # Right — list
        right = tk.Frame(main,bg=C_FACE,bd=0); right.pack(side="left",fill="both",expand=True)
        self._g_list = GroupBox(right); self._g_list.pack(fill="both",expand=True)
        tf = tk.Frame(self._g_list._inner,bg=C_FACE,bd=0); tf.pack(fill="both",expand=True,padx=2,pady=2)
        tk.Frame(tf,bg=C_DARKSHADOW,width=1).pack(side="top",fill="x")
        tk.Frame(tf,bg=C_DARKSHADOW,width=1).pack(side="left",fill="y")
        ti = tk.Frame(tf,bg=C_WINDOW,bd=0); ti.pack(side="left",fill="both",expand=True)
        tk.Frame(tf,bg=C_HIGHLIGHT,width=1).pack(side="right",fill="y")
        tk.Frame(tf,bg=C_HIGHLIGHT,width=1).pack(side="bottom",fill="x")

        cols = ("name","version","publisher","size_str","arch")
        self.tree = ttk.Treeview(ti,columns=cols,show="headings",selectmode="browse",height=18)
        self.tree.heading("name",    command=lambda: self._sort_by("name"))
        self.tree.heading("version", command=lambda: self._sort_by("version"))
        self.tree.heading("publisher",command=lambda: self._sort_by("publisher"))
        self.tree.heading("size_str",command=lambda: self._sort_by("size_kb"))
        self.tree.heading("arch",    command=lambda: self._sort_by("arch"))
        self.tree.column("name",width=310); self.tree.column("version",width=80)
        self.tree.column("publisher",width=200); self.tree.column("size_str",width=90,anchor="e")
        self.tree.column("arch",width=60,anchor="center")

        sty = ttk.Style(); sty.theme_use("clam")
        sty.configure("Treeview",background=C_WINDOW,foreground=C_WINDOWTEXT,
            rowheight=26,fieldbackground=C_WINDOW,font=_FONT_SYS,borderwidth=0)
        sty.configure("Treeview.Heading",font=("Microsoft YaHei UI",8,"bold"),
            background="#D4D0C8",foreground=C_WINDOWTEXT,relief="raised",borderwidth=1)
        sty.map("Treeview.Heading",background=[("active","#C8C4BC")])
        sty.map("Treeview",background=[("selected",C_ACTIVECAP)],foreground=[("selected",C_CAPTEXT)])
        self.tree.tag_configure("large",background=C_LARGE_WARN)
        self.tree.bind("<Double-1>",lambda e: self._on_uninstall_click())
        sb = ttk.Scrollbar(ti,orient="vertical",command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set); self.tree.pack(side="left",fill="both",expand=True); sb.pack(side="right",fill="y")

        # Status bar
        so = tk.Frame(self.root,bg=C_FACE,bd=0); so.pack(fill="x",padx=3,pady=(0,3))
        tk.Frame(so,bg=C_DARKSHADOW,width=1).pack(side="top",fill="x")
        tk.Frame(so,bg=C_DARKSHADOW,width=1).pack(side="left",fill="y")
        si = tk.Frame(so,bg=C_FACE,bd=0); si.pack(side="left",fill="both",expand=True)
        tk.Frame(so,bg=C_HIGHLIGHT,width=1).pack(side="right",fill="y")
        tk.Frame(so,bg=C_HIGHLIGHT,width=1).pack(side="bottom",fill="x")
        self._status = tk.Label(si,font=("Microsoft YaHei UI",8),
            bg=C_FACE,fg=C_WINDOWTEXT,anchor="w",padx=6); self._status.pack(side="left",fill="x")
        self._warn_lbl = tk.Label(si,font=("Microsoft YaHei UI",8,"bold"),
            bg=C_FACE,fg="#CC0000",anchor="w",padx=6); self._warn_lbl.pack(side="left")
        self._prod_lbl = tk.Label(si, text=self.S("producer"), font=("Microsoft YaHei UI",8),
            bg=C_FACE,fg=C_SHADOW,anchor="e",padx=6); self._prod_lbl.pack(side="right")
        self._count_lbl = tk.Label(si,font=("Microsoft YaHei UI",8),
            bg=C_FACE,fg=C_SHADOW,anchor="e",padx=6); self._count_lbl.pack(side="right")

    # ══════════════════════════════════════════════
    #  Apply language
    # ══════════════════════════════════════════════

    def _apply_lang(self):
        s = self.S
        self.root.title(s("title"))
        self._lbl_app.config(text=f"  {s('title')}")
        self._lbl_sub.config(text="")
        self._btn_menu_file.config(text=s("menu_file"))
        self._btn_menu_view.config(text=s("menu_view"))
        self._btn_menu_help.config(text=s("menu_help"))
        self._btn_ref.config(text=s("btn_refresh"))
        self._btn_un.config(text=s("btn_uninst"))
        self._btn_lang.config(text=s("btn_lang"))
        # the search label is tricky — it was created inline. Let's store a ref.
        # We'll store it now if not yet stored.
        if not hasattr(self, '_lbl_find'):
            # Need to locate it — it's the Label just before the entry in the toolbar.
            # Simpler: set the label text in _build_ui with a stored ref.
            pass
        # Actually, let's make _build_ui store the label ref.
        # We'll fix this by adding the label ref storage in _build_ui.
        self._g_sys.set_text(s("group_sys"))
        self._g_stat.set_text(s("group_sum"))
        self._g_list.set_text(s("group_sw"))
        self.tree.heading("name",     text=s("col_name"))
        self.tree.heading("version",  text=s("col_ver"))
        self.tree.heading("publisher",text=s("col_pub"))
        self.tree.heading("size_str", text=s("col_size"))
        self.tree.heading("arch",     text=s("col_arch"))
        self._status.config(text=s("status_ready"))
        self._pg_label.config(text=s("pg_idle"))
        self._prod_lbl.config(text=s("producer"))
        if hasattr(self, '_lbl_find'):
            self._lbl_find.config(text=s("find_label"))
        # Update system info if already loaded
        if self.software_items:
            self._update_stats()
            self._render()

    def _toggle_lang(self):
        self._lang = "en" if self._lang == "zh" else "zh"
        self._apply_lang()
        # Re-render with existing data — no re-scan needed
        if self.software_items:
            self.filtered_items = list(self.software_items)
            self._sort_apply(); self._render(); self._update_stats()

    # ══════════════════════════════════════════════
    #  Animations
    # ══════════════════════════════════════════════

    def _start_breadcrumb(self):
        if self._anim_on: return
        self._anim_on=True; self._anim_idx=0; self._tick_breadcrumb()
    def _tick_breadcrumb(self):
        if not self._anim_on: return
        self._status.config(text=f" {self._anim_syms[self._anim_idx%4]} {self._status_msg}")
        self._anim_idx+=1; self.root.after(130,self._tick_breadcrumb)
    def _stop_breadcrumb(self):
        self._anim_on=False; self._status.config(text=f" {self._status_msg}")

    def _draw_progress(self, pct):
        c = self._pg_canvas
        try: w = c.winfo_width()
        except Exception: w=200
        if w<10: w=200
        h=14
        try: c.delete("all")
        except Exception: return
        if pct<0: return
        c.create_rectangle(0,0,w-1,h-1,fill=C_WINDOW,outline=C_DARKSHADOW)
        c.create_rectangle(0,0,0,h-1,fill=C_DARKSHADOW,outline="")
        c.create_rectangle(0,0,w-1,0,fill=C_DARKSHADOW,outline="")
        c.create_rectangle(w-1,0,w-1,h-1,fill=C_HIGHLIGHT,outline="")
        c.create_rectangle(0,h-1,w-1,h-1,fill=C_HIGHLIGHT,outline="")
        if pct<=0.001: return
        bw=max(2,int((w-3)*pct)); block=14
        for x in range(1,bw,block):
            c.create_rectangle(x,2,min(x+block,bw)-1,h-3,fill=C_ACTIVECAP,outline=C_ACTIVECAP)

    def _animate_progress(self, to):
        self._draw_progress(to)

    # ══════════════════════════════════════════════
    #  Data
    # ══════════════════════════════════════════════

    def _start_scan(self):
        self._status_msg = self.S("scanning"); self._status.config(text=f" {self._status_msg}")
        self._pg_label.config(text=self.S("pg_init")); self._draw_progress(0.0); self._start_breadcrumb()
        self._scan_thread = threading.Thread(target=self._load_data,daemon=True); self._scan_thread.start()

    def _load_data(self):
        info = get_system_info(self.S)
        self.root.after(0,lambda: self._show_sys(info))
        self.root.after(0,lambda: self._pg_label.config(text=self.S("pg_reg")))
        self.root.after(0,lambda: self._draw_progress(0.2))
        items = scan_installed_software(); items.sort(key=lambda x: x.get("size_kb",0) or 0, reverse=True)
        self.root.after(0,lambda: self._pg_label.config(text=self.S("pg_render")))
        self.root.after(0,lambda: self._draw_progress(0.85))
        self.software_items = items; self.root.after(0,self._scan_done)

    def _show_sys(self, info):
        self._sys_text.config(state="normal"); self._sys_text.delete("1.0","end")
        for k,v in info.items(): self._sys_text.insert("end",f"{k}:\n  {v}\n")
        self._sys_text.config(state="disabled")

    def _scan_done(self):
        self._stop_breadcrumb(); n = len(self.software_items)
        self._status_msg = self.S("done",n=n); self._status.config(text=f" {self._status_msg}")
        self._pg_label.config(text=self.S("pg_idle")); self._draw_progress(1.0)
        self._apply_filter(); self.root.after(300,lambda: self._draw_progress(0.0))

    def _refresh(self): self._start_scan()

    # ══════════════════════════════════════════════
    #  Filter / Sort / Render
    # ══════════════════════════════════════════════

    def _apply_filter(self):
        q = self.search_var.get().lower().strip()
        self.filtered_items = [it for it in self.software_items
            if q in it["name"].lower() or q in it.get("publisher","").lower()] if q else list(self.software_items)
        self._sort_apply(); self._render(); self._update_stats()

    def _sort_by(self, col):
        self._sort_rev = not self._sort_rev if self._sort_col==col else (col=="size_kb"); self._sort_col=col
        for c in ("name","version","publisher","size_str","arch"):
            t = self.tree.heading(c)["text"].rstrip(" ↑↓▲▼")
            self.tree.heading(c,text=t+(" " + ("↓" if self._sort_rev else "↑") if c==col else ""))
        self._sort_apply(); self._render()

    def _sort_apply(self):
        k,rv = self._sort_col,self._sort_rev
        def keyfn(it):
            v = it.get(k, "") or ""
            if k == "size_kb":
                try: return (0, int(v))
                except (ValueError, TypeError): return (0, 0)
            if isinstance(v, str): v = v.lower()
            return (1, v)
        self.filtered_items.sort(key=keyfn, reverse=rv)

    def _render(self):
        self.tree.delete(*self.tree.get_children()); big=0
        for it in self.filtered_items:
            sz = it.get("size_kb",0) or 0
            s = f"{sz/(1024*1024):.1f} GB" if sz>=1024*1024 else (f"{sz/1024:.1f} MB" if sz>=1024 else (f"{sz} KB" if sz else "—"))
            if sz>=1024*1024: big+=1
            self.tree.insert("","end",values=(it["name"],it.get("version",""),it.get("publisher",""),s,it.get("arch","")),
                             tags=("large",) if sz>=1024*1024 else ())
        if big:
            gb = sum((it.get("size_kb",0) or 0)/(1024*1024) for it in self.filtered_items if (it.get("size_kb",0) or 0)>=1024*1024)
            self._warn_lbl.config(text=self.S("warn_large",n=big,gb=gb))
        else: self._warn_lbl.config(text="")
        self._count_lbl.config(text=self.S("items",n=len(self.filtered_items)))

    def _update_stats(self):
        t=len(self.filtered_items); kn=[it for it in self.filtered_items if (it.get("size_kb",0) or 0)>0]
        big=[it for it in kn if it["size_kb"]>=1024*1024]; gb=sum(it["size_kb"] for it in kn)/(1024*1024)
        self._stat_text.config(state="normal"); self._stat_text.delete("1.0","end")
        self._stat_text.insert("end",
            f"{self.S('stat_listed')}{t}\n{self.S('stat_sized')}{len(kn)}\n"
            f"{self.S('stat_large')}{len(big)}\n{self.S('stat_total')}{gb:.1f} GB\n")
        self._stat_text.config(state="disabled")

    def _on_uninstall_click(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("MClean", self.S("sel_first")); return
        vals = self.tree.item(sel[0], "values")
        if vals:
            it = next((x for x in self.filtered_items if x["name"]==vals[0]), None)
            if it: uninstall_software(it, self.S)

    def run(self): self.root.mainloop()


if __name__ == "__main__":
    MClean().run()
