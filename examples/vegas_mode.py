from asyncio import sleep
from random import randrange
from aiolaunchpad import LaunchControlXL, spin, set_color


pad = LaunchControlXL()


async def clear_leds(device, color, dt=0.05):
    """Animate the change of all knobs and button lights to a new color"""
    lights = pad.lights.knobs() + pad.lights.buttons()
    for light in lights:
        await set_color(color, light, device)
        await sleep(dt)


@pad.register
async def play_with_leds(code: pad.inputs.released,
                         input: pad.inputs.button0,
                         value, device):
    """Function registered to handle button 0 pressed."""
    spin(
        clear_leds(device, randrange(120), 0.02)
    )


if __name__ == '__main__':
    pad.run_app()
