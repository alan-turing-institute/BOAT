#!/usr/bin/python
"""
A module to prepare header files for the simulated accelerators,
    execute them and retrieve the results.
"""

import argparse
import os
import re
import uuid
import shutil

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

_CONST_AREA = 'area'
_CONST_CYCLE = 'cycle'
_CONST_POWER = 'power'
_CONST_P1 = 'P1'
_CONST_P2 = 'P2'
_CONST_P3 = 'P3'
_CONST_P4 = 'P4'
_CONST_P5 = 'P5'

_CONST_TARGET_CHOICES_SIMULATOR = [_CONST_CYCLE, _CONST_POWER, _CONST_AREA]
_CONST_TARGET_CHOICES_TESTS = [_CONST_P1, _CONST_P2, _CONST_P3, _CONST_P4, _CONST_P5]
_CONST_TARGET_CHOICES = _CONST_TARGET_CHOICES_SIMULATOR + \
    _CONST_TARGET_CHOICES_TESTS

_CONST_C1 = 'C1'
_CONST_C2 = 'C2'

_TARGET_FUNC_COEF = {
    _CONST_P1: {_CONST_C1: 0.50, _CONST_C2: 0.50},
    _CONST_P2: {_CONST_C1: 0.25, _CONST_C2: 0.75},
    _CONST_P3: {_CONST_C1: 0.75, _CONST_C2: 0.25},
    _CONST_P4: {_CONST_C1: 0.99, _CONST_C2: 0.01},
    _CONST_P5: {_CONST_C1: 0.01, _CONST_C2: 0.99}}
    
### fft_transpose 1000 random search results
_CONST_MAX_AREA = 2515230
_CONST_MAX_CYCLE = 62966
_CONST_MAX_POWER = 225.118

# get the paths to aladdin, gem5 and other submodules
_GEM5_PATH = os.path.abspath(os.path.join(os.environ['ALADDIN_HOME'], '..', '..'))

_GEM5_BENCH_DIR_NAME = 'benchmarks'
_GEM5_SWEEPS_DIR_NAME = 'sweeps'
_GEM5_SWEEPS_DESIGN_PY = 'generate_design_sweeps.py'

_GEM5_SWEEPS_PATH = os.path.join(_GEM5_PATH, _GEM5_SWEEPS_DIR_NAME)
_GEM5_SWEEPS_DESIGN_PY_PATH = os.path.join(_GEM5_SWEEPS_PATH, _GEM5_SWEEPS_DESIGN_PY)
_GEM5_SWEEPS_BENCH_PATH = os.path.join(_GEM5_SWEEPS_PATH, _GEM5_BENCH_DIR_NAME)
_GEM5_MACHSUITE_PY = 'machsuite.py'

# Choosing the benchmark
_DEFAULT_BENCH = "fft_transpose"
_BENCH_OUT_PARTIAL_PATH = "0"
_BENCH_OUT_FILE = "outputs/stdout"

# Default constants
_DEFAULT_RESULT_FILE = "gem5_sim_res.txt"

def __create_header_from_template(params, header_path, sim_output_dir, template_path='template.xe'):
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

def __collect_result(results_file_path):
    """Collects results from a simululation run

    Args:
        results_file_path: full path to the simulation results file

    Returns:
        results: a dict mapping simulation results
    """

    results = {}

    cycle = [re.findall(r'Cycle : (.*) cycles', line) for line in open(results_file_path)]
    cycle = [c for l in cycle for c in l]
    cycle = int(cycle[0])

    results['cycle'] = cycle

    power = [re.findall(r'Avg Power: (.*) mW', line) for line in open(results_file_path)]
    power = [p for l in power for p in l]

    power = float(power[0])

    results['power'] = power

    area = [re.findall(r'Total Area: (.*) uM', line) for line in open(results_file_path)]
    area = [a for l in area for a in l]

    area = float(area[0])

    results['area'] = area
    
    return results

def __main(sim_params, sim_output_dir, bench_name=_DEFAULT_BENCH):
    """Collects results from a simululation run

    Args:
        sim_params: parameters for the simulator
        sim_output_dir: directory to save simulator's production runs
        bench_name: benchmark to be run with the simulator

    Returns:
        results: a dict mapping simulation results. For example:
          results = {'area': 1094960.0, 'power': 67.5946, 'cycle': 65029}
    """

    # template file
    header_file_name = str(uuid.uuid4())
    header_file_path = os.path.join(_GEM5_SWEEPS_BENCH_PATH, header_file_name)

    # Preparing input input file for the simulator
    __create_header_from_template(sim_params, header_file_path, sim_output_dir)

    # Generating design sweeps using the script provided with gem5
    # It seems that gem5 generate_design_sweeps.py needs to be executed in the `gem5-aladdin/sweeps` directory.
    # TODO: check above
    _CWD = os.getcwd()
    os.chdir(_GEM5_SWEEPS_PATH)

    # Preparating the benchmarks 
    # comment/uncomment required benchmarks
    machsuitepy_path = os.path.join(_GEM5_SWEEPS_BENCH_PATH, _GEM5_MACHSUITE_PY)
    __comment_uncomment(machsuitepy_path, bench_name)

    # TODO: python2 needs to be python?
    os.system('python2 %s %s' % (_GEM5_SWEEPS_DESIGN_PY_PATH, 
                                 os.path.join(_GEM5_BENCH_DIR_NAME, header_file_name)))

    os.chdir(_CWD)

    # removing the temporary header file
    if os.path.exists(header_file_path):
        os.remove(header_file_path)

    # Running the bechmark with the simulator
    bench_path = os.path.join(sim_output_dir, bench_name, _BENCH_OUT_PARTIAL_PATH)

    os.chdir(bench_path)

    # Performing the benchmark
    os.system('sh run.sh')
    os.chdir(_CWD)

    # Collecting the results from the simululation run
    results_file_path = os.path.join(bench_path, _BENCH_OUT_FILE)

    results = __collect_result(results_file_path)
    
    return results

