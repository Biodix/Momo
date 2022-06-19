import csv
import multiprocessing
import time
import tableaux.core.tableau as tb
import tableaux.preproccesing.syntax_parser
import os
from natsort import natsorted
from tableaux.utils.recursionlimit import recursionlimit


def execute_file(file, t=60, n=1):
    manager = multiprocessing.Manager()
    q = manager.Queue()
    threads = [multiprocessing.Process(target=tb.execute_file, args=(file, q)) for i in range(n)]
    start_time = time.time()
    for thread in threads:
        thread.start()
    end_time=0
    while (end_time) < t and q.qsize() < 1:
        time.sleep(0.01)
        end_time = time.time() - start_time
    for thread in threads:
        thread.terminate()
    res = q.get() if not q.empty() else [file,'to','to']
    res[1] = end_time if res[2] != 'to' else 'to'
    print(end_time)
    return res

def execute_momo():
    if SERVER:
        cmd = 'python3 Momo/momo.py -f "Momo/{}"'.format(file)
    else:
        cmd = 'python3 Momo/momo.py -f "Momo/{}"'.format(file)
    init_time = time.time()
    ps = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    ps.wait()
    end_time = time.time() - init_time
    output = str(ps.communicate()[0])
    if "Model Not Found" in output:
        res_sat = 0
    elif "Model Found" in output:
        res_sat = 1
    else:
        res_sat = -1
    if q:
        q.put([file, end_time, res_sat])


def write_to_file(benchmark_type, file_name, res, sat):
    file = '{}_{}'.format(benchmark_type, sat)
    with open(file, 'a+') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow([file_name] + list(res))

def write_to_file(res):
    file_path_split = res[0].split('/')
    file = "results/{}/{}/{}.csv".format(file_path_split[-4],file_path_split[-3],file_path_split[-2])
    print(file)
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'a+') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(res)

def flush_files(res):
    file_path_split = res.split('/')
    print("File path: ", file_path_split)
    file = "results/{}/{}/{}.csv".format(file_path_split[-3],file_path_split[-2],file_path_split[-1])
    print("File to flush: ",file)
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w+') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(["file","time","sat"])


def test_benchmarks(t=0.1):
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
                with recursionlimit():
                    res = execute_file(file_path, t)
                #write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'no_sat')
                i += 1


def test_black():
    list_dirs = os.listdir('test/antiblack')
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
            with recursionlimit():
                res = execute_file(file_path, t)
            #write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'no_sat')
            i += 1


def test_new_benchmarks_momo2():
    origin_path= './benchmarks/new'
    list_dirs = os.listdir(origin_path)
    list_dirs = natsorted(list_dirs, key=lambda y: y.lower())

    for folder in list_dirs:
        folder = '{}/{}'.format(origin_path,folder)
        list_folders = os.listdir(folder)
        list_folders = natsorted(list_folders, key=lambda y: y.lower())
        print("Folder: ", folder)
        for subfolder in list_folders:
            subfolder = '{}/{}'.format(folder, subfolder)
            list_subfolders = os.listdir(subfolder)
            list_subfolders = natsorted(list_subfolders, key=lambda y: y.lower())
            print("Subfolder: ",subfolder)
            flush_files(subfolder)
            for file in list_subfolders:
                file = '{}/{}'.format(subfolder, file)
                print("File: ",file)
                if '.negated' in subfolder:
                    continue
                time.sleep(0.1)
                with recursionlimit():
                    res = execute_file(file)
                print(res)
                write_to_file(res)
                #write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'no_sat')

def test_new_benchmarks_momo(t):
    origin_path= 'benchmarks/new'
    list_dirs = os.listdir(origin_path)
    list_dirs = natsorted(list_dirs, key=lambda y: y.lower())

    for folder in list_dirs:
        folder = '{}/{}'.format(origin_path,folder)
        list_folders = os.listdir(folder)
        list_folders = natsorted(list_folders, key=lambda y: y.lower())
        print("Folder: ", folder)
        for subfolder in list_folders:
            subfolder = '{}/{}'.format(folder, subfolder)
            list_subfolders = os.listdir(subfolder)
            list_subfolders = natsorted(list_subfolders, key=lambda y: y.lower())
            print("Subfolder: ",subfolder)
            flush_files(subfolder)
            fails=0
            for file in list_subfolders:
                file = '{}/{}'.format(subfolder, file)
                if fails >= 5:
                    print('------ SKIP ------')
                    res = [file,'to','to']
                    write_to_file(res)
                    continue
                print("File: ",file)
                if '.negated' in subfolder:
                    continue
                time.sleep(0.1)
                with recursionlimit():
                    res = execute_file(file,t)
                if 'to' in res:
                    fails += 1
                print(res)
                write_to_file(res)
                #write_to_file('results/{}.csv'.format(benchmark_type), file_name, res, 'no_sat')

if __name__ == '__main__':
    test_new_benchmarks_momo(5)


