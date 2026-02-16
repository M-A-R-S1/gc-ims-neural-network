# OLIVE DATA [https://doi.org/10.1016/j.dib.2022.108730]
DRIFT_CUT = (1.02, 2.5)
RETENTION_CUT = (80, 900)
INPUT_DIR = "./data/IMS_Olive_Oil_Geography"
OUTPUT_DIR = "./output/IMS_Olive_Oil_Geography"
PLOT_DIR = "./output/IMS_Olive_Oil_Geography/model_plots"

# HONEY DATA [http://dx.doi.org/10.1016/j.foodres.2022.111779]
#DRIFT_CUT = (1.02, 2.5)
#RETENTION_CUT = (150, 1000)
#INPUT_DIR = "./data/IMS_Honey_Botanical"
#OUTPUT_DIR = "./output/IMS_Honey_Botanical"
#PLOT_DIR = "./output/IMS_Honey_Botanical/model_plots"
###########################################################################################
PREPROCESSING = False                   # Preprocess the data?
PEAK_DETECTION = False                  # Detect raw peaks?
CONSENSUS_PEAK_CALCULATION = False      # Calculate new consensus peaks?
SAVE_CONSENSUS_WINDOWS = False           # Save consensus peak windows as .npy files?
USE_NEURAL_NETWORK = False              # Build or work with the neural network?
RANDOM_FOREST_CLASSIFICATION = True    # Use the random forest classifier.

PEAK_RADIUS = 5
MAX_NODE_DISTANCE = 0.006
###########################################################################################
# STEP 4 - VAE NEURONAL NETWORK
# Define training hyperparameters here.
BATCH_SIZE = 16
LEARNING_RATE = 0.00005
EPOCHS = 1500
LATENT_DIM = 6
HIDDEN_DIM = 64
PLOT_INTERVAL = 150
TARGET_BETA = 1.0
BETA_WARMUP = 300

# What should the main neural network do?
DO_TRAINING = True                # Train the model?
DO_TESTING = False               # Test the model?
TEST_WITH_ALL_DATA = False        # Do you want to test the model with all the available data? [No Splitting].
SAVING = False                     # Save the model?

# Directory and filename for saving and loading.
SAVE_DIR = "models"
FILE_NAME = "GC-IMS-CNN-VAE-OLIVES-BCE-1500.pt"
###########################################################################################