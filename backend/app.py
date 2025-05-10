
import requests
import pandas as pd
import pickle
import torch
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
def fetch_walmart_product_data(product_url, api_key="681dfde09bb0db7be1b215df"):
    url = "https://api.scrapingdog.com/walmart/product"
    params = {
        "api_key": api_key,
        "url": product_url
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(data)
        return data
    else:
        print(f"Request failed with status code: {response.status_code}")
        return None

def extract_customer_reviews(data):
    reviews_results = data.get('reviews_results', {})
    reviews = reviews_results.get('reviews', {})
    customer_reviews = reviews.get('customer_reviews', [])

    review_data = []

    for review in customer_reviews:
        review_data.append({
            "User": review.get('user_nickname', 'Anonymous'),
            "Title": review.get('title', 'No Title'),
            "Text": review.get('text', 'No Review Text'),
            "Rating": review.get('rating', 'No Rating'),
            "Date": review.get('review_submission_time', 'No Submission Time')
        })

    df = pd.DataFrame(review_data)
    return df

def get_device():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    return device

def forward_pass(X_tensor, input_size, model_path, device):
    hidden_size = 768
    output_size = 2
    fc1 = torch.nn.Linear(input_size, hidden_size).to(device)
    relu = torch.nn.ReLU()
    fc2 = torch.nn.Linear(hidden_size, output_size).to(device)

    model_state = torch.load(model_path, map_location=device)
    model_dict = {
        'fc1.weight': model_state['fc1.weight'],
        'fc1.bias': model_state['fc1.bias'],
        'fc2.weight': model_state['fc2.weight'],
        'fc2.bias': model_state['fc2.bias']
    }

    fc1.weight.data.copy_(model_dict['fc1.weight'])
    fc1.bias.data.copy_(model_dict['fc1.bias'])
    fc2.weight.data.copy_(model_dict['fc2.weight'])
    fc2.bias.data.copy_(model_dict['fc2.bias'])

    with torch.no_grad():
        x = fc1(X_tensor)
        x = relu(x)
        x = fc2(x)
        y_pred = torch.argmax(x, axis=1).cpu().numpy()
    return y_pred

def classify_reviews_functional(df, text_column, vectorizer_path, model_path, label_mapping, output_column):
    device = get_device()

    with open(vectorizer_path, "rb") as f:
        tfidf = pickle.load(f)

    df[text_column] = df[text_column].fillna("")
    X = tfidf.transform(df[text_column]).toarray()
    input_size = X.shape[1]
    X_tensor = torch.tensor(X, dtype=torch.float32).to(device)

    y_pred_labels = forward_pass(X_tensor, input_size, model_path, device)

    df[output_column] = y_pred_labels
    df[output_column] = df[output_column].map(label_mapping)
    return df

def run_review_classification_pipeline(df):
    print("\n--- Classifying Extracted Customer Reviews ---")
    df = classify_reviews_functional(
        df=df,
        text_column='Text',
        vectorizer_path="/Users/vanshikashah/Desktop/crediboost-main/backend/ai detection model/tfidf_vectorizer.pkl",
        model_path="/Users/vanshikashah/Desktop/crediboost-main/backend/ai detection model/aiclassifier.pth",
        label_mapping={1: 'Fake', 0: 'Real'},
        output_column='AI_Classifier_Prediction'
    )

    df = classify_reviews_functional(
        df=df,
        text_column='Text',
        vectorizer_path="/Users/vanshikashah/Desktop/crediboost-main/backend/general detection model/tfidf_vectorizer1.pkl",
        model_path='/Users/vanshikashah/Desktop/crediboost-main/backend/general detection model/generalclassifier.pth',
        label_mapping={0: 'Fake', 1: 'Real'},
        output_column='General_Classifier_Prediction'
    )

    print(df[['Text', 'AI_Classifier_Prediction', 'General_Classifier_Prediction']])
    df.to_csv("extracted_customer_reviews_classified.csv", index=False)
    return df

def determine_label(row):
    if row['AI_Classifier_Prediction'] == 'Fake':
        return 'Fake'
    elif row['AI_Classifier_Prediction'] == 'Real' and row['General_Classifier_Prediction'] == 'Fake':
        return 'Fake'
    else:
        return 'Real'

def analyze_fake_review_impact(df, time_column='Date', label_column='Predicted_Label', date_format='%m/%d/%Y'):
    df[time_column] = pd.to_datetime(df[time_column], format=date_format, errors='coerce')
    df = df.sort_values(by=time_column)

    fake_entries = df[df[label_column] == 'Fake']
    real_entries = df[df[label_column] == 'Real']

    percent_changes = []

    for _, row in fake_entries.iterrows():
        start_date = row[time_column] - pd.Timedelta(days=15)
        end_date = row[time_column] + pd.Timedelta(days=15)

        count_before = df[(df[time_column] >= start_date) & (df[time_column] < row[time_column])].shape[0]
        count_after = df[(df[time_column] > row[time_column]) & (df[time_column] <= end_date)].shape[0]

        if count_before > 0:
            pct_change = ((count_after - count_before) / count_before) * 100
        else:
            pct_change = (count_after - count_before) * 100

        percent_changes.append(pct_change)

    fake_entries = fake_entries.copy()
    fake_entries['percent_change'] = percent_changes

    avgimpact = np.mean(percent_changes) if percent_changes else 0
    medianimpact = np.median(percent_changes) if percent_changes else 0
    nonzero = [i for i in percent_changes if i != 0]
    avgimpact_nonzero = np.mean(nonzero) if nonzero else 0
    medianimpact_nonzero = np.median(nonzero) if nonzero else 0

    print(fake_entries[[time_column, label_column, 'percent_change']])
    print(f"\nTotal reviews: {len(df)}")
    print(f"Real reviews: {len(real_entries)}")
    print(f"Fake reviews: {len(fake_entries)}")
    print(f"Average Impact: {avgimpact:.2f}%")
    print(f"Median Impact: {medianimpact:.2f}%")
    print(f"Non-zero percent change count: {len(nonzero)}")
    print(f"Avg. impact (excluding zero): {avgimpact_nonzero:.2f}%")
    print(f"Median impact (excluding zero): {medianimpact_nonzero:.2f}%")

    return {
        'total_reviews': len(df),
        'real_reviews': len(real_entries),
        'fake_reviews': len(fake_entries),
        'avg_impact': avgimpact,
        'median_impact': medianimpact,
        'avg_impact_nonzero': avgimpact_nonzero,
        'median_impact_nonzero': medianimpact_nonzero,
        'nonzero_count': len(nonzero)
    }

app = Flask(__name__)
CORS(app)
@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        print("Received data:", data)
        url = data.get('url')

        if not url:
            return jsonify({"error": "Missing product URL"}), 400

        maindata = fetch_walmart_product_data(url)
        maindf = extract_customer_reviews(maindata)
        maindf = run_review_classification_pipeline(maindf)
        maindf['Predicted_Label'] = maindf.apply(determine_label, axis=1)
        impact = analyze_fake_review_impact(maindf)

        # Convert DataFrame to JSON-friendly format (list of dicts)
        review_data = maindf[[
            'User', 'Title', 'Text',
            'AI_Classifier_Prediction',
            'General_Classifier_Prediction',
            'Predicted_Label'
        ]].to_dict(orient='records')  # Convert to a list of dictionaries

        return jsonify({
            "impact_analysis": impact
        })

    except Exception as e:
        # Print full traceback to console for debugging
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
