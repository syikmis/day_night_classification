import argparse
import os
from timeit import default_timer as timer

import bcolors
import numpy as np
from PIL import Image
from keras.models import load_model

PRED_RESULT = 'day_night_prediction.csv'

weights = 'day_night_classifier.h5'
image_width = 128
image_heigth = 128
input_shape = (image_width, image_heigth, 3)
labels = {0: "day", 1: "night"}


def image_to_input(path, file):
    path_to_img = os.path.join(path, file)
    img = Image.open(path_to_img)
    img = img.resize((image_width, image_heigth), resample=Image.BICUBIC)
    img = np.asarray(img) / 255
    img = img.reshape(input_shape)
    img = np.expand_dims(img, 0)
    return img


def main(FLAGS):
    start = timer()
    test_files = [f for f in os.listdir(FLAGS.path) if not f.startswith(".")]
    model = load_model(weights)
    predictions = []
    predictions_counter = {}
    with open(PRED_RESULT, 'w') as dst:
        i = 0
        for file in test_files:
            model_input = image_to_input(FLAGS.path, file)
            prediction = model.predict(model_input)[0]
            if prediction[0] == 1:
                label = labels[0]
            else:
                label = labels[1]
            predictions.append(label)
            dst.write(f"{file}\t{label}\n")
            if i % 125 == 0:
                print(bcolors.WAITMSG + '[INFO] Evaluated %.2f percent of all test files'
                      % (i / len(test_files) * 100) + bcolors.ENDC)

            i += 1
    for pred in predictions:
        if pred in predictions_counter:
            predictions_counter[pred] += 1
        else:
            predictions_counter[pred] = 1
    print(bcolors.OKMSG + "[INFO] Frequencies of predictions: \n")
    for key, value in predictions_counter.items():
        print("{}: {}".format(key, value))
    end = timer()
    print("[INFO] Prediction for " + str(len(test_files)) + " took " + str(
        round(end - start, 2)) + " seconds" + bcolors.END)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='path to img dir to classify')

    FLAGS = parser.parse_args()

    main(FLAGS)
