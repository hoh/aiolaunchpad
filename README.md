# AioLaunchpad
Framework to control [Novation Launch](https://global.novationmusic.com/launch) controllers from Python with AsyncIO.

The goal of [aiolaunchpad](https://github.com/hoh/aiolaunchpad) is to make it very easy to handle concurrent actions and interface with other asynchronous tools, especially based on [Asyncio](https://docs.python.org/3/library/asyncio.html).

Supports the [Launch Control XL MK2](https://global.novationmusic.com/launch) at the moment, but support for other boards should be pretty straightforward.


## Usage

A basic usage of AioLaunchpad looks like the following:

```python
from aiolaunchpad import LaunchControlXL

pad = LaunchControlXL()

@pad.register
async def print_fader_0(code, input: pad.inputs.fader0, value, device):
    print("Hello, fader 0 has value", value)

@pad.register
async def print_all_faders(code, input, value, device):
    print("Any fader prints this")

if __name__ == '__main__':
    pad.run_app()
```

AioLaunchpad uses a simplified subscriber system, based on [Type Hints](https://docs.python.org/3/library/typing.html), to call your function only when the values match.

Have a look at the [examples](../examples).

## Requirements

A UNIX-style system is required to talk with the MIDI device natively, and [aiofiles](https://pypi.org/project/aiofiles/) must be installed (`pip install aiofiles`).
