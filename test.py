import argparse
import tableaux.core.tableau as tb
import os
import multiprocessing
import time
import csv
import sys

from natsort import natsorted

if sys.platform != 'win32':
    from tableaux.utils.recursionlimit import recursionlimit

# readme:
# Lanzamiento provisional:
# Para ejecutar un fichero ejecutar desde la terminal
# >>> python momo.py [nombre_fichero]

# Para ejecutar sobre una formula ejecutar desde la terminal
# >>> python momo.py [formula]



def execute_file(file, t=60):
    manager = multiprocessing.Manager()
    q = manager.Queue()
    thread = multiprocessing.Process(target=tb.execute_file, args=(file, q))
    start_time = time.time()
    thread.start()
    while (time.time() - start_time) < t and q.qsize() < 1:
        time.sleep(0.01)
    thread.terminate()
    res = q.get() if not q.empty() else 'to'
    return res


def write_to_file(benchmark_type, file_name, res, sat):
    file = '{}'.format(benchmark_type)
    with open(file, 'a+') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        if isinstance(res,list) or isinstance(res,tuple) or isinstance(res,set):
            wr.writerow([file_name] + list(res))
        else:
            wr.writerow([file_name] + [res])


def test_benchmarks(t=60):
    benchmark_types = ['application', 'crafted', 'random']
    for benchmark_type in benchmark_types:
        i = 0
        list_dirs = os.listdir('benchmarks/' + benchmark_type)
        list_dirs = natsorted(list_dirs, key=lambda y: y.lower())
        for folder in list_dirs:
            folder = 'benchmarks/{}/{}'.format(benchmark_type, folder)
            list_files = os.listdir(folder)
            list_files = natsorted(list_files, key=lambda y: y.lower())
            for file_name in list_files:
                if '.negated' in file_name:
                    continue
                file_path = '{}/{}'.format(folder, file_name)
                time.sleep(0.1)
                print(file_path)
                if sys.platform == 'win32':
                    res = execute_file(file_path, t)
                else:
                    with recursionlimit():
                        res = execute_file(file_path, t)
                print(res)
                write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'sat')
                i += 1





#write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'no_sat')
def test_black():
    list_dirs = os.listdir('test/antiblack')
    list_dirs = natsorted(list_dirs, key=lambda y: y.lower())
    for file in list_dirs[:12]:
        init_time = time.time()
        tb.test('test/antiblack/'+file, False)
        end = time.time() - init_time
        print('{}: {}'.format(file,end))
# test_black()

if __name__ == '__main__':
    # input_file = "benchmarks/new/crafted/schuppan_phltl/phltl_3_2.pltl"
    # input_file = "benchmarks/new/crafted/rozier_counter/counter3.pltl"
    input_file = "benchmarks/new/application/alaska_lift/lift_2.pltl"
    # input_file = "G a & X(X(!a)) & Fc"
    trace=False
    with recursionlimit():
        tb.test(input_file, trace)