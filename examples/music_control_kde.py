from subprocess import check_output
from aiolaunchpad import LaunchControlXL


pad = LaunchControlXL()


def set_volume(value):
    """Change the volume on a KDE Desktop (Linux or similar)"""
    value = min(100, value)
    check_output(["/usr/bin/amixer", "sset", "'Master'", "{}%".format(value)])


@pad.register
async def handle_volume(code, input: pad.inputs.fader0, value, device):
    set_volume(value)


if __name__ == '__main__':
    pad.run_app()