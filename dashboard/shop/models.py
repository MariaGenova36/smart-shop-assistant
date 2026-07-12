from django.db import models


class Product(models.Model):
    product_id = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product_id} ({self.category})"


class CategoryInsight(models.Model):
    category = models.CharField(max_length=100, unique=True)
    avg_review_score = models.FloatField()
    order_count = models.IntegerField()
    avg_sentiment_score = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.category