#!/usr/bin/python
"""
A module to prepare header files for the simulated accelerators,
    execute them and retrieve the results.
"""

import os
import uuid
# import itertools
# import numpy as np

# A list of available accelerator parameters
_AVAILABLE_PARAMS = [
    'cycle_time',
    'pipelining',
    'cache_size',
    'cache_assoc',
    'cache_hit_latency',
    'cache_line_sz',
    'cache_queue_size',
    'cache_bandwith',
    'tlb_hit_latency',
    'tlb_miss_latency',
    'tlb_page_size',
    'tlb_entries',
    'tlb_max_outstanding_walks',
    'tlb_assoc',
    'tlb_bandwidth',
    'l2cache_size',
    'enable_l2',
    'pipelined_dma',
    'ready_mode from',
    'ignore_cache_flush'
]

def create_header_from_template(params, header_path, sim_output_dir, template_path='template.xe'):
    """Prepares a simulator input file based on a template.

    Reads in a provided template file, sets output directory and parameters for the accelerator,
        saves the resulting configuration as a header file in to header_path.

    Args:
        params: a dictionary with the parameters of the simulated accelerator
        header_name: full path where the simulator header
        sim_output_dir: full path to the directory where the results from the simulator should
            be saved
        template_path: full path to the template file

    """

    # Read in the template file
    with open(template_path, 'r') as src_file:
        out_src = src_file.read()

    # Setting the output directory for the simulator results
    out_src = out_src.replace('$OUTPUT_DIR', '{0}'.format(sim_output_dir))

    # Check which parameters match with available parameters and add those values to the header file
    params_src = ''
    for key in set(_AVAILABLE_PARAMS).intersection(params):
        params_src = '%s set %s %s\n' % (params_src, key, params[key])

    out_src = out_src.replace('# Insert here\n', params_src)

    # Writing the new header file
    with open(header_path, 'w') as ouput_file:
        ouput_file.write(out_src)

if __name__ == "__main__":

    # temporary parameters
    _PARAMS = {
        'cache_line_sz': 64,
        'cache_assoc': 8,
        'cache_queue_size': 64
    }

    _GEM5_BENCH_DIR_NAME = 'benchmarks'
    _GEM5_SWEEPS_DIR_NAME = 'sweeps'

    # get the paths to aladdin and its submodules
    _GEM5_PATH = os.path.join(os.environ['ALADDIN_HOME'], '..', '..')

    _GEM5_SWEEPS_PATH = os.path.join(_GEM5_PATH, _GEM5_SWEEPS_DIR_NAME)
    _GEM5_SWEEPS_BENCH_PATH = os.path.join(_GEM5_SWEEPS_PATH, _GEM5_BENCH_DIR_NAME)

    # template file
    _HEADER_FILE_NAME = str(uuid.uuid4())
    _HEADER_PATH = os.path.join(_GEM5_SWEEPS_BENCH_PATH, _HEADER_FILE_NAME)

    _SIM_OUTPUT_DIR = os.path.join(_GEM5_SWEEPS_PATH, 'tla_temp')

    # Preparing input input file for the simulator
    create_header_from_template(_PARAMS, _HEADER_PATH, _SIM_OUTPUT_DIR)

    # Generating design sweeps using the script provided with gem5
    # gem5 generate_design_sweeps.py needs to be executed in the `gem5-aladdin/sweeps` directory
    _CWD = os.getcwd()
    os.chdir(_GEM5_SWEEPS_PATH)

    # TODO: python2 needs to be python?
    os.system('python2 generate_design_sweeps.py %s' % (os.path.join(_GEM5_BENCH_DIR_NAME,
                                                                     _HEADER_FILE_NAME)))

    os.chdir(_CWD)

    # removing the temporary header file
    if os.path.exists(_HEADER_PATH):
        os.remove(_HEADER_PATH)


    # _HEADER_PATH

    # Executing the simulator

    # Gathering the results

    print('Finished.')
