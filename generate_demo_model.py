import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os
model = keras.Sequential([
    layers.Input(shape=(224,224,3)),
    layers.Conv2D(8,3,activation='relu'),
    layers.MaxPool2D(),
    layers.GlobalAveragePooling2D(),
    layers.Dense(2,activation='softmax')
])
export_dir = os.path.join(os.getcwd(),'models','agro_demo','1')
os.makedirs(export_dir, exist_ok=True)
model.save(export_dir, include_optimizer=False)
print('Saved demo model to', export_dir)
