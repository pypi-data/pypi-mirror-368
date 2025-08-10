#!/usr/bin/env python3
import sys, json, pathlib, os, signal, re
from pathlib import Path
import gi

# Forcing the GTK version if the environment variable is set
force = os.environ.get("OBSIDIAN_STICKY_GTK", "").strip()
if force == "4":
  gi.require_version("WebKit2", "5.0")
  gi.require_version("Gtk", "4.0")
  from gi.repository import Gtk, GLib, WebKit2, Gdk, Gio
  IS_GTK4, WEBKIT_API = True, "5.0"
else:
  try:
    gi.require_version("WebKit2", "4.1")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, GLib, WebKit2, Gdk, Gio
    IS_GTK4, WEBKIT_API = False, "4.1"
  except Exception:
    gi.require_version("WebKit2", "5.0")
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk, GLib, WebKit2, Gdk, Gio
    IS_GTK4, WEBKIT_API = True, "5.0"

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
try:
  import yaml
except Exception:
  yaml = None

from .renderer import render_markdown_to_html

# Defining the package assets path and loading the base CSS and JavaScript
PKG_ASSETS = pathlib.Path(__file__).with_suffix('').parent / "assets"
STYLE_CSS = (PKG_ASSETS / "css" / "sticky.css").read_text()
BOOT_JS = (PKG_ASSETS / "js" / "boot.js").read_text() if (PKG_ASSETS / "js" / "boot.js").exists() else ""

# Defining the HTML shell with a valid document structure
HTML_SHELL = f"""<!doctype html>
<html class="__ROOT_CLASS__">
<head>
  <meta charset=utf-8>
  <style id="sticky-base-style">{STYLE_CSS}</style>
  <style id="sticky-custom-style">__CUSTOM_CSS__</style>
</head>
<body style="opacity:__OPACITY__">
  <div id="root">
    <div id="content">__CONTENT__</div>
  </div>
  <script>{BOOT_JS}</script>
</body>
</html>"""

# Initialising the state file variable and hardcoded default settings
STATE_FILE = None
DEFAULTS = {"theme": "canary", "opacity": 1.0, "w": None, "h": None, "click_through": False, "x": None, "y": None}

def load_custom_css(vault_path=None, cfg_css_path=None):
  """
  Loading the custom CSS from a user-defined file
  """
  try:
    css_path = (os.environ.get("OBSIDIAN_STICKY_CSS") or "").strip()
    if not css_path and cfg_css_path:
      css_path = str(cfg_css_path).strip()
    if not css_path:
      return ""
    p = Path(css_path).expanduser()
    if not p.is_absolute() and vault_path:
      p = Path(vault_path) / css_path
    if p.exists():
      return p.read_text(encoding="utf-8")
  except Exception:
    pass
  return ""

def _meta_normalise(meta: dict, defaults: dict) -> dict:
  """
  Normalising the metadata from the note's front matter using the provided defaults
  """
  def first_key(d, keys, default=None):
    for k in keys:
      if k in d: return d[k]
    return default
  out = dict(defaults)
  theme = first_key(meta, ["theme", "Theme"], out["theme"])
  theme = str(theme).strip().lower().replace(" ", "-") if theme is not None else out["theme"]
  out["theme"] = theme
  try:
    op = float(first_key(meta, ["opacity", "Opacity"], out["opacity"]))
  except Exception:
    op = out["opacity"]
  out["opacity"] = max(0.0, min(1.0, op))
  def to_int(x):
    try: return int(x)
    except Exception: return None
  w = first_key(meta, ["w", "width", "Width"], out["w"])
  h = first_key(meta, ["h", "height", "Height"], out["h"])
  out["w"] = to_int(w) if w is not None else out["w"]
  out["h"] = to_int(h) if h is not None else out["h"]
  ct = first_key(meta, ["click_through", "click-through", "clickthrough", "ClickThrough", "Click-through"], out["click_through"])
  out["click_through"] = bool(ct) if isinstance(ct, bool) else str(ct).strip().lower() in ("1", "true", "yes", "on")
  return out

