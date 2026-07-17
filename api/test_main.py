from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Verifies the root endpoint responds successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_category_insights_returns_success():
    """Verifies the category insights endpoint returns a successful response."""
    response = client.get("/insights/categories")
    assert response.status_code == 200


def test_recommendations_invalid_product_returns_404():
    """Verifies requesting recommendations for a non-existent product returns 404."""
    response = client.get("/recommendations/this-id-does-not-exist")
    assert response.status_code == 404


def test_category_insights_response_structure():
    """Verifies the insights response contains the expected fields."""
    response = client.get("/insights/categories")
    data = response.json()

    assert "categories" in data
    assert len(data["categories"]) > 0

    first_category = data["categories"][0]
    assert "category" in first_category
    assert "avg_review_score" in first_category


def test_single_category_not_found_returns_404():
    """Verifies requesting a non-existent category returns 404."""
    response = client.get("/insights/categories/not_a_real_category")
    assert response.status_code == 404