def __get_target_value(results, target_type):
    """ Returns the value of a target function depending on the target_type

    Args:
        results: obtained results from the simulator
        target_type: a key value for the target function

    Returns:
        value: the value of the target function
    """

    if target_type in _CONST_TARGET_CHOICES_SIMULATOR:
        value = results[target_type]

    elif target_type in _CONST_TARGET_CHOICES_TESTS:
        
        area = results[_CONST_AREA]
        cycle = results[_CONST_CYCLE]
        power = results[_CONST_POWER]

        area_norm = area / _CONST_MAX_AREA
        cycle_norm = cycle / _CONST_MAX_CYCLE
        power_norm = power / _CONST_MAX_POWER

        c1 = _TARGET_FUNC_COEF[target_type][_CONST_C1]
        c2 = _TARGET_FUNC_COEF[target_type][_CONST_C2]

        value = c1 * (cycle_norm / area_norm) + c2 * (power_norm / area_norm)

    else:
        value = 0.0
        raise ValueError('Unrecognised target_type')

    return value 

def __find_first_last_lines(file_path, expr):
    """Reads a file and finds the first and the last lines when 
    expression occurs.
    Args:
        file_path: full path to the input file
        expr: expression searched
    Returns:
        first and last line numbers when the given expression occurs in the file
    """
    
    first = -1
    last = -1
    
    f = open(file_path, "r")
    
    line_cnt = 0
    for f_line in f:

        if expr in f_line:
            if first == -1:
                first = line_cnt
            else:
                last = line_cnt
        
        line_cnt += 1
    
    f.close()
    
    return first, last

def __comment_uncomment(file_path, expr):
    """Modifies file by commenting/uncommenting file lines with respect to given expression.
     Args:
        file_path: full path to the input file
        expr: expression searched
    """
    
    first, last = __find_first_last_lines(file_path, expr)

    unique_filename = str(uuid.uuid4())
    
    f = open(file_path, "r")
    f_w = open(unique_filename, "w")
    
    line_cnt = 0
    for f_line in f:
        
        # ignore first 5 lines
        if line_cnt > 4:
            # uncomment benchmark
            if ((line_cnt >= first) & (line_cnt <= last)):
                if f_line.startswith("#"):
                    new_line = f_line[1:].strip()
                else:
                    new_line = f_line.strip()  
            else:
                if len(f_line) > 0:
                    if not f_line.startswith("#"):
                        new_line = "# " + f_line.strip()
                    else:
                        new_line = f_line.strip()
                else:
                    new_line = ""            
        else:
            new_line = f_line.strip()
                
        f_w.write(new_line + "\n")
                
        line_cnt += 1
        
    f.close()
    f_w.close()
    
    shutil.move(unique_filename, file_path)

if __name__ == "__main__":

    # Setting up the argument parser
    parser = argparse.ArgumentParser(description='Run gem5-alladin benchmark')

    parser.add_argument('sim_params', type=str, 
                        help='Parameters for the simulator as a string representation of a Python dict')

    parser.add_argument('results_key', type=str, choices=_CONST_TARGET_CHOICES,
                        help='Targeted accelerator specification')

    parser.add_argument('--sim_name', type=str, default=None,
                        help='Name of the directory where simulator s production runs will be saved')

    parser.add_argument('--results_file', type=str, default=_DEFAULT_RESULT_FILE,
                        help='Filename to save the results.')
                         
    args = parser.parse_args()
    
    _PARAMS = eval(args.sim_params)

    # directory to save simulator's production runs
    if args.sim_name is not None:
        _SIM_SWEEP_NAME = args.sim_name.strip()
    else:
        _SIM_SWEEP_NAME = "{}{}".format("sim_", str(uuid.uuid4()))

    _SIM_OUTPUT_DIR = os.path.join(_GEM5_SWEEPS_PATH, _SIM_SWEEP_NAME)

    # execute the benchmark with the simulator. If it fails at somepoint 
    #  return an empty result.
    try:
        results = __main(_PARAMS, _SIM_OUTPUT_DIR)
    except:
        results = {}

    # saving the results that BOAT could read in
    with open(_DEFAULT_RESULT_FILE, "w") as res_file:
        if not results:
            res_file.write(str(0.0))
        else:
            res_file.write(str(__get_target_value(results, args.results_key)))
            
    # TODO: do we need to clean up _SIM_OUTPUT_DIR ?
    