from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import (
    Flock,
    FlockPlacement,
    FeedProcurementItem,
    FeedStockMovement,
    FeedStock,
    DrugPurchaseItem,
    DrugStockMovement,
    DrugStock,
    MortalityRecord,
    MortalityRecordItem,
    EggGrading,
    ManureLog,
    ShopStockMovement,
    ShopStock,
    ShopProduct,
    ShopSale,
    ShopSaleItem,
    ShopDelivery,
    OldLayerSale,
    WorkerSalary,
    ProductTypeThreshold,
    CustomerOrder,
    CustomerDeposit,
)

# ── FLOCK ────────────────────────────────────────────────────────────────────
@receiver(post_save, sender=Flock)
def set_initial_flock_count(sender, instance, created, **kwargs):
    if created:
        Flock.objects.filter(pk=instance.pk).update(
            current_count=instance.initial_count
        )

# ── FLOCK PLACEMENT ──────────────────────────────────────────────────────────
@receiver(post_save, sender=FlockPlacement)
def compute_placement_total_cost(sender, instance, **kwargs):
    total = instance.quantity_received * instance.cost_per_bird
    FlockPlacement.objects.filter(pk=instance.pk).update(total_cost=total)

# ── FEED PROCUREMENT ITEM ─────────────────────────────────────────────────────
@receiver(post_save, sender=FeedProcurementItem)
def compute_procurement_item_total_cost(sender, instance, **kwargs):
    total = instance.quantity_ordered * instance.price_per_bag
    FeedProcurementItem.objects.filter(pk=instance.pk).update(total_cost=total)

# ── FEED STOCK MOVEMENT ───────────────────────────────────────────────────────
@receiver(post_save, sender=FeedStockMovement)
def update_feed_stock_balance(sender, instance, created, **kwargs):
    if created:
        stock = instance.feed_stock
        if instance.movement_type == 'in':
            new_balance = stock.current_balance + instance.quantity
        else:
            new_balance = stock.current_balance - instance.quantity

        new_balance = max(0, new_balance)

        FeedStockMovement.objects.filter(pk=instance.pk).update(
            balance_after=new_balance
        )
        FeedStock.objects.filter(pk=stock.pk).update(
            current_balance=new_balance,
        )

# ── DRUG PURCHASE ITEM ────────────────────────────────────────────────────────
@receiver(post_save, sender=DrugPurchaseItem)
def compute_drug_purchase_item_total_cost(sender, instance, **kwargs):
    total = instance.quantity_purchased * instance.cost_per_unit
    DrugPurchaseItem.objects.filter(pk=instance.pk).update(total_cost=total)

# ── DRUG STOCK MOVEMENT ───────────────────────────────────────────────────────
@receiver(post_save, sender=DrugStockMovement)
def update_drug_stock_balance(sender, instance, created, **kwargs):
    if created:
        stock = instance.drug_stock
        if instance.movement_type == 'in':
            new_balance = stock.current_quantity + instance.quantity
        else:
            new_balance = stock.current_quantity - instance.quantity

        new_balance = max(new_balance, 0)

        DrugStockMovement.objects.filter(pk=instance.pk).update(
            balance_after=new_balance
        )
        DrugStock.objects.filter(pk=stock.pk).update(
            current_quantity=new_balance,
        )

# ── MORTALITY RECORD ITEM ─────────────────────────────────────────────────────
@receiver(post_save, sender=MortalityRecordItem)
def update_mortality_total_count(sender, instance, **kwargs):
    from django.db.models import Sum
    record = instance.mortality_record
    total = record.items.aggregate(Sum('count'))['count__sum'] or 0
    THRESHOLD = 5
    is_high = total >= THRESHOLD
    MortalityRecord.objects.filter(pk=record.pk).update(
        total_count=total,
        is_high_mortality=is_high
    )
    flock = record.flock
    new_count = max(flock.current_count - instance.count, 0)
    Flock.objects.filter(pk=flock.pk).update(current_count=new_count)

