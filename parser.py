import os
import time
from natsort import natsorted
import subprocess
from pathlib import Path

benchmark_types = ['application', 'crafted', 'random']

def extract_variables(formula):
    import re
    p = re.compile('(([a-z_AP]|(G\d+))+\d*(\_\d*)?)')
    m = p.findall(formula)
    vars = set()
    for var in m:
        vars.add(var[0])
    return vars


def write_to_file_NuSMV(benchmark_type,file_name,time,satisfiable):
    file = 'NuSMV_results/{}'.format(benchmark_type)
    with open(file,'a+') as f:
        f.write("{},{},{}\n".format(file_name,time,satisfiable))


def write_momo_style_file(input_file, output_file, output_extension="pltl"):
    print(input_file)
    #output_file = output_file[:-3]+'smv'
    output_file = output_file + output_extension
    print(output_file)
    # Clear the file
    open(output_file,'w').close()
    with open(input_file) as f:
        formula = f.read()
    #formula = formula.replace(' ','')
    formula = formula.replace('fUll', 'full')
    formula = formula.replace('(g ', '(G ')
    formula = formula.replace(' f ',' F ')
    vars = extract_variables(formula)
    with open(output_file, 'w'): pass
    with open(output_file,'a') as f:
        # Change from Momo syntax to NuSMV syntax
        formula = formula.replace('=','(_iff_)')
        formula = formula.replace('>','(_implication_)')
        formula = formula.replace('-', '(_negation_)')

        formula = formula.replace('(_iff_)','=')
        formula = formula.replace('(_implication_)','->')
        formula = formula.replace('(_negation_)', '!')
        formula = formula.replace('Xu','X(u)')
        f.write(formula)
    return output_file

def execute_all_NuSMV():
    for benchmark_type in benchmark_types:
        write_to_file_NuSMV(benchmark_type+'.csv','file','time','satisfiable')
        i=0
        list_dirs = os.listdir('benchmarks/' + benchmark_type)
        list_dirs = natsorted(list_dirs, key=lambda y: y.lower())
        for folder in list_dirs:
            folder = 'benchmarks/{}/{}'.format(benchmark_type,folder)
            list_files = os.listdir(folder)
            list_files = natsorted(list_files, key = lambda y: y.lower())
            for file_name in list_files:
                nusmv_file_path = '{}/{}'.format(folder, file_name)
                #nusmv_file_path = write_NuSMV_style_file(file_path)
                print(nusmv_file_path)
                command = "./NuSMV {}".format(nusmv_file_path)  # launch your python2 script using bash
                process = 0
                response = ''
                try:
                    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                    ini = time.time()
                    stdout = process.communicate(timeout=60)
                    response = str(stdout[0])
                    elapsed_time = time.time() - ini
                except Exception:
                    print('time up!')
                    elapsed_time = 'to'
                    if process.poll() is None:
                        process.kill()
                        process.wait()
                if 'false' in response:
                    satisfiable = 1
                else:
                    satisfiable = 0
                    

                write_to_file_NuSMV('{}.csv'.format(benchmark_type), file_name, elapsed_time,satisfiable)
                write_to_file_NuSMV('{}-log.csv'.format(benchmark_type), file_name, i,satisfiable)
                i+=1

def parse_to_black():
    path= '../benchmarks/new_benchmarks/new-LTL-benchmarks'
    list_dirs = os.listdir(path)
    list_dirs = natsorted(list_dirs, key=lambda y: y.lower())
    print(list_dirs)
    for folder in list_dirs:
        folder_path = '{}/{}'.format(path,folder)
        print(folder_path)
        new_path = './black_benchmarks/{}'.format(folder)
        print(new_path)
        Path(new_path).mkdir(parents=True, exist_ok=True)
        list_files = os.listdir(folder_path)
        list_files = natsorted(list_files, key = lambda y: y.lower())
        print(list_files)
        for file_name in list_files:
            file_path = './black_benchmarks/{}/{}'.format(folder, file_name)
            print(file_path)
            Path(file_path).mkdir(parents=True, exist_ok=True)
            files = os.listdir(file_path)
            files = natsorted(files, key=lambda y: y.lower())
            for f in files:
                print(f)
                nusmv_file_path = write_momo_style_file(f)
                print(nusmv_file_path)


