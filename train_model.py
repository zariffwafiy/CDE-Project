from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Sample data: Abbreviations and their full forms
data = [
    ("I like using NLP.", "NLP", "technology"),
    ("The DNA sequence is complex.", "DNA", "biology"),
    # Add more examples with different classes here
]

# Split the data into training and testing sets
train_data, test_data = train_test_split(data, test_size=0.2, random_state=42)

# Extract features and labels
train_texts, train_labels, train_expansions = zip(*train_data)
test_texts, test_labels, test_expansions = zip(*test_data)

# Convert labels to binary format
mlb = MultiLabelBinarizer()
train_labels_bin = mlb.fit_transform([[label] for label in train_expansions])
test_labels_bin = mlb.transform([[label] for label in test_expansions])

# Vectorize the text data using TfidfVectorizer
vectorizer = TfidfVectorizer(preprocessor=preprocess)
train_texts_vectorized = vectorizer.fit_transform(train_texts)
test_texts_vectorized = vectorizer.transform(test_texts)

# Create a pipeline with a neural network
model = MLPClassifier(
    hidden_layer_sizes=(100,),  # Adjust the architecture based on your task
    max_iter=100,
    random_state=42,
)

# Fit the model
model.fit(train_texts_vectorized, train_labels_bin)

# Evaluate the model
predictions_bin = model.predict(test_texts_vectorized)

# Display classification report
print("Classification Report:\n", classification_report(test_labels_bin, predictions_bin, target_names=mlb.classes_))
