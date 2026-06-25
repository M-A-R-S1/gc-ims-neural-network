# BASIC SETTINGS
DRIFT_CUT = (1.02, 2.0)
RETENTION_CUT = (150, 1900)
INPUT_DIR = "./data/IMS_Honey_RUB"
OUTPUT_DIR = "./output/IMS_Honey_RUB"
PLOT_DIR = "./output/IMS_Honey_RUB/model_plots"
###########################################################################################
PREPROCESSING = False                   # Preprocess the data?
PEAK_DETECTION = False                  # Detect raw peaks?
CONSENSUS_PEAK_CALCULATION = False      # Calculate new consensus peaks?
SAVE_CONSENSUS_WINDOWS = False          # Save consensus peak windows as .npy files?
USE_NEURAL_NETWORK = False              # Build or work with the neural network?
RANDOM_FOREST_CLASSIFICATION = False    # Use the random forest classifier.

PEAK_RADIUS = 5
MAX_NODE_DISTANCE = 0.006
###########################################################################################
# VAE NEURONAL NETWORK
# Define training hyperparameters here.
BATCH_SIZE = 16
LEARNING_RATE = 0.00005
EPOCHS = 1500
LATENT_DIM = 16
HIDDEN_DIM = 64
PLOT_INTERVAL = 300
TARGET_BETA = 1.0
BETA_WARMUP = 300

# What should the main neural network do?
DO_TRAINING = True                # Train the model?
DO_TESTING = False               # Test the model?
TEST_WITH_ALL_DATA = False        # Do you want to test the model with all the available data? [No Splitting].
SAVING = True                     # Save the model?

# Directory and filename for saving and loading.
SAVE_DIR = "models"
FILE_NAME = "HONEY-RUB-1500.pt"
###########################################################################################
# RANDOM FOREST CLASSIFICATION
SINGLE_PEAK_RANDOM_FOREST = True
COMBINED_RANDOM_FOREST = True