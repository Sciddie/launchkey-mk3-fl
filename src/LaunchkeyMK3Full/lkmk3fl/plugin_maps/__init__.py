"""Curated Device-mode pages for specific plugins.

A plugin map is plain data (see ``vital.py``)::

    MAP = {
        "name": "Vital",                 # shown on the screen
        "match": ("vital",),             # lower-case substrings of the plugin's name that select this map
        "pages": [
            {"name": "Macros",           # page title on the screen (keep it short: the row has 16 characters)
             "pots": [(label, (candidate parameter names, ...)), ...],     # up to 8 entries, None = unused
             "faders": [...]},                                             # up to 8 entries (49 / 61 / 88)
        ],
    }

Parameters are looked up by *name* at runtime (exact match after normalising case, spaces and punctuation, then by
prefix), never by index, because the order a plugin reports its parameters in can differ between plugin versions and
formats. Slots whose parameter is not found stay empty; pages without any found parameter are dropped. To support
another plugin, add a module with a ``MAP`` and list it in ``MAPS`` below.

The module is called ``plugin_maps`` (not ``plugins``) so it is never confused with FL Studio's ``plugins`` module.
"""

from lkmk3fl.plugin_maps import vital

MAPS = (vital.MAP,)

SLOTS = 16  # pots 1-8, then faders 1-8


def find_map(*plugin_names):
    """The map for a plugin whose (original or user) name contains one of a map's ``match`` strings, else None."""
    for name in plugin_names:
        lowered = (name or "").lower()
        if not lowered:
            continue
        for m in MAPS:
            if any(s in lowered for s in m["match"]):
                return m
    return None


def normalise(name):
    return "".join(c for c in (name or "").lower() if c.isalnum())


class Page:
    __slots__ = ("name", "slots")

    def __init__(self, name, slots):
        self.name = name
        self.slots = slots  # SLOTS entries: (param index, label) or None

    def found(self):
        return sum(1 for s in self.slots if s is not None)


def resolve(plugin_map, param_names):
    """Turns a map into pages of parameter indices for a plugin reporting ``param_names`` (index -> name)."""
    exact = {}
    normalised = []
    for index, name in enumerate(param_names):
        n = normalise(name)
        normalised.append(n)
        if n and n not in exact:
            exact[n] = index

    def lookup(candidates):
        keys = [normalise(c) for c in candidates]
        for k in keys:
            if k in exact:
                return exact[k]
        for k in keys:  # hosts may append units or truncate: accept a prefix match either way
            if not k:
                continue
            for index, n in enumerate(normalised):
                if n and (n.startswith(k) or (len(n) >= 8 and k.startswith(n))):
                    return index
        return None

    pages = []
    for page in plugin_map["pages"]:
        entries = list(page.get("pots", ()))[:8]
        entries += [None] * (8 - len(entries))
        faders = list(page.get("faders", ()))[:8]
        entries += faders + [None] * (8 - len(faders))
        slots = []
        used = set()
        for entry in entries:
            if entry is None:
                slots.append(None)
                continue
            label, candidates = entry
            index = lookup(candidates)
            if index is None or index in used:
                slots.append(None)
            else:
                used.add(index)
                slots.append((index, label))
        resolved = Page(page["name"], slots)
        if resolved.found():
            pages.append(resolved)
    return pages