# ── EGG GRADING ───────────────────────────────────────────────────────────────
@receiver(post_save, sender=EggGrading)
def compute_egg_grading_totals(sender, instance, **kwargs):
    from django.db.models import Sum
    from .models import EggCollection
    total_graded = instance.whole_eggs + instance.broken_eggs
    total_collected = EggCollection.objects.filter(
        collection_date=instance.grading_date
    ).aggregate(Sum('observed_count'))['observed_count__sum'] or 0
    discrepancy = total_graded - total_collected
    EggGrading.objects.filter(pk=instance.pk).update(
        total_graded=total_graded,
        total_collected=total_collected,
        grading_discrepancy=discrepancy
    )

# ── MANURE LOG ────────────────────────────────────────────────────────────────
@receiver(post_save, sender=ManureLog)
def compute_manure_total_revenue(sender, instance, **kwargs):
    if instance.bags_sold and instance.price_per_bag:
        total = instance.bags_sold * instance.price_per_bag
        ManureLog.objects.filter(pk=instance.pk).update(total_revenue=total)

# ── SHOP PRODUCT ──────────────────────────────────────────────────────────────
@receiver(post_save, sender=ShopProduct)
def create_shop_stock_for_product(sender, instance, created, **kwargs):
    if created:
        ShopStock.objects.get_or_create(
            product=instance,
            defaults={'current_quantity': 0}
        )

# ── SHOP STOCK MOVEMENT ───────────────────────────────────────────────────────
@receiver(post_save, sender=ShopStockMovement)
def update_shop_stock_balance(sender, instance, created, **kwargs):
    if created:
        stock = instance.shop_stock
        if instance.movement_type == 'in':
            new_balance = stock.current_quantity + instance.quantity
        else:
            new_balance = stock.current_quantity - instance.quantity

        new_balance = max(new_balance, 0)

        ShopStockMovement.objects.filter(pk=instance.pk).update(
            balance_after=new_balance
        )

        update_fields = {'current_quantity': new_balance}
        if instance.movement_type == 'in':
            update_fields['current_batch_number'] = instance.batch_number or ''
            update_fields['current_expiry_date'] = instance.expiry_date

        ShopStock.objects.filter(pk=stock.pk).update(**update_fields)


@receiver(post_delete, sender=ShopStockMovement)
def recalculate_shop_stock_on_delete(sender, instance, **kwargs):
    instance.shop_stock.recalculate_balance()


