from fastapi import FastAPI, HTTPException
import pandas as pd
import torch
import torch.nn.functional as F
import os

DATA_DIR = os.getenv('DATA_DIR', '../ml/data')

app = FastAPI(title="Smart Shop Assistant API")

# Load the data once when server is started
products = pd.read_csv(f'{DATA_DIR}/products_clean.csv')

# Load the business insights data
category_sentiment = pd.read_csv(f'{DATA_DIR}/category_sentiment_summary.csv')
category_ratings = pd.read_csv(f'{DATA_DIR}/category_ratings_summary.csv')

# Ready the one-hot matrix (same as in notebook)
category_encoded = pd.get_dummies(products['product_category_name_english'])
category_matrix = torch.tensor(category_encoded.values.astype(float), dtype=torch.float32)

print(f"API started. Loaded {len(products)} products.")


@app.get("/")
def read_root():
    return {"message": "Smart Shop Assistant API работи!"}


@app.get("/recommendations/{product_id}")
def get_recommendations(product_id: str, top_n: int = 5):
    # Find the index of the product by using product_id
    matches = products.index[products['product_id'] == product_id]
    
    if len(matches) == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product_index = matches[0]
    
    # Sme logic as in notebook
    target_vector = category_matrix[product_index].unsqueeze(0)
    similarities = F.cosine_similarity(target_vector, category_matrix, dim=1)
    
    sorted_indices = similarities.argsort(descending=True)
    sorted_indices = sorted_indices[sorted_indices != product_index]
    top_indices = sorted_indices[:top_n]
    
    recommended = products.iloc[top_indices.numpy()]
    
    return {
        "product_id": product_id,
        "category": products.iloc[product_index]['product_category_name_english'],
        "recommendations": recommended.to_dict(orient='records')
    }

@app.get("/insights/categories")
def get_category_insights():
    # Combine the two tables (sentiment + звезди) by catgegories
    combined = category_ratings.merge(category_sentiment, on='category', how='inner')
    combined = combined.sort_values('avg_sentiment_score')
    
    return {
        "categories": combined.to_dict(orient='records')
    }

@app.get("/insights/categories/{category_name}")
def get_single_category_insight(category_name: str):
    rating_row = category_ratings[category_ratings['category'] == category_name]
    sentiment_row = category_sentiment[category_sentiment['category'] == category_name]
    
    if len(rating_row) == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    
    result = {"category": category_name}
    result.update(rating_row.iloc[0].to_dict())
    if len(sentiment_row) > 0:
        result.update(sentiment_row.iloc[0].to_dict())
    
    return result