def _save_front_matter(note_path: Path, updates: dict) -> bool:
  """
  Saving the updated metadata to the note's front matter
  """
  try:
    txt = Path(note_path).read_text(encoding="utf-8")
    m = __import__("re").match(r"(?s)^---\\n(.*?)\\n---\\n(.*)$", txt)
    fm, body = {}, txt
    if m:
      fm_txt, body = m.group(1), m.group(2)
      try:
        fm = yaml.safe_load(fm_txt) if yaml else {}
        if fm is None: fm = {}
      except Exception:
        fm = {}
    fm.update(updates)
    new_fm = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True) if yaml else ""
    new_txt = f"---\\n{new_fm.strip()}\\n---\\n{body}"
    Path(note_path).write_text(new_txt, encoding="utf-8")
    return True
  except Exception:
    return False

class DragHandle(Gtk.EventBox if not IS_GTK4 else Gtk.Box):
  """
  A custom drag handle widget for moving the window
  """
  def __init__(self, win):
    super().__init__()
    self._win = win
    if IS_GTK4:
      self.set_size_request(-1, 10)
      gesture = Gtk.GestureClick()
      def on_press(gest, n_press, x, y):
        try:
          btn = 1
          ts = int(GLib.get_monotonic_time() / 1000)
          self._win.win.begin_move_drag(btn, int(x), int(y), ts)
        except Exception: pass
      gesture.connect("pressed", on_press)
      self.add_controller(gesture)
    else:
      self.set_size_request(-1, 10)
      self.set_visible_window(False)
      self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
      def on_button_press(widget, event):
        try:
          if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self._win.win.begin_move_drag(int(event.button), int(event.x_root), int(event.y_root), int(event.time))
            return True
        except Exception: pass
        return False
      self.connect("button-press-event", on_button_press)

class ResizeGrip(Gtk.EventBox if not IS_GTK4 else Gtk.Box):
  """
  A custom resize grip widget for resizing the window
  """
  def __init__(self, win):
    super().__init__()
    self._win = win
    self.set_size_request(16, 16)
    if IS_GTK4:
      gesture = Gtk.GestureDrag()
      def on_update(gest, dx, dy):
        try:
          alloc = self._win.win.get_allocation()
          self._win.win.set_default_size(max(160, alloc.width + int(dx)), max(120, alloc.height + int(dy)))
        except Exception: pass
      gesture.connect("drag-update", on_update)
      self.add_controller(gesture)
    else:
      self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON1_MOTION_MASK)
      self.connect("button-press-event", lambda *a: True)
      def on_motion(widget, event):
        try:
          alloc = self._win.win.get_allocation()
          self._win.win.resize(max(160, alloc.width + int(event.x)), max(120, alloc.height + int(event.y)))
        except Exception: pass
        return True
      self.connect("motion-notify-event", on_motion)

