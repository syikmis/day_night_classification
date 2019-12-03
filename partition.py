import argparse
import csv
import glob
import os
import shutil
import sys
from timeit import default_timer as timer

import bcolors

prediction_results = 'day_night_prediction.csv'

with open(prediction_results) as src:
    reader = csv.reader(src, delimiter="\t")
    prediction_dict = dict(reader)


def check_dirs(path):
    print("Checking " + str(path))
    if os.path.exists(path) and os.path.isdir(path):
        if not os.listdir(path):
            print("[INFO] Directory is empty")
        else:
            print("[INFO] Directory is not empty!")
            boolean = input(
                bcolors.WARN + "Do you want to delete all files? [true, false]\n" + bcolors.END).lower().strip()
            if boolean == "true":
                print(bcolors.OKMSG + "[INFO] Deleting directory content" + bcolors.END)
                files = glob.glob(os.path.join(path, '*'))
                for f in files:
                    os.remove(f)
            else:
                print("Break!")
                sys.exit()
    else:
        print("Given Directory don't exists! Creating directory...")
        os.mkdir(path)


os.mkdir('results')
day_path = 'results/day'
night_path = 'results/night'
parser = argparse.ArgumentParser()
parser.add_argument('--path', type=str, help='path to img dir to partition')

FLAGS = parser.parse_args()
check_dirs(day_path)
check_dirs(night_path)

files = os.listdir(FLAGS.path)
files_list = [f for f in files if not f.startswith(".")]
i = 0
start = timer()
for file in files_list:
    prediction = prediction_dict[file]
    if prediction == "night":
        shutil.copy(os.path.join(FLAGS.path, file), night_path)
    elif prediction == "day":
        shutil.copy(os.path.join(FLAGS.path, file), day_path)

    if i % 125 == 0:
        print(bcolors.WAITMSG + '[INFO] Partitioned %.2f percent of all test files'
              % (i / len(files_list) * 100) + bcolors.ENDC)

    i += 1
end = timer()
print(bcolors.OKMSG + "[INFO] The partitioning of " + str(len(files_list)) + " images took " + str(
    round(end - start, 2)) + " seconds")
