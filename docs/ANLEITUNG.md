# Anleitung: Launchkey MK3 (Full) in FL Studio

Kurzanleitung für das Skript **Novation Launchkey MK3 (Full)** (ab Version 0.3.0), geschrieben für das
**Launchkey MK3 49**. Auf 61 / 88 gilt alles genauso; 25 / 37 haben keine Fader und Fader-Tasten (dafür gibt es die
Mixer-Pad-Ebene).

**Shift** ist eine Umschalttaste: gedrückt halten und dann die andere Taste drücken.

## 1. Einrichtung (kurz)

1. **Easy Start ausschalten** (einmalig): Im Easy-Start-Modus meldet sich das Launchkey als USB-Laufwerk und der
   DAW-Port funktioniert nicht. Ausschalten laut Novation-Anleitung (Einstellungen am Gerät oder Novation Components).
2. Ordner `LaunchkeyMK3Full` nach `Dokumente/Image-Line/FL Studio/Settings/Hardware/` kopieren.
3. FL Studio: *Options > MIDI settings* (F10):
   - **Input** `MIDIIN2 (LKMK3 MIDI)` (macOS: `... LKMK3 DAW In`): aktivieren, *Controller type*
     **Novation Launchkey MK3 (Full)**, *Port* z. B. `10`.
   - **Output** `MIDIOUT2 (LKMK3 MIDI)` (macOS: `... LKMK3 DAW Out`): **dieselbe Port-Nummer** (`10`). Ohne das
     gibt es keine LEDs und keine Display-Texte.
   - **Input** `LKMK3 MIDI` (die Tastatur): aktivieren als **(generic controller)**. Tasten, Räder, Sustain und
     Drum-Pads spielen dann den ausgewählten Kanal.
   - Falls FL Studio dem DAW-Port das eingebaute *Novation Launchkey MK3*-Skript zugewiesen hat: durch dieses ersetzen.
4. Beim Start zeigt das Display `FL Studio` / `LK MK3 Full 0.3.0`.

## 2. Transport und Bearbeiten

| Taste | Drücken | Shift + Drücken |
|---|---|---|
| ▶ **Play** | Abspielen / Pause | Stopp und von vorne abspielen |
| ■ **Stop** | Stopp | Stopp und an den Anfang springen |
| ● **Record** | Aufnahme an / aus | Step-Edit an / aus |
| ⟲ **Loop** | Pattern- ⇄ Song-Modus | Loop-Aufnahme an / aus |
| **Click** | Metronom an / aus | Vorzähler (Count-in) an / aus |
| **Undo** | Rückgängig | Wiederherstellen (Redo) |
| **Capture MIDI** | Die zuletzt gespielten Noten (letzte 30 s) ins ausgewählte Pattern schreiben | Dieses Noten-Gedächtnis (Score Log) leeren |
| **Quantise** | Ausgewählten Kanal quantisieren (nur Notenanfänge) | Anfänge **und** Längen quantisieren |

Jede Taste zeigt ihr Ergebnis 1,5 s auf dem Display (z. B. `Metronome` / `On`) und in FL Studios Hinweiszeile.
Play, Stop, Record, Loop, Click, Undo, Capture MIDI und Quantise haben am MK3 keine LEDs.

## 3. Mixer

Die Pots und Fader steuern eine **Bank aus 8 Mixer-Spuren** (Start: Insert 1–8).

| Bedienelement | Funktion |
|---|---|
| **Track ◀ / ▶** | Vorherige / nächste Mixer-Spur auswählen (Master … Insert 125); die Bank wandert mit. LEDs: leuchten, wenn es in diese Richtung weitergeht |
| **Shift + Track ◀ / ▶** | Bank um 8 Spuren verschieben (Display: `Tracks 9-16`) |
| **Fader 1–8** | Je nach Fader-Modus (siehe unten) |
| **Master-Fader** (9.) | Immer Master-Lautstärke, in jedem Fader-Modus |
| **Fader-Tasten 1–8** | Mute (Standard) / Solo / Select der Bank-Spuren, im Arm-Modus Aufnahme-Scharfschalten |
| **Shift + Fader-Taste** | Diese Spur auswählen |
| **Arm / Select** | Fader-Tasten zwischen Arm und Mute/Solo/Select umschalten (LED hell = Arm) |
| **Stop/Solo/Mute** (rechts unter den Pads) | Funktion der Fader-Tasten weiterschalten: Mute → Solo → Select (Shift: rückwärts); schaltet Arm aus |

