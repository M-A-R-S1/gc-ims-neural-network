# Define training hyperparameters here.
BATCH_SIZE = 16
LEARNING_RATE = 0.0001
EPOCHS = 5
LATENT_DIM = 6
# LATENT_DIM = 6        3.42 | 3.53
# LATENT_DIM = 4        3.41 | 3.63
# LATENT_DIM = 16       3.47 | 3.63
# LATENT_DIM = 8        3.42 | 3.58
HIDDEN_DIM = 64
# HIDDEN_DIM = 16       3.62 | 3.71
# HIDDEN_DIM = 32       3.49 | 3.63
# HIDDEN_DIM = 64       3.42 | 3.58 ***
# HIDDEN_DIM = 256      3.49 | 3.67
# HIDDEN_DIM = 128      3.41 | 3.58 ***

# What should the main script do?
DO_TRAINING = True              # Train the model?
DO_TESTING = False              # Test the model?
SAVING = True                   # Save the model?

# Directory and filename for saving and loading.
SAVE_DIR = "models"
FILE_NAME = "GC-IMS-CNN-VAE.pt"