class NoteWindow(object):
  """
  The main class for a single sticky note window
  """
  def __init__(self, vault: pathlib.Path, note: pathlib.Path, cfg_css_path=None, defaults=None):
    self.vault = vault
    self.note = note
    self.cfg_css_path = cfg_css_path
    self.defaults = defaults if defaults is not None else DEFAULTS.copy()

    # --- State Management ---
    self._theme_override = None
    self._click_through_override = None
    self._last_theme = self.defaults["theme"]
    self._click_through = self.defaults["click_through"]
    self._last_x = None
    self._last_y = None
    self._last_w = None
    self._last_h = None
    self._initial_pos_set = False
    self.available_themes = self._discover_themes()

    if IS_GTK4:
      self.win = Gtk.Window(title=f"Sticky: {note.name}")
      self.win.set_decorated(False)
      css_provider = Gtk.CssProvider()
      css_provider.load_from_data(b"window { background-color: transparent; }")
      Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
      self.win.set_resizable(True)
      self.win.set_default_size(380, 280)
      try: self.win.set_focusable(False)
      except Exception: pass
      box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
      self.win.set_child(box)
      box.append(DragHandle(self))
      self.web = WebKit2.WebView()
      self.web.set_background_color(Gdk.RGBA(0, 0, 0, 0))
      settings = self.web.get_settings()
      settings.set_enable_developer_extras(True)
      self.web.set_settings(settings)
      # GTK4 context menu would be implemented here if needed
      self.web.connect("decide-policy", self.on_nav)
      box.append(self.web)
      griprow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
      griprow.append(Gtk.Box())
      griprow.append(ResizeGrip(self))
      box.append(griprow)
      self.win.connect("close-request", self.on_close)
    else: # GTK3
      self.win = Gtk.Window()
      self.win.set_title(f"Sticky: {note.name}")
      self.win.set_decorated(False)
      screen = self.win.get_screen()
      visual = screen.get_rgba_visual()
      if visual and screen.is_composited():
        self.win.set_visual(visual)
      self.win.set_app_paintable(True)
      css_provider = Gtk.CssProvider()
      css_provider.load_from_data(b"GtkWindow { background-color: transparent; }")
      Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
      self.win.set_resizable(True)
      self.win.set_default_size(380, 280)
      try:
        self.win.set_accept_focus(False)
        self.win.set_wmclass("obsidian-sticky", "Obsidian-sticky")
      except Exception: pass
      box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
      self.win.add(box)
      box.pack_start(DragHandle(self), False, False, 0)
      self.web = WebKit2.WebView()
      self.web.set_background_color(Gdk.RGBA(0, 0, 0, 0))
      settings = self.web.get_settings()
      settings.set_enable_developer_extras(True)
      self.web.set_settings(settings)
      self.web.connect("context-menu", self.on_context_menu)
      self.web.connect("decide-policy", self.on_nav)
      box.pack_start(self.web, True, True, 0)
      griprow = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
      griprow.pack_start(Gtk.Box(), True, True, 0)
      griprow.pack_start(ResizeGrip(self), False, False, 0)
      box.pack_start(griprow, False, False, 0)
      self.win.connect("delete-event", self.on_close_gtk3)

    self.reload()

    try:
      s = json.loads((vault / ".sticky-state.json").read_text())
      g = s.get(str(note), {})
    except Exception:
      s, g = {}, {}
    try:
      _, meta = render_markdown_to_html(self.note)
      nm = _meta_normalise(meta, self.defaults)
      w, h = (nm.get("w"), nm.get("h")) if (nm.get("w") and nm.get("h")) else (g.get("w"), g.get("h"))
      if w and h:
        self.win.set_default_size(int(w), int(h))
        if not IS_GTK4: self.win.resize(int(w), int(h))
      self._last_x, self._last_y = g.get("x"), g.get("y")
    except Exception:
      pass
      
    self.win.connect("configure-event", self._on_configure)

  def _discover_themes(self):
    """
    Discovering available themes from the base and custom CSS files
    """
    base_themes = ["canary", "parchment", "graphite"]
    custom_themes = []
    
    custom_css = load_custom_css(self.vault, self.cfg_css_path)
    if custom_css:
      # Finding all instances of 'html.theme-...' in the CSS
      found = re.findall(r'html\.theme-([a-zA-Z0-9_-]+)', custom_css)
      custom_themes.extend(found)
      
    # Combining, deduplicating, and sorting the theme list
    all_themes = sorted(list(set(base_themes + custom_themes)))
    return all_themes

  def _on_configure(self, widget, event):
    if not self._initial_pos_set and self._last_x is not None and self._last_y is not None:
      self.win.move(self._last_x, self._last_y)
      self._initial_pos_set = True
    else:
      x, y = self.win.get_position()
      self._last_x, self._last_y = x, y
    
    if not IS_GTK4:
        alloc = self.win.get_allocation()
        self._last_w, self._last_h = alloc.width, alloc.height

  def _build_context_menu(self):
    if IS_GTK4: return None
    menu = Gtk.Menu()

    item_theme = Gtk.MenuItem(label="Theme")
    submenu = Gtk.Menu()
    current = self._last_theme
    head = None
    for th in self.available_themes:
      label = th.capitalize()
      radio = Gtk.RadioMenuItem.new_with_label(None, label) if head is None else Gtk.RadioMenuItem.new_with_label_from_widget(head, label)
      if head is None: head = radio
      if th == current: radio.set_active(True)
      def on_pick(mi, th_name=th):
        if mi.get_active():
          self._theme_override = th_name
          self.reload()
      radio.connect("toggled", on_pick)
      submenu.append(radio)
    item_theme.set_submenu(submenu)
    menu.append(item_theme)

    item_toggle = Gtk.CheckMenuItem(label="Click-through (content)")
    item_toggle.set_active(self._click_through)
    def on_toggle(mi):
      self._click_through_override = mi.get_active()
      self.reload()
    item_toggle.connect("toggled", on_toggle)
    menu.append(item_toggle)

    menu.append(Gtk.SeparatorMenuItem())
    
    item_save_theme = Gtk.MenuItem(label="Save theme to front matter")
    item_save_theme.connect("activate", lambda *_: _save_front_matter(Path(self.note), {"theme": self._last_theme}))
    menu.append(item_save_theme)

    item_save_size = Gtk.MenuItem(label="Save current size to front matter")
    def on_save_size(_mi):
      _save_front_matter(Path(self.note), {"w": self._last_w, "h": self._last_h})
    item_save_size.connect("activate", on_save_size)
    menu.append(item_save_size)
    
    menu.append(Gtk.SeparatorMenuItem())

    item_debug = Gtk.MenuItem(label="Debug → Show applied state…")
    def on_debug(_):
      try:
        _, meta = render_markdown_to_html(self.note)
        nm = _meta_normalise(meta, self.defaults)
        alloc = self.win.get_allocation()
        info = f"Front matter: {meta}\\nNormalized: {nm}\\nroot_class: theme-{nm['theme']}{' click-through' if self._click_through else ''}\\nopacity: {nm['opacity']}\\nsize: {alloc.width}×{alloc.height}"
        dlg = Gtk.MessageDialog(parent=self.win, flags=0, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.OK, message_format=info)
        dlg.run()
        dlg.destroy()
      except Exception: pass
    item_debug.connect("activate", on_debug)
    menu.append(item_debug)
    
    item_inspector = Gtk.MenuItem(label="Inspect Element")
    def on_inspector(*_): self.web.get_inspector().show()
    item_inspector.connect("activate", on_inspector)
    menu.append(item_inspector)

    menu.show_all()
    return menu

  def on_context_menu(self, webview, context_menu, event, hit_test_result):
    """
    Handling the context menu to show our custom Gtk.Menu
    """
    menu = self._build_context_menu()
    if menu:
        menu.popup_at_pointer(event)
    return True # Suppressing the default WebKit menu

  def present(self):
    if IS_GTK4: self.win.present()
    else: self.win.show_all()

  def persist_geometry(self):
    try:
      s = {}
      st = self.vault / ".sticky-state.json"
      if st.exists():
        s = json.loads(st.read_text(encoding="utf-8"))
      
      if IS_GTK4:
        w, h = self.win.get_default_size()
      else:
        w, h = self._last_w, self._last_h
        
      if w and h and self._last_x is not None and self._last_y is not None:
        s[str(self.note)] = {"w": int(w), "h": int(h), "x": self._last_x, "y": self._last_y}
        st.write_text(json.dumps(s, indent=2, ensure_ascii=False))
    except Exception: pass

  def on_close(self, *_): self.persist_geometry()
  def on_close_gtk3(self, *a):
    self.persist_geometry()
    Gtk.main_quit()
    return False

  def reload(self):
    html, meta = render_markdown_to_html(self.note)
    nm = _meta_normalise(meta, self.defaults)
    theme = self._theme_override if self._theme_override is not None else nm["theme"]
    click_through = self._click_through_override if self._click_through_override is not None else nm["click_through"]
    opacity = nm["opacity"]
    self._last_theme = theme
    self._click_through = click_through
    
    custom_css = load_custom_css(Path(self.vault), self.cfg_css_path)
    root_class = f"theme-{theme}" + (" click-through" if click_through else "")
    shell = HTML_SHELL.replace("__CONTENT__", html) \
                      .replace("__ROOT_CLASS__", root_class) \
                      .replace("__OPACITY__", str(opacity)) \
                      .replace("__CUSTOM_CSS__", custom_css)
    base_uri = "file://" + str(self.note.parent) + "/"
    self.web.load_html(shell, base_uri)

  def on_nav(self, webview, decision, decision_type):
    try:
      nav = decision.get_navigation_action(); req = nav.get_request(); uri = req.get_uri()
    except Exception: return False
    if uri.startswith("http") or uri.startswith("file:"): return False
    decision.ignore(); return True

