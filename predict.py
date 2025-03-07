import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
from collections import Counter
from services import datamanager

# Preprocessing function
def preprocess(text):
    # Convert to string and handle None or NaN
    text_str = str(text) if pd.notnull(text) else ""
    return text_str.lower().strip()

def is_valid_zip_code(input_str):
    # Check for 5-digit or 9-digit ZIP+4 format
    return bool(re.match(r'^\d{5}(-\d{4})?$', input_str))

# Load training data from CSV
training_csv_path = r"assets/trainingdata.csv"  # Path to training CSV
df_train = pd.read_csv(training_csv_path)
df_train['text'] = df_train['text'].apply(preprocess)

# Split into training and test sets with stratification
X_train, X_test, y_train, y_test = train_test_split(df_train['text'], df_train['label'], test_size=0.2, random_state=42, stratify=df_train['label'])

# Build pipeline with Random Forest
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(lowercase=True, ngram_range=(1, 5), analyzer='char', max_features=5000)),
    ('clf', RandomForestClassifier(n_estimators=200, random_state=42))
])

# Train the model
pipeline.fit(X_train, y_train)

# Evaluate the model
y_pred = pipeline.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, y_pred, zero_division=1))  # Set zero_division to 1 to avoid warnings

# load state data for better predictions
state_abbreviations, state_full_names = datamanager.get_reference_data('assets/states.csv')

# load country data for better predictions
country_abbreviations, country_full_names = datamanager.get_reference_data('assets/country.csv')

# Prediction function with debugging
def predict_input_type(user_input):
    processed_input = preprocess(user_input)
    if re.match(r'^\d+$', processed_input) and len(processed_input) != 5:
        prediction = "Number"
        confidence = 1.0  # Assign high confidence to rule-based decision
    elif processed_input.upper() in state_abbreviations or processed_input.upper() in state_full_names:
        prediction = "State"
        confidence = 1.0  # Assign high confidence to rule-based decision
    elif processed_input.upper() in country_abbreviations or processed_input.upper() in country_full_names:
        prediction = "Country"
        confidence = 1.0  # Assign high confidence to rule-based decision
    elif is_valid_zip_code(processed_input):
        prediction = "Zip"
        confidence = 1.0  # Assign high confidence to rule-based decision
    else:
        prediction = pipeline.predict([processed_input])[0]
        confidence = max(pipeline.predict_proba([processed_input])[0])
        if confidence < .30:
            prediction = 'Unknown'
    #print(processed_input)
    #print(prediction)
    #print(confidence)
    return prediction, confidence

# Test the model with dynamic CSV column consensus
def predict(csv_file):
    df = pd.read_csv(csv_file, dtype=str)
    print(f"\nColumn consensus from CSV file: {csv_file}")

    # Dictionary to store predictions for each column
    column_predictions = {col: [] for col in df.columns}

    # Collect predictions for each non-null value in each column
    for column in df.columns:
        non_null_values = df[column].dropna()
        for value in non_null_values:
            prediction, confidence = predict_input_type(value)
            column_predictions[column].append((prediction, confidence))

    # Calculate consensus for each column and print result
    predictions_dic = {}
    for column in column_predictions:
        if column_predictions[column]:  # Only process if there are predictions
            predictions = [pred for pred, _ in column_predictions[column]]
            consensus = Counter(predictions).most_common(1)[0][0]  # Most common prediction
            print(f"Column: {column} -> Predicted Type: {consensus}")
            predictions_dic[column] = consensus
    return predictions_dic