LED-Farben der Fader-Tasten:

- **Mute:** Spurfarbe = hörbar, aus = stumm
- **Solo:** blau pulsierend = Solo, sonst gedimmte Spurfarbe
- **Select:** weiß = ausgewählte Spur
- **Arm:** rot = scharf, dunkelrot = nicht scharf

Die LED von **Stop/Solo/Mute** zeigt die aktuelle Funktion: orange = Mute, blau = Solo, weiß = Select, rot = Arm.

### Pot- und Fader-Modi

Die Modi wählst du **am Keyboard** (siehe Novation-Bedienungsanleitung); das Skript folgt automatisch und zeigt den
Modus kurz an (`Pots: Volume`).

| Modus | Pots 1–8 | Fader 1–8 |
|---|---|---|
| **Pan** (Pot-Standard) | Panorama der 8 Spuren (Mittelstellung rastet bei 63/64 auf „C“) | – |
| **Volume** (Fader-Standard) | Lautstärke der 8 Spuren | Lautstärke der 8 Spuren |
| **Send A** | Send-Pegel von jeder Spur zu Insert 124 | wie Pots |
| **Send B** | Send-Pegel von jeder Spur zu Insert 125 | wie Pots |
| **Device** | Plugin-Parameter 1–8 der aktuellen Seite (Abschnitt 6) | Plugin-Parameter 9–16 der Seite |

Sends bewegen nur **vorhandene** Routings (sonst zeigt das Display `no send`) und brauchen FL Studio 21.2 oder neuer.

**Soft Takeover:** Ein Pot / Fader übernimmt einen Wert erst, wenn er ihn erreicht (oder überquert). Bis dahin zeigt
das Display die Richtung: `> 50%` = weiter nach rechts / oben, `50% <` = nach links / unten. So springt beim
Bank-, Seiten- oder Plugin-Wechsel nichts.

## 4. Pads: die vier Ebenen

**► Scene Launch** (rechts neben der oberen Pad-Reihe) schaltet die Pad-Ebene weiter:
**Steps → Patterns → Channels → Mixer** (Shift + Scene Launch: rückwärts). Die LED zeigt die Ebene. Waren die Pads im
Drum-Layout, holt Scene Launch sie zurück in das Session-Layout, in dem diese Ebenen leben.

Die Tasten **Scene ▲ / ▼** (links neben den Pads) navigieren je nach Ebene; ihre LEDs leuchten, wenn es in diese
Richtung weitergeht.

### Steps (LED orange) – Step-Sequencer

Die 16 Pads sind die Steps 1–16 des **ausgewählten Kanals** im aktuellen Pattern.

- **Pad:** Step an / aus.
- **Shift + Pad *n*:** zur Step-Seite *n* springen (bei Patterns länger als 16 Steps).
- **Scene ▲ / ▼:** vorheriger / nächster Kanal.
- **Shift + Scene ▲ / ▼:** vorherige / nächste Step-Seite.

Farben:

| Zustand | Farbe |
|---|---|
| Step gesetzt | Kanalfarbe (bei grauen/weißen Kanälen weiß) |
| Step leer | aus; jeder 4. Step (Zählzeit) gedimmt weiß |
| Abspielposition auf **gesetztem** Step | **weiß** (bei weißen/grauen Kanälen **gelb**) |
| Abspielposition auf **leerem** Step | **blau** |
| hinter dem Pattern-Ende | aus |

Die Abspielposition läuft nur im **Pattern-Modus** während der Wiedergabe mit und blättert die Step-Seiten
automatisch mit. Die Farben lassen sich in `lkmk3fl/config.py` ändern (`PLAYHEAD_SET_COLOUR`,
`PLAYHEAD_SET_ALT_COLOUR`, `PLAYHEAD_EMPTY_COLOUR`).

### Patterns (LED türkis)

