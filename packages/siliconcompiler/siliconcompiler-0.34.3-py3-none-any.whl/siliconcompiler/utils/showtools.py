from siliconcompiler.tools.klayout import show as klayout_show
from siliconcompiler.tools.klayout import screenshot as klayout_screenshot
from siliconcompiler.tools.openroad import show as openroad_show
from siliconcompiler.tools.openroad import screenshot as openroad_screenshot
from siliconcompiler.tools.vpr import show as vpr_show
from siliconcompiler.tools.vpr import screenshot as vpr_screenshot
from siliconcompiler.tools.yosys import screenshot as yosys_screenshot
from siliconcompiler.tools.gtkwave import show as gtkwave_show
from siliconcompiler.tools.surfer import show as surfer_show
from siliconcompiler.tools.graphviz import show as graphviz_show
from siliconcompiler.tools.graphviz import screenshot as graphviz_screenshot
from shutil import which


def setup(chip):
    chip.register_showtool('gds', klayout_show)
    chip.register_showtool('gds', klayout_screenshot)
    chip.register_showtool('oas', klayout_show)
    chip.register_showtool('oas', klayout_screenshot)
    chip.register_showtool('lef', klayout_show)
    chip.register_showtool('lef', klayout_screenshot)
    chip.register_showtool('lyrdb', klayout_show)
    chip.register_showtool('ascii', klayout_show)

    chip.register_showtool('odb', openroad_show)
    chip.register_showtool('odb', openroad_screenshot)
    chip.register_showtool('def', openroad_show)
    chip.register_showtool('def', openroad_screenshot)

    chip.register_showtool('route', vpr_show)
    chip.register_showtool('route', vpr_screenshot)
    chip.register_showtool('place', vpr_show)
    chip.register_showtool('place', vpr_screenshot)

    chip.register_showtool('v', yosys_screenshot)
    chip.register_showtool('vg', yosys_screenshot)

    if which('surfer') is not None:
        chip.register_showtool('vcd', surfer_show)
    else:
        chip.register_showtool('vcd', gtkwave_show)

    chip.register_showtool('dot', graphviz_show)
    chip.register_showtool('dot', graphviz_screenshot)
    chip.register_showtool('xdot', graphviz_show)
    chip.register_showtool('xdot', graphviz_screenshot)


def showtasks():
    from siliconcompiler import ShowTaskSchema, ScreenshotTaskSchema

    from siliconcompiler.tools.openroad.show import ShowTask as OpenROADShow
    from siliconcompiler.tools.openroad.screenshot import ScreenshotTask as OpenROADScreenshot

    ShowTaskSchema.register_task(OpenROADShow)
    ScreenshotTaskSchema.register_task(OpenROADScreenshot)
