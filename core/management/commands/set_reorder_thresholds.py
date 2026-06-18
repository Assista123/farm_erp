from django.core.management.base import BaseCommand
from core.models import ShopStock, ProductTypeThreshold


class Command(BaseCommand):
    help = 'Set reorder thresholds on existing ShopStock records based on ProductTypeThreshold settings'

    def handle(self, *args, **kwargs):
        thresholds = {
            t.product_type: t.reorder_threshold
            for t in ProductTypeThreshold.objects.all()
        }

        if not thresholds:
            self.stdout.write(self.style.WARNING(
                'No ProductTypeThreshold records found. '
                'Please set them in the admin panel first.'
            ))
            return

        updated = 0
        skipped = 0

        for stock in ShopStock.objects.select_related('product').all():
            product_type = stock.product.product_type
            if product_type in thresholds:
                stock.reorder_threshold = thresholds[product_type]
                stock.save(update_fields=['reorder_threshold'])
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Updated: {updated} records. Skipped: {skipped} records.'
        ))