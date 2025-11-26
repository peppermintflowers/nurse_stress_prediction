import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import joblib # Used to save the model
import os
import kagglehub # Library for downloading Kaggle datasets
import glob
import sys
import re
from io import StringIO

# --- Configuration ---
KAGGLE_DATASET = "priyankraval/nurse-stress-prediction-wearable-sensors"
LOCAL_DATA_FILE = 'nurse_stress_data.csv' # Name of the small simulated file
# CONFIRMED Name of the main CSV file inside the Kaggle dataset
KAGGLE_DATA_FILENAME = 'merged_data.csv'

# Define the mapping from the *NORMALIZED* (lowercase, stripped) raw column names
# to the clean names used in the model. This handles both files robustly.
COLUMN_MAP = {
    # Normalized headers from BOTH the simulated file and the downloaded Kaggle file
    # (assuming the Kaggle file uses 'id', 'x', 'hr', 'eda', etc., potentially capitalized)
    'id': 'User_ID',
    'timestamp': 'Timestamp', # Keep Timestamp for context, though not a feature
    'x': 'Orientation_X',
    'y': 'Orientation_Y',
    'z': 'Orientation_Z',
    'hr': 'Heart_Rate',
    'temp': 'Skin_Temp',
    'eda': 'EDA',
    'label': 'Stress_Label',

    # Also map the prefixed names from the simulated file, normalized
    '@ id': 'User_ID',
    '# x': 'Orientation_X',
    '# y': 'Orientation_Y',
    '# z': 'Orientation_Z',
    '# hr': 'Heart_Rate',
    '# temp': 'Skin_Temp',
    '# eda': 'EDA',
    '# label': 'Stress_Label',
}

# --- 0. Data Download Function ---
def download_kaggle_dataset():
    """Downloads the full Kaggle dataset and returns the path to the directory."""
    print(f"Target data file '{LOCAL_DATA_FILE}' not found. Attempting to download '{KAGGLE_DATASET}' from KaggleHub...")

    try:
        download_path = kagglehub.dataset_download(KAGGLE_DATASET)
        print(f"Dataset downloaded successfully to: {download_path}")
        return download_path

    except Exception as e:
        print(f"Kaggle download failed. Ensure you have the Kaggle API key configured.")
        print(f"Error: {e}")
        return None

# --- 1. Load Data ---
df = None
downloaded_path = None
data_file_path = LOCAL_DATA_FILE
loaded_from_fallback = False

# Check for local file first
if not os.path.exists(LOCAL_DATA_FILE):
    downloaded_path = download_kaggle_dataset()

    # If download was successful, try to find the specific CSV file inside the downloaded folder
    if downloaded_path:
        # Check for the expected CSV name in the downloaded folder
        potential_file = os.path.join(downloaded_path, KAGGLE_DATA_FILENAME)
        if os.path.exists(potential_file):
            data_file_path = potential_file
            print(f"Found Kaggle file at: {data_file_path}")
        else:
            print(f"Warning: Could not locate '{KAGGLE_DATA_FILENAME}' in the Kaggle download folder.")
            data_file_path = None # Force fallback or use the simulation below

# Attempt to load the final determined file path (either local, or downloaded)
try:
    if data_file_path and os.path.exists(data_file_path):
        # Setting low_memory=False to handle the DtypeWarning on the large CSV
        df = pd.read_csv(data_file_path, low_memory=False)
        print(f"Data loaded successfully from {data_file_path}.")
    else:
        # This occurs if the local file wasn't found AND the download failed/file was missing.
        print(f"Fatal Error: Data file not found at expected path: {data_file_path}")
        print("Using simulated data as a guaranteed fallback for demonstration.")
        loaded_from_fallback = True

        # FALLBACK: Create a small DataFrame from the simulated data
        simulated_csv_data = """@ id,Timestamp,# X,# Y,# Z,# HR,# TEMP,# EDA,# label
15,1704067200,-13.0,-61.0,5.0,99.43,31.17,6.769995,2
15,1704067200,-20.0,-69.0,-3.0,99.43,31.17,6.769995,2
16,1704067200,-31.0,-78.0,-15.0,85.20,30.50,4.100000,1
17,1704067200,-47.0,-65.0,-38.0,68.90,32.00,1.200000,0
15,1704067200,-67.0,-57.0,-53.0,99.43,31.17,6.769995,2"""
        df = pd.read_csv(StringIO(simulated_csv_data))

    # We must check if df is None after all attempts
    if df is None or df.empty:
        print("Failed to load any data. Exiting.")
        sys.exit(1)

    # --- Renaming and Normalization (CRITICAL FIX) ---
    # 1. Normalize current column names (strip whitespace/special chars, lowercase)
    def normalize_col_name(col_name):
        # Convert to string, strip surrounding whitespace, and convert to lowercase
        return str(col_name).strip().lower().replace(" ", "")

    df.columns = [normalize_col_name(col) for col in df.columns]

    # 2. Rename based on the normalized map
    # We only rename columns that exist in the DataFrame AND are in our map
    rename_dict = {
        normalized_raw_name: clean_name
        for normalized_raw_name, clean_name in COLUMN_MAP.items()
        if normalized_raw_name in df.columns
    }

    if not rename_dict and not loaded_from_fallback:
        print("Error: Could not determine column names after normalization. Check the CSV headers.")
        print(f"Current columns in DataFrame: {df.columns.tolist()}")
        sys.exit(1)

    df.rename(columns=rename_dict, inplace=True)
    print("Columns renamed to match model feature list.")

except Exception as e:
    print(f"An unexpected error occurred during data loading or cleaning: {e}")
    sys.exit(1)


# --- 2. Preprocessing and Feature Engineering ---
# The features defined in the proposal: Orientation (x, y, z), Heart Rate, Skin Temp, EDA
features = ['Orientation_X', 'Orientation_Y', 'Orientation_Z', 'Heart_Rate', 'Skin_Temp', 'EDA']
target = 'Stress_Label'

# Now that 'df' is guaranteed to be defined and columns are correctly renamed,
# we can safely proceed with subsetting and training.
df = df.dropna(subset=features + [target])

# --- 3. Train Model (Upgraded to Gradient Boosting Classifier) ---
X = df[features]
y = df[target]

# Ensure there is enough data for split after dropna (especially with small fallback data)
if len(X) < 2:
    print("Not enough data to train the model after cleaning. Exiting.")
    sys.exit(1)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

print(f"Training GradientBoostingClassifier on {len(X_train)} records...")
# Using a more robust classifier with increased complexity for better predictive power.
model = GradientBoostingClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)
print("Training complete.")

# --- 4. Evaluation ---
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Test Accuracy: {accuracy:.4f}")

# --- 5. Save Model ---
model_filename = 'stress_prediction_model.joblib'
joblib.dump(model, model_filename)
print(f"Trained model saved successfully as '{model_filename}' for deployment.")

# --- 6. Output Feature List (Used by Kafka Producer) ---
# This list ensures the producer sends data in the correct order/format expected by the model.
print("\nModel Features for Stream Processor:")
print(features)
