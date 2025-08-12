from siliconcompiler.tools.verilator.verilator import setup as setup_tool
from siliconcompiler.tools.verilator.verilator import runtime_options as runtime_options_tool
from siliconcompiler.tools._common import get_input_files, get_tool_task


def setup(chip):
    '''
    Compiles Verilog and C/C++ sources into an executable. In addition to the
    standard RTL inputs, this task reads C/C++ sources from :keypath:`input,
    hll, c`.  Outputs an executable in ``outputs/<design>.vexe``.
    '''

    # Generic tool setup.
    setup_tool(chip)

    tool = 'verilator'
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    _, task = get_tool_task(chip, step, index)

    design = chip.top()

    chip.add('tool', tool, 'task', task, 'require', 'input,hll,c', step=step, index=index)
    chip.set('tool', tool, 'task', task, 'output', f'{design}.vexe', step=step, index=index)

    # var defaults
    chip.set('tool', tool, 'task', task, 'var', 'mode', 'cc', clobber=False, step=step, index=index)
    chip.set('tool', tool, 'task', task, 'var', 'trace', False, clobber=False,
             step=step, index=index)
    chip.set('tool', tool, 'task', task, 'var', 'trace_type', 'vcd', clobber=False,
             step=step, index=index)

    mode = chip.get('tool', tool, 'task', task, 'var', 'mode', step=step, index=index)
    if mode not in (['cc'], ['systemc']):
        chip.error(f"Invalid mode {mode} provided to verilator/compile. Expected one of 'cc' or "
                   "'systemc'")
    chip.add('tool', tool, 'task', task, 'require',
             ','.join(['tool', tool, 'task', task, 'var', 'mode']),
             step=step, index=index)

    trace_type = chip.get('tool', tool, 'task', task, 'var', 'trace_type', step=step, index=index)
    if trace_type not in (['vcd'], ['fst']):
        chip.error(f"Invalid trace type {trace_type} provided to verilator/compile. Expected "
                   "one of 'vcd' or 'fst'.")
    chip.add('tool', tool, 'task', task, 'require',
             ','.join(['tool', tool, 'task', task, 'var', 'trace_type']),
             step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'cflags',
             'flags to provide to the C++ compiler invoked by Verilator',
             field='help')
    if chip.get('tool', tool, 'task', task, 'var', 'cflags', step=step, index=index):
        chip.add('tool', tool, 'task', task, 'require',
                 ','.join(['tool', tool, 'task', task, 'var', 'cflags']),
                 step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'ldflags',
             'flags to provide to the linker invoked by Verilator',
             field='help')
    if chip.get('tool', tool, 'task', task, 'var', 'ldflags', step=step, index=index):
        chip.add('tool', tool, 'task', task, 'require',
                 ','.join(['tool', tool, 'task', task, 'var', 'ldflags']),
                 step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'pins_bv',
             'controls datatypes used to represent SystemC inputs/outputs. See --pins-bv in '
             'Verilator docs for more info.',
             field='help')
    if chip.get('tool', tool, 'task', task, 'var', 'pins_bv', step=step, index=index):
        chip.add('tool', tool, 'task', task, 'require',
                 ','.join(['tool', tool, 'task', task, 'var', 'pins_bv']),
                 step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'mode',
             "defines compilation mode for Verilator. Valid options are 'cc' for C++, or 'systemc' "
             "for SystemC.",
             field='help')

    chip.set('tool', tool, 'task', task, 'dir', 'cincludes',
             'include directories to provide to the C++ compiler invoked by Verilator',
             field='help')
    if chip.get('tool', tool, 'task', task, 'dir', 'cincludes', step=step, index=index):
        chip.add('tool', tool, 'task', task, 'require',
                 ','.join(['tool', tool, 'task', task, 'dir', 'cincludes']),
                 step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'trace',
             "if true, enables trace generation.",
             field='help')
    if chip.get('tool', tool, 'task', task, 'var', 'trace', step=step, index=index):
        chip.add('tool', tool, 'task', task, 'require',
                 ','.join(['tool', tool, 'task', task, 'var', 'trace']),
                 step=step, index=index)

    chip.set('tool', tool, 'task', task, 'var', 'trace_type',
             "specifies type of wave file to create when [trace] is set. Valid options are "
             "'vcd' or 'fst'. Defaults to 'vcd'.",
             field='help')

    chip.set('tool', tool, 'task', task, 'var', 'initialize_random',
             'true/false, when true registers will reset with a random value.',
             field='help')
    chip.set('tool', tool, 'task', task, 'var', 'initialize_random', False,
             step=step, index=index, clobber=False)


def runtime_options(chip):
    tool = 'verilator'
    step = chip.get('arg', 'step')
    index = chip.get('arg', 'index')
    _, task = get_tool_task(chip, step, index)
    design = chip.top()

    cmdlist = runtime_options_tool(chip)

    random_init = chip.get('tool', tool, 'task', task, 'var',
                           'initialize_random', step=step, index=index)
    if random_init == ['true']:
        cmdlist.extend(['--x-assign', 'unique'])

    cmdlist.extend(['--exe', '--build'])

    threads = chip.get('tool', tool, 'task', task, 'threads', step=step, index=index)
    cmdlist.extend(['-j', str(threads)])

    mode = chip.get('tool', tool, 'task', task, 'var', 'mode', step=step, index=index)
    if mode == ['cc']:
        cmdlist.append('--cc')
    elif mode == ['systemc']:
        cmdlist.append('--sc')

    pins_bv = chip.get('tool', tool, 'task', task, 'var', 'pins_bv', step=step, index=index)
    if pins_bv:
        cmdlist.extend(['--pins-bv', pins_bv[0]])

    cmdlist.extend(['-o', f'../outputs/{design}.vexe'])

    c_flags = chip.get('tool', tool, 'task', task, 'var', 'cflags', step=step, index=index)
    c_includes = chip.find_files('tool', tool, 'task', task, 'dir', 'cincludes',
                                 step=step, index=index)

    if chip.get('tool', tool, 'task', task, 'var', 'trace', step=step, index=index)[0] == 'true':
        trace_type = chip.get('tool', tool, 'task', task, 'var', 'trace_type',
                              step=step, index=index)

        if trace_type == ['vcd']:
            ext = 'vcd'
            trace_opt = '--trace'
        elif trace_type == ['fst']:
            ext = 'fst'
            trace_opt = '--trace-fst'

        cmdlist.append(trace_opt)

        # add siliconcompiler specific defines
        c_flags.append("-DSILICONCOMPILER_TRACE_DIR=\\\"reports\\\"")
        c_flags.append(f"-DSILICONCOMPILER_TRACE_FILE=\\\"reports/{design}.{ext}\\\"")

    if c_includes:
        c_flags.extend([f'-I{include}' for include in c_includes])

    if c_flags:
        cflags_str = ' '.join(c_flags)
        cmdlist.extend(['-CFLAGS', cflags_str])

    ld_flags = chip.get('tool', tool, 'task', task, 'var', 'ldflags', step=step, index=index)
    if ld_flags:
        ldflags_str = ' '.join(ld_flags)
        cmdlist.extend(['-LDFLAGS', ldflags_str])

    for value in get_input_files(chip, 'input', 'hll', 'c'):
        cmdlist.append(value)

    return cmdlist