def old_benchmarks_to_black():
    new_benchmarks_path= '../benchmarks/old'
    translated_benchmarks_path = './benchmarks/old'
    list_dirs = os.listdir(new_benchmarks_path)
    benchmark_families = natsorted(list_dirs, key=lambda y: y.lower())
    print(benchmark_families)
    for benchmark_family in benchmark_families:
        benchmark_family_sets = '{}/{}'.format(new_benchmarks_path,benchmark_family)
        print(benchmark_family_sets)
        translated_benchmark_family_path = '{}/{}'.format(translated_benchmarks_path, benchmark_family)
        print(translated_benchmark_family_path)
        Path(translated_benchmark_family_path).mkdir(parents=True, exist_ok=True)
        list_files = os.listdir(benchmark_family_sets)
        benchmark_family_subsets = natsorted(list_files, key = lambda y: y.lower())
        print(benchmark_family_subsets)
        for new_benchmark_file_name in benchmark_family_subsets:
            print('aaaaaaaaaaa')
            print(new_benchmark_file_name)
            benchmark_family_subsets = '{}/{}'.format(benchmark_family_sets, new_benchmark_file_name)
            print(benchmark_family_subsets)
            new_benchmark_file_path = '{}/{}'.format(translated_benchmark_family_path, new_benchmark_file_name)
            print(new_benchmark_file_path)
            Path(new_benchmark_file_path).mkdir(parents=True, exist_ok=True)
            files = os.listdir(benchmark_family_subsets)

            print(files)
            ctl_files = natsorted(files, key=lambda y: y.lower())
            print('ctl files: ',ctl_files)
            for f in ctl_files:
                print(f)
                input_path = '{}/{}'.format(benchmark_family_subsets,f)
                output_path = '{}/{}'.format(new_benchmark_file_path, f)
                print('------------------------')
                print(input_path)
                print('++++++++++++++++++++++++')
                nusmv_file_path = write_momo_style_file(input_path, output_path[:-4])


def new_benchmarks_to_momo():
    new_benchmarks_path= '../benchmarks/new'
    translated_benchmarks_path = './benchmarks/new'
    list_dirs = os.listdir(new_benchmarks_path)
    benchmark_families = natsorted(list_dirs, key=lambda y: y.lower())
    print(benchmark_families)
    for benchmark_family in benchmark_families:
        benchmark_family_sets = '{}/{}'.format(new_benchmarks_path,benchmark_family)
        print(benchmark_family_sets)
        translated_benchmark_family_path = '{}/{}'.format(translated_benchmarks_path, benchmark_family)
        print(translated_benchmark_family_path)
        Path(translated_benchmark_family_path).mkdir(parents=True, exist_ok=True)
        list_files = os.listdir(benchmark_family_sets)
        benchmark_family_subsets = natsorted(list_files, key = lambda y: y.lower())
        print(benchmark_family_subsets)
        for new_benchmark_file_name in benchmark_family_subsets:
            print('aaaaaaaaaaa')
            print(new_benchmark_file_name)
            benchmark_family_subsets = '{}/{}'.format(benchmark_family_sets, new_benchmark_file_name)
            print(benchmark_family_subsets)
            new_benchmark_file_path = '{}/{}'.format(translated_benchmark_family_path, new_benchmark_file_name)
            print(new_benchmark_file_path)
            Path(new_benchmark_file_path).mkdir(parents=True, exist_ok=True)
            files = os.listdir(benchmark_family_subsets)

            print(files)
            ctl_files = natsorted(files, key=lambda y: y.lower())
            print('ctl files: ',ctl_files)
            for f in ctl_files:
                print(f)
                input_path = '{}/{}'.format(benchmark_family_subsets,f)
                output_path = '{}/{}'.format(new_benchmark_file_path, f)
                print('------------------------')
                print(input_path)
                print(output_path)
                print('++++++++++++++++++++++++')
                if '.pltl' in output_path:
                    nusmv_file_path = write_momo_style_file(input_path, output_path[:-4])
                elif '.ctl' in output_path:
                    nusmv_file_path = write_momo_style_file(input_path, output_path[:-3])
                elif '.ltl' in output_path:
                    nusmv_file_path = write_momo_style_file(input_path, output_path[:-3])
                print(input_path)
#parse_to_NuSMV()
#execute_all_NuSMV()
new_benchmarks_to_momo()
#old_benchmarks_to_black()
print("aaaaaaaaa")