- **Pad:** Pattern auswählen. Das aktuelle Pattern pulsiert in seiner Farbe, andere sind gedimmt; das
  **gedimmt grüne** Pad hinter dem letzten Pattern legt ein **neues** Pattern an.
- **Scene ▲ / ▼:** vorheriges / nächstes Pattern.
- **Shift + Scene ▲ / ▼:** vorherige / nächste Seite mit 16 Patterns.

### Channels (LED grün)

- **Pad:** Kanal auswählen (ausgewählter Kanal pulsiert, andere in gedimmter Kanalfarbe).
- **Shift + Pad:** Kanal stumm / laut (stumm = dunkelrot).
- **Scene ▲ / ▼:** vorherige / nächste Seite mit 16 Kanälen.
- **Shift + Scene ▲ / ▼:** vorheriger / nächster Kanal.

### Mixer (LED magenta)

- **Obere Reihe:** die 8 Bank-Spuren auswählen (ausgewählte = weiß).
- **Untere Reihe:** Mute (Spurfarbe = hörbar, aus = stumm); **Shift + Pad:** Solo (blau pulsierend).
- **Scene ▲ / ▼:** Bank um 8 Spuren verschieben.
- **Shift + Scene ▲ / ▼:** vorherige / nächste Mixer-Spur.

## 5. Drum-Modus

Das Drum-Layout der Pads wählst du am Keyboard. Die Pads spielen die Noten 36–51 auf dem **ausgewählten Kanal**
(passt zum Standard-Layout von FPC) und werden ganz normal aufgenommen. Mit einem FPC auf dem ausgewählten Kanal
leuchten die Pads in den FPC-Pad-Farben, sonst gedimmt in der Kanalfarbe; gedrückte Pads leuchten weiß.

## 6. Device-Modus (Plugins steuern)

Im **Device**-Pot-Modus steuern die Pots die Parameter des „Devices“. Das Device ist, in dieser Reihenfolge:

1. das **gesperrte** Plugin (Device Lock),
2. sonst das **fokussierte Plugin-Fenster** (Instrument oder Mixer-Effekt),
3. sonst das per Device Select + Pad **gewählte** Plugin,
4. sonst das Instrument des **ausgewählten Kanals**.

- Es zählen nur Parameter mit Namen; je **8 pro Seite**. Sind auch die Fader im Device-Modus, hat eine Seite
  16 Parameter (Pots 1–8, Fader 9–16).
- **Track ◀ / ▶:** vorherige / nächste Parameter-Seite (Display `Page 2/5`; die LEDs zeigen, ob es weitergeht).
  **Shift + Track ◀ / ▶** verschiebt weiterhin die Mixer-Bank.
- Display: Zeile 1 = Plugin-Name, Zeile 2 = `Dev 2/5` (bzw. `Dev 2/5 LOCK`); beim Drehen Parametername und Wert.

| Taste | Funktion |
|---|---|
| **Device Select** kurz drücken | Plugin-Fenster des Devices öffnen (Instrument: öffnen / schließen; Mixer-Effekt: öffnen bzw. in den Vordergrund holen) |
| **Device Select** halten | Pads werden zur Device-Auswahl: **obere Reihe** = die 8 Kanäle um den ausgewählten (Pad wählt den Kanal und sein Instrument), **untere Reihe** = Effekt-Slots 1–8 der ausgewählten Mixer-Spur (belegt = türkis; Pad öffnet den Effekt und macht ihn zum Device). Das aktuelle Device pulsiert. Loslassen: Pads wie vorher |
| **Shift + Device Select** | Pots zwischen Device-Modus und dem vorherigen Pot-Modus umschalten |
| **Device Lock** | Aktuelles Device sperren / entsperren (LED hell = gesperrt). Gesperrt bleiben die Pots auf diesem Plugin, auch wenn du ein anderes Fenster anklickst |

Die LED von **Device Select** ist hell, wenn es ein Device gibt.

### Vital

