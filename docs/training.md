# Training

Configure image size, batch size, epochs, and learning rate on the Training
page, then Start Training. Training runs on a background thread using
tf.data generators (no full-dataset RAM loading), BCE+Dice loss, Adam
optimizer, early stopping on validation loss, and saves both the best and
latest checkpoints plus TensorBoard logs under logs/tensorboard/.
