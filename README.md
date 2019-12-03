# day_night_classification
Classify your pictures by classes day and night!

1. Evaluate your images:
python evaluate.py --path path/to/your/image/directory
Running the evaluate script results in a .csv-file composed of two columns (filename, classlabel). The pretrained model is used for this step.

2. Copy them into seperate directories:
python partition.py --path path/to/your/image/directory
Running the partition script results in two directiores in the results dir containing the final partition of the images 
  
3. Train the model w/ your own day/night images:
Your train data has to divided into two directories [../data/day, ../data/night]
python train.py --path path/to/your/train/data
Running the train script results in weights.h5 file
