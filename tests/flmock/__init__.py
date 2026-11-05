"""Mock of the FL Studio MIDI scripting API modules (device, transport, mixer, channels, ...) for unit tests.

``tests/conftest.py`` puts this directory on ``sys.path`` so ``import mixer`` etc. resolve here, exactly like the
script resolves them inside FL Studio.
"""
