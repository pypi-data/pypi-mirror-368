# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.
import os
import sys

from siliconcompiler import Chip
from siliconcompiler import SiliconCompilerError
from siliconcompiler.utils import get_default_iomap
from siliconcompiler.targets import skywater130_demo
from siliconcompiler.apps._common import UNSET_DESIGN


def _infer_designname(chip):
    topfile = None
    sourcesets = list(chip.getkeys('input'))
    for sourceset in reversed(('rtl', 'hll')):
        if sourceset in sourcesets:
            sourcesets.remove(sourceset)
            sourcesets.insert(0, sourceset)
    for sourceset in sourcesets:
        for filetype in chip.getkeys('input', sourceset):
            all_vals = chip.get('input', sourceset, filetype, field=None).getvalues()
            if all_vals:
                # just look at first value
                sources, _, _ = all_vals[0]
                # grab first source
                topfile = sources[0]
                break
        if topfile:
            break

    if not topfile:
        return None

    root = os.path.basename(topfile)
    while True:
        root, ext = os.path.splitext(root)
        if not ext:
            break

    return root


###########################
def main():
    progname = "sc"
    description = """
    ------------------------------------------------------------
    SiliconCompiler is an open source compiler framework that
    aims to enable automated translation from source code to
    silicon.

    The sc program includes the following steps.

    1. Read command line arguments
    2. If not set, 'design' is set to base of first source file.
    3. If not set, 'target' is set to 'skywater130_demo'.
    4. Run compilation
    5. Display summary

    Sources: https://github.com/siliconcompiler/siliconcompiler
    ------------------------------------------------------------
    """

    # Create a base chip class.
    chip = Chip(UNSET_DESIGN)

    # Read command-line inputs and generate Chip objects to run the flow on.
    try:
        args = chip.create_cmdline(progname,
                                   description=description,
                                   input_map=get_default_iomap())
    except SiliconCompilerError:
        return 1
    except Exception as e:
        chip.logger.error(e)
        return 1

    # Set design if none specified
    if chip.get('design') == UNSET_DESIGN:
        topmodule = _infer_designname(chip)

        if not topmodule:
            chip.logger.error('Invalid arguments: either specify -design or provide sources.')
            return 1

        chip.set('design', topmodule)

    # Set demo target if none specified
    if 'target' not in args or not args['target']:
        chip.use(skywater130_demo)

    try:
        # Run flow
        chip.run(raise_exception=True)

        # Print Job Summary
        chip.summary()
        chip.snapshot()
    except SiliconCompilerError:
        return 1
    except Exception as e:
        chip.logger.error(e)
        return 1

    return 0


#########################
if __name__ == "__main__":
    sys.exit(main())