# ── SHOP SALE ITEM ────────────────────────────────────────────────────────────
@receiver(post_save, sender=ShopSaleItem)
def compute_shop_sale_item_totals(sender, instance, created, **kwargs):
    if created:
        from django.db.models import Sum

        # Respect pre-set price (e.g. from customer order agreed price)
        if instance.price_per_unit and instance.price_per_unit > 0:
            price_per_unit = instance.price_per_unit
            pricing_type = 'agreed'
        else:
            pricing_type = 'wholesale' if instance.quantity >= instance.product.wholesale_threshold else 'retail'
            price_per_unit = instance.product.wholesale_price if pricing_type == 'wholesale' else instance.product.retail_price

        gross_total = instance.quantity * price_per_unit

        # Apply discount using fixed amount per unit
        if instance.discount_applied:
            fixed = instance.product.discount_fixed_amount
            if fixed and fixed > 0:
                discount_amount = fixed * instance.quantity
            else:
                discount_amount = 0
        else:
            discount_amount = 0

        total = gross_total - discount_amount

        if instance.quantity_delivered_at_sale >= instance.quantity:
            delivery_status = 'complete'
            quantity_delivered = instance.quantity
        elif instance.quantity_delivered_at_sale > 0:
            delivery_status = 'partial'
            quantity_delivered = instance.quantity_delivered_at_sale
        else:
            delivery_status = 'pending'
            quantity_delivered = 0

        ShopSaleItem.objects.filter(pk=instance.pk).update(
            price_per_unit=price_per_unit,
            pricing_type=pricing_type,
            total_amount=total,
            discount_amount=discount_amount,
            delivery_status=delivery_status,
            quantity_delivered=quantity_delivered
        )

        # Create initial delivery record for partial delivery only
        if 0 < instance.quantity_delivered_at_sale < instance.quantity:
            ShopDelivery.objects.create(
                sale_item=instance,
                delivery_date=instance.sale.sale_date,
                quantity_delivered=instance.quantity_delivered_at_sale,
                delivered_by=instance.sale.recorded_by,
                notes='Initial delivery at point of sale'
            )

        # Auto-reduce shop stock on sale
        try:
            shop_stock = ShopStock.objects.get(product=instance.product)
            ShopStockMovement.objects.create(
                shop_stock=shop_stock,
                movement_type='out',
                movement_reason='sale',
                quantity=instance.quantity,
                recorded_by=instance.sale.recorded_by,
                notes=f'Auto: Sale #{instance.sale.pk}'
            )
        except ShopStock.DoesNotExist:
            pass

        # Update parent ShopSale total and delivery_status
        sale = instance.sale
        new_total = sale.items.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        all_statuses = list(
            sale.items.exclude(pk=instance.pk).values_list('delivery_status', flat=True)
        ) + [delivery_status]

        if all(s == 'complete' for s in all_statuses):
            sale_status = 'complete'
        elif all(s == 'pending' for s in all_statuses):
            sale_status = 'pending'
        else:
            sale_status = 'partial'

        ShopSale.objects.filter(pk=sale.pk).update(
            total_amount=new_total,
            delivery_status=sale_status
        )


# ── SHOP DELIVERY ─────────────────────────────────────────────────────────────
@receiver(post_save, sender=ShopDelivery)
def update_sale_item_delivery_status(sender, instance, **kwargs):
    from django.db.models import Sum
    sale_item = instance.sale_item
    total_delivered = sale_item.deliveries.aggregate(
        Sum('quantity_delivered'))['quantity_delivered__sum'] or 0

    if total_delivered == 0:
        status = 'pending'
    elif total_delivered >= sale_item.quantity:
        status = 'complete'
    else:
        status = 'partial'

    ShopSaleItem.objects.filter(pk=sale_item.pk).update(
        quantity_delivered=total_delivered,
        delivery_status=status
    )

    sale = sale_item.sale
    all_statuses = list(sale.items.values_list('delivery_status', flat=True))

    if all(s == 'complete' for s in all_statuses):
        sale_status = 'complete'
    elif all(s == 'pending' for s in all_statuses):
        sale_status = 'pending'
    else:
        sale_status = 'partial'

    ShopSale.objects.filter(pk=sale.pk).update(delivery_status=sale_status)


# ── OLD LAYER SALE ────────────────────────────────────────────────────────────
@receiver(post_save, sender=OldLayerSale)
def compute_old_layer_sale_total(sender, instance, **kwargs):
    total = instance.quantity_sold * instance.price_per_bird
    OldLayerSale.objects.filter(pk=instance.pk).update(total_amount=total)


# ── WORKER SALARY ─────────────────────────────────────────────────────────────
@receiver(post_save, sender=WorkerSalary)
def compute_net_salary(instance, **kwargs):
    net = instance.basic_salary + instance.allowances - instance.deductions
    WorkerSalary.objects.filter(pk=instance.pk).update(net_salary=net)


# ── CUSTOMER DEPOSIT ──────────────────────────────────────────────────────────
@receiver(post_save, sender=CustomerDeposit)
def update_customer_order_status(sender, instance, **kwargs):
    order = instance.order

    # Only the release view controls these statuses — never override them
    if order.status in ['partially_released', 'completed', 'cancelled']:
        return

    total = order.total_deposited
    if total <= 0:
        status = 'pending'
    else:
        status = 'partially_paid'

    CustomerOrder.objects.filter(pk=order.pk).update(status=status)