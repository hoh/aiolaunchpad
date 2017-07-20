"""
AioLaunchpad is an Asyncio based framework to read and control the
Novation Launch MIDI controllers.
"""

import re
import asyncio
import aiofiles

# LEDs and inputs do not always have the same id mapping on the
# Launch Control XL MK2 (LCXL2). These numbers correspond to the
# User Template mode:
LCXL2_MAPPING = {
    'lights': {
        'knob':   [13, 29, 45, 61, 77, 93, 109, 125,
                   14, 30, 46, 62, 78, 94, 110, 126,
                   15, 31, 47, 63, 79, 95, 111, 127],

        'button': [41, 42, 43, 44, 57, 58, 59, 60,
                   73, 74, 75, 76, 89, 90, 91, 92],

        'control': [105, 106, 107, 108],
        'track_select': [106, 107],
        'send_select': [104, 105],
    },
    'inputs': {
        'knob':   [13, 14, 15, 16, 17, 18, 19, 20,
                   29, 30, 31, 32, 33, 34, 35, 36,
                   49, 50, 51, 52, 53, 54, 55, 56],

        'fader':  [77, 78, 79, 80, 81, 82, 83, 84],

        'button': [41, 42, 43, 44, 57, 58, 59, 60,
                   73, 74, 75, 76, 89, 90, 91, 92],

        'control': [105, 106, 107, 108],
        'track_select': [106, 107],
        'send_select': [104, 105],
    },
}


class Shortcut:
    def __init__(self, mapping: dict):
        self.mapping = mapping

    def __getattr__(self, item):
        """Support for pad.input.button0, etc"""
        match = re.match(r'(\w+)(\d+)', item)
        if match:
            name = match.group(1)
            index = int(match.group(2))
            return self.mapping[name][index]
        raise AttributeError()

    @property
    def all(self):
        for group in self.mapping.values():
            for id in group:
                yield id

    def knobs(self, row=None):
        ids = self.mapping['knob']
        if row is None:
            return self.mapping['knob']
        else:
            return ids[8 * row:8 * (row + 1)]

    def buttons(self, row=None):
        ids = self.mapping['button']
        if row is None:
            return self.mapping['button']
        else:
            return ids[8 * row:8 * (row + 1)]


class LightsShortcut(Shortcut):
    pass


class InputsShortcut(Shortcut):
    pressed = 144
    released = 128


# ---


def parse_midi(midi):
    """Convert a MIDI (3 bytes) to a dictionnary for ease of use."""
    return {
        'code': midi[0], 'input': midi[1], 'value': midi[2],
    }


def note_fits_annotations(note, annotations):
    """Return whether a note matches a function's annotations."""
    for ann in annotations:
        if note[ann] != annotations[ann]:
            return False
    return True


# --- Useful functions ---

async def set_color(color, light_id, device):
    """Set the color of a light given its id."""
    "Set the color of a light given its id."
    await device.write(bytes([0x90, light_id, color]))


def spin(task):
    """Run a task asynchronously in the event loop, shortcut"""
    return asyncio.get_event_loop().create_task(task)


# --- Launch boards ---


class LaunchBoard:

    def __init__(self, path='/dev/midi2'):
        self.path = path
        self.handlers = []

    async def setup(self, device):
        """Turn of all lights during setup"""
        for light in self.lights.all:
            await set_color(0, light, device)

    def register(self, handler):
        """Decorator"""
        annotations = handler.__annotations__

        async def subscriber(queue, device):
            while True:
                midi = await queue.get()
                note = parse_midi(midi)
                if note_fits_annotations(note, annotations):
                    await handler(**note, device=device)
        self.handlers.append(subscriber)
        return handler

    @staticmethod
    async def input_handler(device, queues):
        while True:
            midi = await device.read(3)
            for queue in queues:
                await queue.put(midi)

    async def run(self):
        queues = []
        async with aiofiles.open(self.path, 'wb+', buffering=0) as device:

            await self.setup(device)

            tasks = []

            for handler in self.handlers:
                queue = asyncio.Queue()

                queues.append(queue)
                tasks.append(handler(queue, device))

            await asyncio.gather(
                self.input_handler(device, queues),
                *tasks,
            )

    def run_app(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run())
        loop.close()


class LaunchControlXL(LaunchBoard):
    lights = LightsShortcut(LCXL2_MAPPING['lights'])
    inputs = InputsShortcut(LCXL2_MAPPING['inputs'])

    def __init__(self, path='/dev/midi2'):
        super().__init__(path)