class NoteHandler(FileSystemEventHandler):
  def __init__(self, win: 'NoteWindow'): self.win = win
  def on_modified(self, ev):
    p = pathlib.Path(ev.src_path)
    if p == self.win.note:
      self.win._theme_override = None
      self.win._click_through_override = None
      GLib.idle_add(self.win.reload)

def expanduser(p: str) -> pathlib.Path: return pathlib.Path(os.path.expanduser(p)).resolve()
def load_config(path: pathlib.Path):
  if not path.exists(): return None
  if yaml is None: raise RuntimeError("PyYAML not installed; cannot read config.")
  with open(path, "r", encoding="utf-8") as fh: return yaml.safe_load(fh) or {}

def parse_args(argv):
  import argparse
  ap = argparse.ArgumentParser(prog="obsidian-sticky-notes", description="Obsidian Markdown sticky windows.")
  ap.add_argument("--debug", action="store_true")
  ap.add_argument("--config", nargs="?", const="auto", help="Use YAML config (default path if omitted)")
  ap.add_argument("--vault", help="Vault path (overrides config)")
  ap.add_argument("notes", nargs="*", help="Note paths (relative to vault)")
  return ap.parse_args(argv)

def main():
  args = parse_args(sys.argv[1:])
  if args.debug:
    print("GTK:", "4.x" if IS_GTK4 else "3.x"); print("WebKit2 API:", WEBKIT_API)
    try:
      import markdown_it, frontmatter, watchdog
      print("markdown-it-py:", getattr(markdown_it, "__version__", "unknown"))
      print("python-frontmatter:", getattr(frontmatter, "__version__", "unknown"))
      import watchdog.observers
      print("watchdog:", getattr(watchdog, "__version__", "unknown"))
      print("PyYAML:", getattr(yaml, "__version__", "missing") if yaml else "missing")
    except Exception as e: print("Diagnostics error:", e)
    sys.exit(0)

  vault = None; notes = []; cfg_css_path = None
  final_defaults = DEFAULTS.copy()

  if args.config:
    cfg_path = (pathlib.Path("~/.config/obsidian-sticky/config.yml").expanduser() if args.config == "auto" else expanduser(args.config))
    if not cfg_path.exists() and args.config == "auto":
      alt = pathlib.Path("~/.config/obsidian-sticky/config.yaml").expanduser()
      if alt.exists(): cfg_path = alt
    cfg = load_config(cfg_path)
    if not cfg: print(f"Config not found or empty: {cfg_path}"); sys.exit(2)
    vault = expanduser(cfg.get("vault",""))
    if not vault.exists(): print(f"Vault path in config does not exist: {vault}"); sys.exit(2)
    cfg_css_path = cfg.get("css")
    config_defaults = cfg.get("defaults", {})
    if config_defaults: final_defaults.update(config_defaults)
    for n in (cfg.get("notes") or []): notes.append(vault / n)

  if args.vault: vault = expanduser(args.vault)
  if args.notes: notes.extend([(vault / n) if vault else expanduser(n) for n in args.notes])

  if not vault or not notes:
    print("Usage: obsidian-sticky-notes --vault ~/Vault 'Pessoal/Compras necessárias.md' [...]")
    print("   or: obsidian-sticky-notes --config"); sys.exit(2)

  global STATE_FILE; STATE_FILE = vault / ".sticky-state.json"

  windows=[]
  def shutdown_handler(*args):
    for win in windows:
      win.persist_geometry()
    Gtk.main_quit()
  
  GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGTERM, shutdown_handler)
  GLib.unix_signal_add(GLib.PRIORITY_DEFAULT, signal.SIGINT, shutdown_handler)

  def start_note(app_, note_path, defaults):
    win = NoteWindow(vault, note_path, cfg_css_path=cfg_css_path, defaults=defaults)
    if IS_GTK4 and app_ is not None: win.win.set_application(app_)
    win.present()
    obs = Observer(); obs.schedule(NoteHandler(win), str(note_path), recursive=False); obs.start()
    windows.append(win)

  if IS_GTK4:
    app = Gtk.Application(application_id="dev.sticky.obsidian")
    def activate(app_):
      for n in notes: start_note(app_, pathlib.Path(n), final_defaults)
    app.run()
  else:
    for n in notes: start_note(None, pathlib.Path(n), final_defaults)
    Gtk.main()

if __name__ == "__main__":
  main()