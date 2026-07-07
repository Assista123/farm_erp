from django.core.management.base import BaseCommand
from core.models import ShopProduct, ProductTypeThreshold


class Command(BaseCommand):
    help = 'Set reorder thresholds on existing ShopProduct records based on ProductTypeThreshold settings'

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

        for product in ShopProduct.objects.all():
            if product.product_type in thresholds:
                product.reorder_threshold = thresholds[product.product_type]
                product.save(update_fields=['reorder_threshold'])
                updated += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'Done. Updated: {updated} records. Skipped: {skipped} records.'
        ))