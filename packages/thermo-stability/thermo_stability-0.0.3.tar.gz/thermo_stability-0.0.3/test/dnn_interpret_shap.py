import shap
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from thermo_stability import config, utils

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import layers

# data preparation for MLs
from sklearn.utils import class_weight

logpath = config.LOG_DIR
logger = utils.setup_logging(log_path=logpath + "/shap.txt", name="SHAP")

filepath  = config.FILE_DIR
modelpath = config.MODEL_DIR
plotpath  = config.PLOT_DIR

# Load data split in numpy format, pandas
npz_datasplit = np.load(os.path.join(filepath, 'npz_datasplits.npz'),allow_pickle=True)
X_train_scaled = npz_datasplit['X_train_scaled']
X_val_scaled = npz_datasplit['X_val_scaled']
X_test_scaled = npz_datasplit['X_test_scaled']
y_train = npz_datasplit['y_train']
y_val   = npz_datasplit['y_val']
y_test  = npz_datasplit['y_test']

pd_datasplit = pd.read_csv(os.path.join(filepath, 'df_datasplit.csv'))
Xpd_train_scaled = pd_datasplit[pd_datasplit['split'] == 'train_scaled'].drop(columns=['split','label']) 

act='relu'
# Optimizer with learning rate
adam = tf.keras.optimizers.legacy.Adam(learning_rate=0.0003)
loss = 'binary_crossentropy'

# learning rate scheduler; lowers the learning rate when the validation loss plateaus
lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=1, min_lr=1e-6)

'''# Define model
DNN_model = Sequential()
# Input layer
DNN_model.add(layers.Dense(128, activation=act, input_shape=[X_train_scaled.shape[1]]))
DNN_model.add(layers.Dropout(0.1))
DNN_model.add(layers.BatchNormalization())

# Hidden layers (using a loop)
for _ in range(1):  # 2 hidden layers
    DNN_model.add(layers.Dense(128, activation=act))
    DNN_model.add(layers.Dropout(0.3)) # typical dropout for moderate to strong regularization
    DNN_model.add(layers.BatchNormalization())

# Output layer
DNN_model.add(layers.Dense(1,activation='sigmoid'))

#Compile the model
DNN_model.compile(optimizer='adam', loss=loss, metrics=['accuracy'])
logger.info(DNN_model.summary())

# to avoid overfitting
early_stopping = tf.keras.callbacks.EarlyStopping(patience = 5, min_delta = 0.001, restore_best_weights = True)

# Compute class weights
class_weights = class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(class_weights))

history_dnn = DNN_model.fit(X_train_scaled, y_train, validation_data=(X_val_scaled, y_val), batch_size=128, epochs=13)#, callbacks=[early_stopping, lr_scheduler], class_weight=class_weights) # alternatively use: callbacks=[lr_scheduler]'''


# hardcoded hypertunned model:
batch, neurons, layer_num = 128, 128, 2
act = 'relu'
# Define model
DNN_model = Sequential()
# Input layer
#DNN_model.add(layers.Dense(neurons, activation=act, input_shape=[X_train_scaled.shape[1]]))
DNN_model.add(layers.Dense(neurons, input_shape=[X_train_scaled.shape[1]]))
DNN_model.add(layers.BatchNormalization())
DNN_model.add(layers.Activation(act))
DNN_model.add(layers.Dropout(0.1))
#

# Hidden layers (using a loop)
for _ in range(layer_num):  # 1 hidden layers
    #DNN_model.add(layers.Dense(neurons, activation=act))
    DNN_model.add(layers.Dense(neurons))
    DNN_model.add(layers.BatchNormalization())
    DNN_model.add(layers.Activation(act))
    DNN_model.add(layers.Dropout(0.1)) # typical dropout for moderate to strong regularization
    #DNN_model.add(layers.BatchNormalization())

# Output layer
DNN_model.add(layers.Dense(1,activation='sigmoid'))

#Compile the model
DNN_model.compile(optimizer=adam, loss=loss, metrics=['accuracy'])

early_stopping = tf.keras.callbacks.EarlyStopping(patience = 10, min_delta = 0.001, restore_best_weights = True)
   
   # Compute class weights
class_weights = class_weight.compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
class_weights = dict(enumerate(class_weights))
DNN_model.fit(X_train_scaled, y_train, validation_data=(X_val_scaled, y_val), batch_size=batch, epochs=50, callbacks=[early_stopping,lr_scheduler], class_weight=class_weights) 



# SHAP explanation (using DeepExplainer for TensorFlow/Keras)
explainer = shap.DeepExplainer(DNN_model, X_train_scaled[:100])
shap_values = explainer.shap_values(X_test_scaled[:100])


shap_values_2d = np.squeeze(shap_values)
mean_shap = np.abs(shap_values_2d).mean(axis=0)
top_indices = np.argsort(mean_shap)[-15:]  # top 15 features
feat_imporname = [Xpd_train_scaled.columns[i] for i in top_indices]
shap.summary_plot(shap_values_2d[:, top_indices], X_test_scaled[:100, top_indices],feature_names=feat_imporname,show=False)#,label=Xpd_train_scaled.columns[top_indices])
impfeat_filename = os.path.join(plotpath,'dnn_shap.pdf')
plt.savefig(impfeat_filename)
plt.close()

feat_imporname = [f"{Xpd_train_scaled.columns[i]}: {mean_shap[i]:.3f}" for i in top_indices]

sorted_values = mean_shap[top_indices]
shap.summary_plot(shap_values_2d[:, top_indices], X_test_scaled[:100, top_indices], plot_type='bar',feature_names=feat_imporname,show=False)
plt.tight_layout()
shap_filename = os.path.join(plotpath,'dnn_impfeat.pdf')
plt.savefig(shap_filename)
plt.close()

