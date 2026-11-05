"""Device mode: pots (and faders in Device fader mode) control the parameters of a plugin.

Which plugin ("the device"):
1. the locked one, while Device Lock is on;
2. otherwise the focused plugin window (generator or mixer effect);
3. otherwise the one last picked with Device Select + pad;
4. otherwise the selected channel's instrument.

Parameters are paged in eights over the plugin's *named* parameters; Track < > turns pages while the pots are in
Device mode. Plugins with a map in ``plugin_maps`` (e.g. Vital) first get curated, titled pages (pots 1-8 and faders
1-8 each), followed by the generic pages.

Device Select held turns the pads into a device picker (top row: channels, bottom row: the selected mixer track's
effect slots); a short press opens / closes the device's window.
"""

from lkmk3fl import config, host, plugin_maps
from lkmk3fl import flconst as fl
from lkmk3fl import palette as pal
from lkmk3fl import protocol as p
from lkmk3fl.controls import NoTarget, PluginParam
from lkmk3fl.leds import LedState

MAX_SCANNED_PARAMS = 4096


class DeviceMixin:
    def reset_state(self):
        super().reset_state()
        self.locked = None
        self.picked = None
        self.param_pages = {}  # plugin -> page
        self.param_cache = {}  # plugin -> [(param index, name)]
        self.curated_cache = {}  # plugin -> (map name, [plugin_maps.Page]) or None
        self.last_device = None
        self.device_select_held = False
        self.device_select_used = False
        self.pad_mode_before_select = p.PAD_SESSION
        self.pot_mode_before_device = p.POT_PAN

    # ------------------------------------------------------------------------------------------------ the device

    def device(self):
        if self.locked is not None:
            return self.locked if host.plugin_valid(self.locked) else None
        focused = host.focused_plugin()
        if focused is not None and host.plugin_valid(focused):
            return focused
        if self.picked is not None and host.plugin_valid(self.picked):
            return self.picked
        ch = host.selected_channel()
        if ch >= 0 and host.plugin_valid((ch, -1)):
            return (ch, -1)
        return None

    def device_params(self, plugin):
        params = self.param_cache.get(plugin)
        if params is None:
            params = []
            try:
                count = min(host.param_count(plugin), MAX_SCANNED_PARAMS)
                for i in range(count):
                    name = host.param_name(plugin, i)
                    if name and name.strip():
                        params.append((i, name.strip()))
            except Exception:
                params = []
            self.param_cache[plugin] = params
        return params

    def device_name(self, plugin):
        try:
            return host.plugin_name(plugin)
        except Exception:
            return "Device"

    def curated(self, plugin):
        """(map name, pages) when a plugin map applies to ``plugin`` (e.g. Vital), else None."""
        if not config.CURATED_PLUGIN_PAGES:
            return None
        if plugin in self.curated_cache:
            return self.curated_cache[plugin]
        result = None
        try:
            m = plugin_maps.find_map(host.plugin_original_name(plugin), host.plugin_name(plugin))
            if m is not None:
                count = min(host.param_count(plugin), MAX_SCANNED_PARAMS)
                names = [host.param_name(plugin, i) for i in range(count)]
                pages = plugin_maps.resolve(m, names)
                if pages:
                    result = (m["name"], pages)
        except Exception:
            result = None
        self.curated_cache[plugin] = result
        return result

    def generic_per_page(self):
        # 8 parameters per page; with the faders in Device mode a page is 16 (pots 1-8, faders 9-16)
        return 16 if (self.has_faders and self.fader_mode == p.FADER_DEVICE) else 8

    def generic_page_count(self, plugin):
        per_page = self.generic_per_page()
        return (len(self.device_params(plugin)) + per_page - 1) // per_page

    def param_page_count(self, plugin):
        curated = self.curated(plugin)
        extra = len(curated[1]) if curated else 0
        return max(1, extra + self.generic_page_count(plugin))

    def current_page(self, plugin):
        return min(self.param_pages.get(plugin, 0), self.param_page_count(plugin) - 1)

    def page_title(self, plugin):
        """Name of a curated page ("Macros"), "" for generic pages."""
        curated = self.curated(plugin)
        page = self.current_page(plugin)
        if curated and page < len(curated[1]):
            return curated[1][page].name
        return "Params" if curated else ""

    def device_target(self, slot):
        plugin = self.device()
        if plugin is None:
            return NoTarget("No device")
        page = self.current_page(plugin)
        curated = self.curated(plugin)
        if curated:
            pages = curated[1]
            if page < len(pages):
                entry = pages[page].slots[slot]
                if entry is None:
                    return NoTarget("-")
                index, label = entry
                return PluginParam(plugin, index, label)
            page -= len(pages)
        params = self.device_params(plugin)
        per_page = self.generic_per_page()
        if slot >= per_page:  # faders outside a 16-parameter generic page (not in Device fader mode)
            return NoTarget("-")
        i = page * per_page + slot
        if i >= len(params):
            return NoTarget("-")
        index, name = params[i]
        return PluginParam(plugin, index, name)

    def check_device_change(self):
        plugin = self.device()
        if plugin != self.last_device:
            self.last_device = plugin
            if plugin is not None and self.pot_mode == p.POT_DEVICE:
                self.message(self.device_name(plugin), self.page_text(plugin))
            self.update_labels()
            return True
        return False

    def page_text(self, plugin):
        """ "Page 2/5", or with a curated page "2/5 Osc"."""
        number = "%d/%d" % (self.current_page(plugin) + 1, self.param_page_count(plugin))
        title = self.page_title(plugin)
        return (number + " " + title) if title else ("Page " + number)

    # ------------------------------------------------------------------------------------------------ buttons

    def navigate_track(self, delta):
        if self.pot_mode == p.POT_DEVICE and not self.shift:
            plugin = self.device()
            if plugin is None:
                self.message("No device")
                return
            page = self.param_pages.get(plugin, 0) + delta
            page = max(0, min(self.param_page_count(plugin) - 1, page))
            self.param_pages[plugin] = page
            self.retarget()
            self.message(self.device_name(plugin), self.page_text(plugin))
            return
        super().navigate_track(delta)

    def _btn_device_select(self):
        if self.shift:  # pots: Device mode <-> the mode before
            if self.pot_mode == p.POT_DEVICE:
                mode = self.pot_mode_before_device
            else:
                self.pot_mode_before_device = self.pot_mode
                mode = p.POT_DEVICE
            host.send(p.pot_mode(mode))
            self.on_event(p.Event("pot_mode", value=mode))
            return
        self.device_select_held = True
        self.device_select_used = False
        if self.pad_mode != p.PAD_DEVICE_SELECT:
            self.pad_mode_before_select = self.pad_mode
            host.send(p.pad_mode(p.PAD_DEVICE_SELECT))
            self.on_pad_mode(p.PAD_DEVICE_SELECT)
        plugin = self.device()
        self.message("Device Select", self.device_name(plugin) if plugin else "pick a pad")

    def on_button_release(self, e):
        super().on_button_release(e)
        if e.button != p.DEVICE_SELECT or not self.device_select_held:
            return
        self.device_select_held = False
        if self.pad_mode == p.PAD_DEVICE_SELECT:
            host.send(p.pad_mode(self.pad_mode_before_select))
            self.on_pad_mode(self.pad_mode_before_select)
        if not self.device_select_used:
            self.toggle_device_window()

    def toggle_device_window(self):
        plugin = self.device()
        if plugin is None:
            self.message("No device")
            return
        index, slot = plugin
        if slot < 0:
            host.show_channel_editor(index)
        else:
            host.focus_effect(index, slot)
        self.message(self.device_name(plugin))

    def _btn_device_lock(self):
        if self.locked is not None:
            self.locked = None
            self.message("Device unlocked")
        else:
            plugin = self.device()
            if plugin is None:
                self.message("Device Lock", "no device")
                return
            self.locked = plugin
            self.message("Locked", self.device_name(plugin))
        self.check_device_change()
        self.retarget()

    # ------------------------------------------------------------------------------------------------ pads

    def device_select_channels(self):
        ch = max(0, host.selected_channel())
        first = (ch // 8) * 8
        return [c if c < host.channel_count() else -1 for c in range(first, first + 8)]

    def on_device_select_pad(self, e):
        if not e.pressed:
            return
        self.device_select_used = True
        if e.index < 8:
            ch = self.device_select_channels()[e.index]
            if ch < 0:
                return
            host.select_channel(ch)
            self.pick((ch, -1))
        else:
            slot = e.index - 8
            track = host.selected_track()
            if not host.is_effect_valid(track, slot):
                self.message("Slot %d" % (slot + 1), "empty")
                return
            host.focus_effect(track, slot)
            self.pick((track, slot))

    def pick(self, plugin):
        self.picked = plugin
        if self.locked is not None:
            self.locked = plugin
        self.last_device = None
        self.check_device_change()
        self.message(self.device_name(plugin), "selected")

    def on_channel_selected(self, channel):
        super().on_channel_selected(channel)
        self.picked = None

    def device_select_leds(self):
        out = []
        device = self.device()
        selected = host.selected_channel()
        for ch in self.device_select_channels():
            if ch < 0:
                out.append(LedState(pal.OFF))
                continue
            colour = pal.of_fl_colour(host.channel_colour(ch))
            if device == (ch, -1):
                out.append(LedState(colour, p.PULSING))
            elif ch == selected:
                out.append(LedState(colour))
            else:
                out.append(LedState(pal.dimmed(colour)))
        track = host.selected_track()
        for slot in range(8):
            if not host.is_effect_valid(track, slot):
                out.append(LedState(pal.OFF))
            elif device == (track, slot):
                out.append(LedState(pal.CYAN, p.PULSING))
            else:
                out.append(LedState(pal.DIM_CYAN))
        return out

    # ------------------------------------------------------------------------------------------------ feedback

    def button_leds(self, leds):
        super().button_leds(leds)
        leds[("cc", p.DEVICE_SELECT_CC)] = LedState(pal.WHITE if self.device() is not None else pal.DIM_WHITE)
        leds[("cc", p.DEVICE_LOCK_CC)] = LedState(pal.WHITE if self.locked is not None else pal.DIM_WHITE)
        if self.pot_mode == p.POT_DEVICE and not self.shift:
            plugin = self.device()
            if plugin is not None:
                page = self.param_pages.get(plugin, 0)
                leds[("cc", p.TRACK_LEFT_CC)] = LedState(pal.WHITE if page > 0 else pal.OFF)
                more = page + 1 < self.param_page_count(plugin)
                leds[("cc", p.TRACK_RIGHT_CC)] = LedState(pal.WHITE if more else pal.OFF)

    def default_rows(self):
        top, bottom = super().default_rows()
        if self.pot_mode == p.POT_DEVICE:
            plugin = self.device()
            if plugin is not None:
                top = self.device_name(plugin)
                text = self.page_text(plugin)
                bottom = "Dev " + (text[5:] if text.startswith("Page ") else text) + (" LOCK" if self.locked else "")
            else:
                top = "No device"
        return top, bottom

    def on_refresh(self, flags):
        if flags & (fl.HW_DIRTY_FOCUSED_WINDOW | fl.HW_DIRTY_REMOTE_LINKS | fl.HW_DIRTY_NAMES):
            self.param_cache.clear()  # plugin replaced or renamed parameters
            self.curated_cache.clear()
        if self.active:
            self.check_device_change()
        super().on_refresh(flags)

    def on_event(self, e):
        handled = super().on_event(e)
        if e.kind == "pot_mode" and e.value == p.POT_DEVICE:
            self.last_device = None
            self.check_device_change()
        return handled
