import pandas as pd
from django.core.management.base import BaseCommand
from shop.models import Product, CategoryInsight


class Command(BaseCommand):
    help = 'Loading data from CSV files in the data base'

    def handle(self, *args, **options):
        # Изчистваме старите данни, ако има такива (за да не дублираме при повторно пускане)
        Product.objects.all().delete()
        CategoryInsight.objects.all().delete()

        # --- Зареждаме продуктите ---
        products_df = pd.read_csv('../ml/data/products_clean.csv')
        
        products_to_create = [
            Product(
                product_id=row['product_id'],
                category=row['product_category_name_english']
            )
            for _, row in products_df.iterrows()
        ]
        Product.objects.bulk_create(products_to_create)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(products_to_create)} files'))

        # --- Зареждаме category insights ---
        ratings_df = pd.read_csv('../ml/data/category_ratings_summary.csv')
        sentiment_df = pd.read_csv('../ml/data/category_sentiment_summary.csv')
        
        combined_df = ratings_df.merge(sentiment_df, on='category', how='left')

        insights_to_create = [
            CategoryInsight(
                category=row['category'],
                avg_review_score=row['avg_review_score'],
                order_count=row['order_count'],
                avg_sentiment_score=row['avg_sentiment_score'] if pd.notna(row['avg_sentiment_score']) else None,
                review_count=row['review_count'] if pd.notna(row['review_count']) else None
            )
            for _, row in combined_df.iterrows()
        ]
        CategoryInsight.objects.bulk_create(insights_to_create)
        self.stdout.write(self.style.SUCCESS(f'Loaded {len(insights_to_create)} categories'))