import os
import cv2
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization

def load_images(image_folder, image_ids, size=(64, 64)):
    images = []
    for img_id in image_ids:
        img_path = os.path.join(image_folder, f"{img_id}.jpg")
        img = cv2.imread(img_path)
        if img is not None:
            img = cv2.resize(img, size)
            images.append(img / 255.0)
    return np.array(images)

def build_model(input_shape, num_labels):
    model = Sequential([
        Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=input_shape),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(64, (3, 3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(128, (3, 3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Conv2D(256, (3, 3), padding='same', activation='relu'),
        BatchNormalization(),
        MaxPooling2D((2, 2)),

        Flatten(),
        Dense(512, activation='relu'),
        Dropout(0.5),
        Dense(num_labels, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model



class_descriptions = {
    'Class1.1': 'Smooth (Completely round)',
    'Class1.2': 'Smooth (In between)',
    'Class1.3': 'Smooth (Cigar-shaped)',
    'Class2.1': 'Features or Disk',
    'Class2.2': 'Edge-on, Yes',
    'Class2.3': 'Edge-on, No',
    'Class3.1': 'Bar present',
    'Class3.2': 'No bar',
    'Class4.1': 'Spiral arms present',
    'Class4.2': 'No spiral arms',
    'Class5.1': 'Bulge: No bulge',
    'Class5.2': 'Bulge: Just noticeable',
    'Class5.3': 'Bulge: Obvious',
    'Class5.4': 'Bulge: Dominant',
    'Class6.1': 'Roundness: Completely round',
    'Class6.2': 'Roundness: In between',
    'Class6.3': 'Roundness: Cigar-shaped',
    'Class7.1': 'Odd: Yes',
    'Class7.2': 'Odd: No',
    'Class8.1': 'Merger',
    'Class8.2': 'Not a merger',
    'Class9.1': 'Don’t know what to choose',
    'Class9.2': 'Artifact',
    'Class9.3': 'Star / Artifact',
    'Class10.1': 'Spiral winding: Tight',
    'Class10.2': 'Spiral winding: Medium',
    'Class10.3': 'Spiral winding: Loose',
    'Class11.1': 'Spiral arm count: 1',
    'Class11.2': 'Spiral arm count: 2',
    'Class11.3': 'Spiral arm count: 3'
}
