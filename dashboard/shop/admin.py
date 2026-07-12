from django.contrib import admin
from .models import Product, CategoryInsight


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'category')
    list_filter = ('category',)
    search_fields = ('product_id', 'category')


@admin.register(CategoryInsight)
class CategoryInsightAdmin(admin.ModelAdmin):
    list_display = ('category', 'avg_review_score', 'order_count', 'avg_sentiment_score', 'review_count')
    ordering = ('avg_sentiment_score',)
    search_fields = ('category',)