Ist das Device **Vital** (erkannt am Plugin-Namen, auch wenn du es umbenannt hast), beginnt der Device-Modus mit fünf
festen Seiten. **Track ◀ / ▶** blättert durch diese Seiten und danach weiter durch die normalen Seiten mit allen
benannten Parametern. Das Display zeigt die Seite (z. B. `Dev 1/11 Macros`, beim Blättern `2/11 Osc`) und beim Drehen
Parametername und Wert. Die Pots steuern die erste Spalte, die Fader (nur im Fader-Modus **Device**) die zweite:

| Seite | Pots 1–8 | Fader 1–8 (Fader-Modus Device) |
|---|---|---|
| **Macros** | Macro 1, Macro 2, Macro 3, Macro 4, Filter 1 Cutoff, Filter 1 Resonance, Reverb Mix, Volume | Osc 1 / 2 / 3 Level, Sub Level, Sample Level, Delay Mix, Chorus Mix, Distortion Mix |
| **Osc** | Osc 1 / 2 / 3 Wave Frame, Osc 1 / 2 / 3 Transpose, Osc 1 Unison Voices, Osc 1 Unison Detune | Osc 1 / 2 / 3 Level, Osc 1 / 2 / 3 Tune, Osc 2 / 3 Unison Detune |
| **Filter** | Filter 1 Cutoff, Resonance, Drive, Mix; Filter 2 Cutoff, Resonance, Drive, Mix | Filter 1 / 2 Key Track, Filter 1 / 2 Blend, Distortion Drive, Distortion Mix, EQ Low Gain, EQ High Gain |
| **Env** | Hüllkurve 1 Attack, Decay, Sustain, Release; Hüllkurve 2 Attack, Decay, Sustain, Release | Hüllkurve 3 Attack, Decay, Sustain, Release; LFO 1 / 2 Frequency, Portamento (Glide), Velocity Track |
| **FX** | Reverb Mix, Size, Decay; Delay Mix, Feedback; Chorus Mix; Phaser Mix; Flanger Mix | Compressor Mix, EQ Low / Band / High Gain, Delay Frequency, Chorus Voices, Distortion Drive, Distortion Mix |

Die Parameter werden beim Fokussieren **über ihren Namen** gesucht, nicht über ihre Position. Wird ein Name nicht
gefunden, bleibt der Regler leer (`-`). Abschalten: `CURATED_PLUGIN_PAGES = False` in `lkmk3fl/config.py`.

## 7. Display

| Anzeige | Inhalt |
|---|---|
| Zeile 1 | Steps / Channels: ausgewählter Kanal · Patterns: aktuelles Pattern · Mixer: ausgewählte Mixer-Spur · Device-Modus: Plugin-Name |
| Zeile 2 | Ebene + Seite und Transport (im Device-Modus `Dev 2/5` bzw. bei Vital `Dev 1/11 Macros`), z. B. `S1-16 PLAY PAT C`: `S`/`P`/`C`/`M` = Steps/Patterns/Channels/Mixer, `PLAY`/`STOP`/`REC` (`ARM` = Aufnahme an, aber gestoppt), `PAT`/`SONG`, `C` = Metronom an |
| Pot-/Fader-Anzeige | Name und Wert des bewegten Reglers: Spurname mit dB / Pan (`L37`, `C`, `R12`) / Send-%, oder Parametername und -wert |
| Meldungen | Ergebnis jedes Tastendrucks für 1,5 s |

## 8. Was das Keyboard selbst macht

Tasten, Pitch- und Mod-Rad, Sustain, Octave − / +, Arp, Scale und Fixed Chord arbeitet das Launchkey selbst ab; die
Noten kommen über den Tastatur-Port (`LKMK3 MIDI`) in FL Studio an. Die Custom-Modi der Pads, Pots und Fader bleiben
ebenfalls beim Keyboard.

## 9. Einstellungen

In `LaunchkeyMK3Full/lkmk3fl/config.py` (danach *Update MIDI scripts* in den MIDI-Einstellungen): Modell erzwingen,
Soft Takeover, Start-Modi, Send-Ziele, Anzeigedauer, Capture-Länge, Quantise-Variante, Abspielpositions-Farben,
Start-Pad-Ebene, Hinweiszeile, feste Plugin-Seiten (Vital). Die Bedeutung jeder Option steht in der Datei und im README.
