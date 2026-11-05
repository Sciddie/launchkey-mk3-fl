"""The Launchkey MK3's 16 x 2 LCD: default rows, temporary messages, and pot / fader labels, all cached."""

from lkmk3fl import host
from lkmk3fl import protocol as p


class Display:
    def __init__(self, clock):
        self.clock = clock
        self.rows = [None, None]
        self.labels = {}  # ("pot"|"fader", index, "name"|"value") -> text
        self.message = None
        self.message_until = 0.0

    def forget(self):
        self.rows = [None, None]
        self.labels.clear()

    def show_message(self, top, bottom="", seconds=1.5):
        self.message = (top, bottom)
        self.message_until = self.clock() + seconds
        self._set_rows(top, bottom)

    def message_active(self):
        if self.message is None:
            return False
        if self.clock() >= self.message_until:
            self.message = None
            return False
        return True

    def set_default(self, top, bottom):
        """Default rows shown whenever no temporary message is up."""
        if self.message_active():
            return
        self._set_rows(top, bottom)

    def _set_rows(self, top, bottom):
        for row, text in ((0, top), (1, bottom)):
            shown = p.display_text(text)
            if self.rows[row] != shown:
                host.send_sysex(p.set_default_display(row, text))
                self.rows[row] = shown

    def set_label(self, control, index, name, value):
        for part, text in (("name", name), ("value", value)):
            key = (control, index, part)
            shown = p.display_text(text)
            if self.labels.get(key) == shown:
                continue
            self.labels[key] = shown
            if control == "pot":
                msg = p.set_pot_name(index, text) if part == "name" else p.set_pot_value(index, text)
            else:
                msg = p.set_fader_name(index, text) if part == "name" else p.set_fader_value(index, text)
            host.send_sysex(msg)

    def clear(self):
        host.send_sysex(p.clear_default_display())
        self.forget()
