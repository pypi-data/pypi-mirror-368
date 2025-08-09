# Code-Astro_Project

## Galaxy Morphology Classifier
A deep learning project for classifying galaxy morphologies based on the Galaxy Zoo dataset. This model uses convolutional neural networks (CNNs) to classify galaxies into morphological categories such as elliptical, spiral, and others.


## Dataset
We use the Galaxy Zoo 1 dataset (GZ1), available from Kaggle.

## Source:
Kaggle Dataset: Galaxy Zoo Dataset (Kaggle)
https://www.kaggle.com/code/ansuman30sahu/galaxy-zoo-dataset/input

## Files used:
images_training_rev1.zip: Contains ~61,000 galaxy JPG images.
training_solutions_rev1.csv: Provides the vote fractions for each morphological feature.

## After extracting:
Images go into: images_training_rev1/
CSV goes into: project root or data/
The model uses images and their corresponding labels (based on vote thresholds) to classify galaxies.

## Classification Strategy
The original dataset includes 37 probabilistic classes. These were mapped to simplified galaxy types using a threshold strategy:

| Class      | Meaning                        | Group         |
|------------|--------------------------------|----------------|
| Class1.1   | Smooth (Completely round)      | Elliptical     |
| Class1.2   | Smooth (In between)            | Elliptical     |
| Class2.1   | Features or Disk               | Spiral         |
| Class4.1   | Spiral arms present            | Spiral         |
| Class8.1   | Merger                         | Other          |
| Class9.3   | Star / Artifact                | Other          |

## Tests
The create_tests.py script allows the user to crate dummy galaxies, which can then be used to test the code. This script allows for spiral, elliptical, barred spiral and bulge dominated galaxies to be created as .fits files. These images can then be used as input for the CNN, and the user will be able to compare the result of the neural network to the original type of galaxy that was chosen.


