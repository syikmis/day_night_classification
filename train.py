from __future__ import print_function

import argparse
import os

import bcolors
import keras
import numpy as np
from PIL import Image
from keras.callbacks import TensorBoard
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.models import Sequential
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

FILES_DIR_BASE = '/disk/vanishing_data/fp173/training_data'
model_name = 'day_night_classifier.h5'
epochs = 20
batch_size = 16
num_classes = 2
image_width = 128
image_heigth = 128
kernel_size = (2, 2)
input_shape = (image_width, image_heigth, 3)
labels = {0: 'day', 1: 'night'}

datagen = ImageDataGenerator(
    featurewise_center=False,  # set input mean to 0 over the dataset
    samplewise_center=False,  # set each sample mean to 0
    featurewise_std_normalization=False,  # divide inputs by std of the dataset
    samplewise_std_normalization=False,  # divide each input by its std
    zca_whitening=False,  # apply ZCA whitening
    zca_epsilon=1e-06,  # epsilon for ZCA whitening
    rotation_range=10,  # randomly rotate images in the range (degrees, 0 to 180)
    # randomly shift images horizontally (fraction of total width)
    width_shift_range=0.05,
    # randomly shift images vertically (fraction of total height)
    height_shift_range=0.05,
    shear_range=0.05,  # set range for random shear
    zoom_range=0.05,  # set range for random zoom
    channel_shift_range=0.,  # set range for random channel shifts
    # set mode for filling points outside the input boundaries
    fill_mode='nearest',
    cval=0.,  # value used for fill_mode = 'onstant'    horizontal_flip=True,  # randomly flip images
    vertical_flip=False,  # randomly flip images
    # set rescaling factor (applied before any other transformation)
    rescale=None,
    # set function that will be applied on each input
    preprocessing_function=None,
    # image data format, either 'hannels_first'or 'hannels_last'    data_format='hannels_last'
    # fraction of images reserved for validation (strictly between 0 and 1)
    validation_split=0.01)


def load_data(path):
    outdoor_data, outdoor_label = load_dataset(path, 'day')
    indoor_data, indoor_label = load_dataset(path, 'night')
    x = np.concatenate((outdoor_data, indoor_data))
    y = np.concatenate((outdoor_label, indoor_label))
    print(' shape', x.shape)
    print(' shape', y.shape)
    return x, y


def load_dataset(path, string):
    img_data = []
    labels_ = []

    path = os.path.join(path, string)
    files = os.listdir(path)
    files = [f for f in files if f.endswith('.jpg')]

    for file in files:
        path_to_img = os.path.join(path, file)
        img = Image.open(path_to_img)
        img = img.resize((image_width, image_heigth), resample=Image.BICUBIC)
        img = np.asarray(img)
        img = img.reshape(input_shape)
        img_data.append(img)
        if string == 'day':
            labels_.append(0)
        else:
            labels_.append(1)

    img_data = np.asarray(img_data)
    labels_ = np.asarray(labels_)
    print(string, str(img_data.shape), str(labels_.shape))
    return img_data, labels_


def make_model():
    model = Sequential()
    model.add(Conv2D(32, kernel_size, padding='same',
                     input_shape=input_shape))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, kernel_size))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(32, kernel_size))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes))
    model.add(Activation('softmax'))
    print(model.summary())

    return model


def main(FLAGS):
    print(bcolors.WAITMSG + '[INFO] Loading outdoor and indoor dataset..' + bcolors.END)
    model = make_model()
    x, y = load_data(FLAGS.path)
    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=420, test_size=0.15)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    print(bcolors.OKMSG + '[INFO] Loading data done!' + bcolors.END)

    model.compile(loss='categorical_crossentropy',
                  optimizer=Adam(lr=1e-3),
                  metrics=['accuracy'])

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    datagen.fit(x_train)

    # Fit the model on the batches generated by datagen.flow().
    print(bcolors.WARN + '[INFO] Starting training' + bcolors.END)
    print(bcolors.WARN + bcolors.BOLD + 'heavy workload for ya machine bruv' + bcolors.END)
    log_dir = 'logs/000'
    logging = TensorBoard(log_dir=log_dir, histogram_freq=1)

    model.fit_generator(datagen.flow(x_train, y_train,
                                     batch_size=batch_size),
                        epochs=epochs,
                        steps_per_epoch=len(x_train) // batch_size,
                        validation_data=(x_test, y_test),
                        callbacks=[logging])
    y_pred = model.predict_classes(x_test)
    y_pred = keras.utils.to_categorical(y_pred, num_classes)
    print(bcolors.BLUEIC + 'Confusion Matrix')
    print(confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1)))
    print('Classification Report')
    target = list(labels.values())
    print(classification_report(y_test.argmax(axis=1), y_pred.argmax(axis=1), target_names=target) + bcolors.END)
    model_path = os.path.join(model_name)
    model.save(model_path, include_optimizer=False)
    print(bcolors.OKMSG + '[INFO] Training done! Baaaam!' + bcolors.END)
    print(bcolors.BLUE + 'Saved trained model at %s ' % model_path + bcolors.END)

    # Score trained model.
    scores = model.evaluate(x_test, y_test, verbose=1)
    print('Test loss:', scores[0])
    print('Test accuracy:', scores[1])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, help='base path to trainings data')

    FLAGS = parser.parse_args()

    main(FLAGS)
