from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# Farm Unit Model
class FarmUnit(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


#  Pen Model
class Pen(models.Model):
    name = models.CharField(max_length=100)
    farm_unit = models.ForeignKey(
        FarmUnit,
        on_delete=models.PROTECT,
        related_name='pens'
    )
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.farm_unit.name} - {self.name}"


    # Worker Model
class Worker(models.Model):
    ROLE_CHOICES = [
    ('pen_workers', 'Pen Worker'),
    ('supervisor', 'Supervisor'),
    ('store_keeper', 'Store Keeper'),
    ('manager', 'Farm Mamager'),
    ('general_manager', 'General Manager'),
    ('salesperson','Salesperson'),
    ('accountant', 'Accountant'),
    ('director', 'Director'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_profile'
    )
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50, choices = ROLE_CHOICES)
    phone = models.CharField()
    date_joined = models.DateField()
    is_active = models.BooleanField(default=True)
        
    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
    

# PenWorkerAssignment Model
class PenWorkerAssignment(models.Model):
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='worker_assignments'
    )
    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='pen_assignments'
    )
    assigned_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['pen', 'worker']

    def __str__(self):
        return f"{self.worker.full_name} -> {self.pen.name}"


# Flock Model
class Flock(models.Model):
    BIRD_TYPE_CHOICES = [
        ('layer', 'Layer'),
        ('broiler', 'Broiler'),
    ]

    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='flocks'
    )

    bird_type = models.CharField(max_length=20, choices=BIRD_TYPE_CHOICES)
    initial_count = models.PositiveIntegerField()
    current_count = models.PositiveIntegerField(editable=False, default=0)
    date_placed = models.DateField() 
    date_removed = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_bird_type_display()} - {self.pen.name} ({self.date_placed})"


# Supplier Model
class Supplier(models.Model):
    SUPPLIER_TYPE_CHOICES = [
        ('feed', 'Feed'),
        ('birds', 'Birds'),
        ('drugs', 'Drugs'),
        ('mixed', 'Mixed'),
    ]

    name = models.CharField(max_length=200)
    supplier_type = models.CharField(max_length=20, choices=SUPPLIER_TYPE_CHOICES)
    supplier_type_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe supplier type if you selected Other above"
)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_supplier_type_display()})"


# FlockPlacement Model
class FlockPlacement(models.Model):
    flock = models.OneToOneField(
        Flock,
        on_delete=models.PROTECT,
        related_name="placement"
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='placements_recorded'
    )
    quantity_received = models.PositiveIntegerField()
    cost_per_bird = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0)
    placement_date = models.DateField()
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='placements_recorded'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.flock} - {self.placement_date}"


# FeedType Model
class FeedType(models.Model):
    FEED_TYPE_CHOICES = [
        ('layers_mash', 'Layer Mash'),
        ('broiler_starter', 'Broiler Starter'),
        ('broiler_finisher', 'Broiler Finisher'),
        ('grower_mash', 'Grower Mash'),
        ('other', 'other')

    ]

    name = models.CharField(max_length=100, choices=FEED_TYPE_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.get_name_display()


# DrugAndSupplement Class
class DrugAndSupplement(models.Model):
    TREATMENT_TYPE_CHOICES = [
        ('vitamin', 'Vitamin'),
        ('antibiotics', 'Antibiotics'),
        ('vaccine', 'Vaccine'),
        ('electrolyte', 'Electrolyte'),
        ('others', 'Others'),
    ]
    name = models.CharField(max_length=200)
    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES)
    default_dosage_unit = models.CharField(max_length=50, blank=True, help_text="Unit of measurement for this product e.g. ml, g, stachets, vials")
    manufacturer = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_treatment_type_display()})"


# FeedProcurement
class FeedProcurement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partially_delivered', 'Partially Delivered'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='feed_procurements'
    )
    order_date = models.DateField()
    expected_delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending')
    ordered_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feed_orders_placed'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.supplier.name} ({self.get_status_display()})"

# FeedProcurementItem
class FeedProcurementItem(models.Model):
    procurement = models.ForeignKey(
        FeedProcurement,
        on_delete=models.CASCADE,
        related_name='items'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='procurement_items'
    )
    quantity_ordered = models.PositiveIntegerField()
    bag_size_kg = models.PositiveIntegerField(
        help_text="Weight of each bag in kilograms e.g. 25 or 50"
    )
    price_per_bag = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0
    )

    def __str__(self):
        return f'{self.feed_type} - {self.quantity_ordered} bags'


# FeedPayment Model
class FeedPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]

    procurement = models.ForeignKey(
        FeedProcurement,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    payment_date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )
    paid_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feed_payments_made'
    )
    received_by = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of supplier representative who received payment"
    )
    receipt_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Receipt or transaction reference number"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of {self.amount_paid} for Order #{self.procurement.id} on {self.payment_date}"


# FeedDelivery Model
class FeedDelivery(models.Model):
    procurement = models.ForeignKey(
        FeedProcurement,
        on_delete=models.PROTECT,
        related_name='deliveries'
    )
    delivery_date = models.DateField()
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Supplier invoice or waybill reference for this delivery trip"
    )
    delivery_confirmed_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='deliveries_confirmed'
    )
    received_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery for Order #{self.procurement.id} on {self.delivery_date}"

# FeedDeliveryItem
class FeedDeliveryItem(models.Model):
    delivery = models.ForeignKey(
        FeedDelivery,
        on_delete=models.CASCADE,
        related_name='items'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='delivery_items'
    )
    quantity_received = models.PositiveIntegerField()
    quantity_rejected = models.PositiveIntegerField(default=0)
    rejection_reason = models.TextField(
        blank=True,
        help_text="Explain why bags were rejected if any"
    )

    def __str__(self):
        return f"{self.feed_type} - {self.quantity_received} bags received"


# FeedStock Model
class FeedStock(models.Model):
    feed_type = models.OneToOneField(
        FeedType,
        on_delete=models.PROTECT,
        related_name='stock'
    )
    current_balance = models.PositiveIntegerField(
        default=0,
        editable=False,
        help_text="Auto-updated by system on every stock movement"
    )
    reorder_threshold = models.PositiveIntegerField(
        default=0,
        help_text="Minimum number of bags before a low stock alert is triggered"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.feed_type.get_name_display()} - {self.current_balance} bags"



# FeedStockMovement Model
class FeedStockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'IN'),
        ('out', 'OUT'),
    ]

    MOVEMENT_REASON_CHOICES = [
        ('delivery', 'Delivery'),
        ('issuance', 'Issuance'),
        ('adjustment', 'Adjustment'),
        ('damaged', 'Damaged'),
        ('other', 'Other'),
    ]

    REFERENCE_TYPE_CHOICES = [
        ('delivery', 'Delivery'),
        ('issuance', 'Issuance'),
        ('manual', 'Manual'),
    ]

    feed_stock = models.ForeignKey(
        FeedStock,
        on_delete=models.PROTECT,
        related_name='movements'
    )
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    movement_reason = models.CharField(max_length=20, choices=MOVEMENT_REASON_CHOICES)
    
    movement_reason_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe movement reason if you selected Other above"
    )
    quantity = models.PositiveIntegerField()
    balance_after = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Stock balance immediately after this movement — set automatically"
    )
    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE_CHOICES,
        blank=True
    )
    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the linked Delivery or Issuance record"
    )
    adjustment_reason = models.TextField(
        blank=True,
        help_text="Required when movement reason is Adjustment"
    )
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='stock_adjustments_authorized',
        null=True,
        blank=True,
        help_text="Required for Adjustment movements"
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='stock_movements_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.quantity} bags of {self.feed_stock.feed_type} on {self.recorded_at.date()}"


# FeedIssuance Model
class FeedIssuance(models.Model):
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='feed_issuances'
    )
    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='feed_issuances'
    )
    issuance_date = models.DateField()
    issued_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feed_issuances_made'
    )
    received_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feed_issuances_received'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Issuance to {self.pen.name} on {self.issuance_date}"



#FeedIssuanceItem
class FeedIssuanceItem(models.Model):
    issuance = models.ForeignKey(
        FeedIssuance,
        on_delete=models.CASCADE,
        related_name='items'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='issuance_items'
    )
    bags_issued = models.PositiveIntegerField()

    def str(self):
        return f"{self.feed_type} - {self.bags_issued} bags"



# PenFeedingActivity Model
class PenFeedingActivity(models.Model):
    LEFTOVER_ACTION_CHOICES = [
        ('added_on_top', 'Added on Top'),
        ('removed_first', 'Removed First'),
        ('reduced_ration', 'Reduced Ration'),
        ('nothing_done', 'Nothing Done'),
    ]

    issuance = models.ForeignKey(
        FeedIssuance,
        on_delete=models.PROTECT,
        related_name='feeding_activities'
    )
    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='feeding_activities'
    )
    feeding_date = models.DateField()
    leftover_observed = models.BooleanField(default=False)
    leftover_action = models.CharField(
        max_length=20,
        choices=LEFTOVER_ACTION_CHOICES,
        blank=True
    )
    fed_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feeding_activities'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Feeding - {self.flock} on {self.feeding_date}"



# PenFeedingActivityItem Model
class PenFeedingActivityItem(models.Model):
    feeding_activity = models.ForeignKey(
        PenFeedingActivity,
        on_delete=models.CASCADE,
        related_name='items'
    )
    feed_type = models.ForeignKey(
        FeedType,
        on_delete=models.PROTECT,
        related_name='feeding_activity_items'
    )
    bags_used = models.PositiveIntegerField()
    empty_bags_returned = models.PositiveIntegerField(default=0)
    bags_discrepancy = models.IntegerField(
        default=0,
        editable=False,
        help_text="Computed: bags_used minus empty_bags_returned — set automatically"
    )

    def __str__(self):
        return f"{self.feed_type} - {self.bags_used} bags used"



# PenFeedingSupervisor Model
class PenFeedingSupervision(models.Model):
    TROUGH_CONDITION_CHOICES = [
        ('good', 'Good'),
        ('damaged', 'Damaged'),
        ('needs_attention', 'Needs Attention'),
    ]

    BIRD_BEHAVIOR_CHOICES = [
        ('normal', 'Normal'),
        ('not_eating', 'Not Eating'),
        ('lethargic', 'Lethargic'),
        ('aggressive', 'Aggressive'),
        ('other', 'Other'),
    ]

    CONFIRMATION_STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('flagged', 'Flagged'),
        ('rejected', 'Rejected'),
    ]

    feeding_activity = models.OneToOneField(
        PenFeedingActivity,
        on_delete=models.PROTECT,
        related_name='supervision'
    )
    distribution_even = models.BooleanField(default=False)
    trough_condition = models.CharField(max_length=20, choices=TROUGH_CONDITION_CHOICES)
    bird_behavior = models.CharField(max_length=20, choices=BIRD_BEHAVIOR_CHOICES)
    bird_behavior_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe bird behavior if you selected Other above"
    )
    confirmation_status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS_CHOICES,
        default='confirmed'
    )
    supervised_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='feeding_supervisions'
    )
    supervised_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Supervision - {self.feeding_activity} ({self.get_confirmation_status_display()})"


# DrugStock Model
class DrugStock(models.Model):
    drug = models.OneToOneField(
        DrugAndSupplement,
        on_delete=models.PROTECT,
        related_name='stock'
    )
    current_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False,
        help_text="Auto-updated by system on every stock movement"
    )
    quantity_unit = models.CharField(
        max_length=50,
        help_text="e.g. ml, g, sachets, vials"
    )
    reorder_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Minimum quantity before low stock alert is triggered"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.drug.name} - {self.current_quantity}{self.quantity_unit}"



# DrugPurchaseOrder Model
class DrugPurchaseOrder(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='drug_purchase_orders'
    )
    purchase_date = models.DateField()
    purchased_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='drug_orders_made'
    )
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='drug_orders_authorized'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Drug Order #{self.id} - {self.supplier.name} on {self.purchase_date}"


# DrugPurchaseItem Model
class DrugPurchaseItem(models.Model):
    purchase_order = models.ForeignKey(
        DrugPurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    drug = models.ForeignKey(
        DrugAndSupplement,
        on_delete=models.PROTECT,
        related_name='purchase_items'
    )
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_unit = models.CharField(
        max_length=50,
        help_text="e.g. ml, g, sachets, vials"
    )
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Computed: quantity_purchased x cost_per_unit"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date on this specific batch"
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Supplier batch reference for traceability"
    )

    def __str__(self):
        return f"{self.drug.name} - {self.quantity_purchased}{self.quantity_unit}"


# DrugStockMovement Model
class DrugStockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'IN'),
        ('out', 'OUT'),
    ]

    MOVEMENT_REASON_CHOICES = [
        ('purchase', 'Purchase'),
        ('administration', 'Administration'),
        ('expired', 'Expired'),
        ('damaged', 'Damaged'),
        ('adjustment', 'Adjustment'),
        ('other', 'Other'),
    ]

    REFERENCE_TYPE_CHOICES = [
        ('drug_purchase', 'Drug Purchase'),
        ('water_treatment', 'Water Treatment'),
        ('manual', 'Manual'),
    ]

    drug_stock = models.ForeignKey(
        DrugStock,
        on_delete=models.PROTECT,
        related_name='movements'
    )
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPE_CHOICES)
    movement_reason = models.CharField(max_length=20, choices=MOVEMENT_REASON_CHOICES)
    movement_reason_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe movement reason if you selected Other above"
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Balance immediately after this movement — set automatically"
    )
    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE_CHOICES,
        blank=True
    )
    reference_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the linked Drug Purchase or Water Treatment record"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date of this batch — relevant for IN movements"
    )
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Manufacturer batch code printed on product packaging"
    )
    adjustment_reason = models.TextField(
        blank=True,
        help_text="Required if movement reason is Adjustment"
    )
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='drug_adjustments_authorized',
        null=True,
        blank=True,
        help_text="Required for Adjustment and Expired movements"
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='drug_movements_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.quantity} of {self.drug_stock.drug.name}"


# WaterTreatmentLog Model
class WaterTreatmentLog(models.Model):
    DOSAGE_UNIT_CHOICES = [
        ('ml', 'ml'),
        ('g', 'g'),
        ('sachets', 'Sachets'),
        ('vials', 'Vials'),
        ('other', 'Other'),
    ]

    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='water_treatments'
    )
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='water_treatments'
    )
    treatment_date = models.DateField()
    drug = models.ForeignKey(
        DrugAndSupplement,
        on_delete=models.PROTECT,
        related_name='water_treatments',
        null=True,
        blank=True
    )
    is_plain_water = models.BooleanField(
        default=False,
        help_text="Check this if no drug or supplement was added"
    )
    dosage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    dosage_unit = models.CharField(
        max_length=20,
        choices=DOSAGE_UNIT_CHOICES,
        blank=True
    )
    dosage_unit_other = models.CharField(
    max_length=100,
    blank=True,
    help_text="Specify dosage unit if you selected Other above"
    )
    adjusted_dosage = models.BooleanField(
        default=False,
        help_text="Check if standard dosage was adjusted"
    )
    adjustment_reason = models.TextField(
        blank=True,
        help_text="Required if dosage was adjusted"
    )
    administered_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='water_treatments_administered'
    )
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='water_treatments_authorized',
        null=True,
        blank=True,
        help_text="Farm manager who approved — not required for plain water"
    )
    substitute_authorization = models.BooleanField(
        default=False,
        help_text="Check if a substitute authorized in the manager's absence"
    )
    observed_at = models.TimeField(
        help_text="Time treatment was physically administered"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        if self.is_plain_water:
            return f"Plain water - {self.pen.name} on {self.treatment_date}"
        return f"{self.drug.name} - {self.pen.name} on {self.treatment_date}"


# EggCollection Model
class EggCollection(models.Model):
    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='egg_collections'
    )
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='egg_collections'
    )
    collection_date = models.DateField()
    observed_count = models.PositiveIntegerField(
        help_text="Raw egg count inside the pen at point of collection"
    )
    collected_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='egg_collections'
    )
    observed_at = models.TimeField(
        help_text="Time collection happened inside the pen"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Egg Collection - {self.pen.name} on {self.collection_date}"



# EggGrading Model
class EggGrading(models.Model):
    grading_date = models.DateField(
        help_text="Date grading was done — covers all collections from this date"
    )
    whole_eggs = models.PositiveIntegerField()
    broken_eggs = models.PositiveIntegerField(default=0)
    dirty_eggs = models.PositiveIntegerField(default=0)
    total_graded = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Computed: whole + broken + dirty — set automatically"
    )
    total_collected = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Computed: sum of all pen collections on this date — set automatically"
    )
    grading_discrepancy = models.IntegerField(
        editable=False,
        default=0,
        help_text="Computed: total_graded minus total_collected — set automatically"
    )
    graded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='egg_gradings'
    )
    support_staff = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='egg_grading_support',
        null=True,
        blank=True
    )
    graded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['grading_date']

    def __str__str(self):
        return f"Egg Grading — {self.grading_date}"


# EggStorageConfirmation Model
class EggStorageConfirmation(models.Model):
    grading = models.OneToOneField(
        EggGrading,
        on_delete=models.PROTECT,
        related_name='storage_confirmation'
    )
    whole_eggs_stored = models.PositiveIntegerField()
    broken_eggs_stored = models.PositiveIntegerField(default=0)
    total_stored = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Computed: sum of all stored counts — set automatically"
    )
    storage_discrepancy = models.IntegerField(
        editable=False,
        default=0,
        help_text="Computed: total_graded minus total_stored — set automatically"
    )
    confirmed_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='egg_storage_confirmations'
    )
    confirmed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Storage Confirmation - {self.grading.collection.pen.name}"


# EggTransfer Model
class EggTransfer(models.Model):
    transfer_date = models.DateField()
    whole_eggs = models.PositiveIntegerField()
    broken_eggs = models.PositiveIntegerField(default=0)
    total_eggs = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Computed: sum of all three — set automatically"
    )
    transferred_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='egg_transfers'
    )
    received_by = models.CharField(
        max_length=200,
        help_text="Name of sales branch representative who received"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Egg Transfer - {self.total_eggs} eggs on {self.transfer_date}"



# MortalityRecord Model
class MortalityRecord(models.Model):
    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='mortality_records'
    )
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='mortality_records'
    )
    date_found = models.DateField()
    discovered_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='mortalities_discovered'
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='mortalities_recorded'
    )
    observed_at = models.TimeField(
        help_text="Time worker physically found the dead birds"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    total_count = models.PositiveIntegerField(
        editable=False,
        default=0,
        help_text="Computed: sum of all MortalityRecordItem counts — set automatically"
    )
    is_high_mortality = models.BooleanField(
        default=False,
        editable=False,
        help_text="Set automatically when total_count exceeds threshold"
    )
    alert_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Mortality - {self.pen.name} on {self.date_found} ({self.total_count} birds)"




# MortalityRecordItem Model
class MortalityRecordItem(models.Model):
    CONDITION_CHOICES = [
        ('fresh', 'Fresh'),
        ('decomposed', 'Decomposed'),
        ('injured', 'Injured'),
        ('unknown', 'Unknown'),
    ]

    DISPOSAL_METHOD_CHOICES = [
        ('buried', 'Buried'),
        ('burned', 'Burned'),
        ('pit', 'Pit'),
        ('sold', 'Sold'),
        ('other', 'Other'),
    ]

    SUSPECTED_CAUSE_CHOICES = [
        ('starvation', 'Starvation'),
        ('disease', 'Disease'),
        ('injury', 'Injury'),
        ('unknown', 'Unknown'),
        ('other', 'Other'),
    ]

    mortality_record = models.ForeignKey(
        MortalityRecord,
        on_delete=models.CASCADE,
        related_name='items'
    )
    count = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    disposal_method = models.CharField(max_length=20, choices=DISPOSAL_METHOD_CHOICES)
    sale_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount received if disposal method is Sold"
    )
    buyer_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Who bought the birds if disposal method is Sold"
    )
    suspected_cause = models.CharField(max_length=20, choices=SUSPECTED_CAUSE_CHOICES)
    disposal_method_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe disposal method if you selected Other above"
    )
    suspected_cause_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe suspected cause if you selected Other above"
    )
    def __str__(self):
        return f"{self.count} birds - {self.get_condition_display()} - {self.get_disposal_method_display()}"




# MortalityAlert Model
class MortalityAlert(models.Model):
    RESPONSE_ACTION_CHOICES = [
        ('vet_called', 'Vet Called'),
        ('pen_inspected', 'Pen Inspected'),
        ('feed_checked', 'Feed Checked'),
        ('water_checked', 'Water Checked'),
        ('birds_isolated', 'Birds Isolated'),
        ('other', 'Other'),
    ]

    mortality_record = models.OneToOneField(
        MortalityRecord,
        on_delete=models.PROTECT,
        related_name='alert'
    )
    alert_date = models.DateField(auto_now_add=True)
    threshold_exceeded = models.PositiveIntegerField(
        help_text="The count that triggered this alert"
    )
    notified_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='mortality_alerts_sent'
    )
    notified_persons = models.TextField(
        help_text="List everyone who was informed — manager, owner, vet"
    )
    response_action = models.CharField(
        max_length=20,
        choices=RESPONSE_ACTION_CHOICES
    )
    response_action_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe response action if you selected Other above"
    )
    response_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='mortality_alerts_actioned',
        null=True,
        blank=True
    )
    response_at = models.DateTimeField(
        null=True,
        blank=True
    )
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Alert - {self.mortality_record.pen.name} on {self.alert_date}"


# CleaningLog Model
class CleaningLog(models.Model):
    CLEANING_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('saturday_deep_clean', 'Saturday Deep Clean'),
    ]

    CONFIRMATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]

    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='cleaning_logs'
    )
    cleaning_date = models.DateField()
    cleaning_type = models.CharField(max_length=25, choices=CLEANING_TYPE_CHOICES)
    swept = models.BooleanField(default=False)
    general_tidying_done = models.BooleanField(default=False)
    gutter_cleared = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='cleaning_logs_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    confirmation_status = models.CharField(
        max_length=20,
        choices=CONFIRMATION_STATUS_CHOICES,
        default='pending'
    )
    confirmed_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='cleaning_logs_confirmed',
        null=True,
        blank=True
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmation_notes = models.TextField(
        blank=True,
        help_text="Supervisor remarks — especially important if status is Rejected"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_cleaning_type_display()} - {self.pen.name} on {self.cleaning_date}"



# ManureLog Model
class ManureLog(models.Model):
    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='manure_logs'
    )
    collection_date = models.DateField()
    collected_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='manure_collected'
    )
    drying_done = models.BooleanField(default=False)
    dried_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='manure_dried',
        null=True,
        blank=True
    )
    date_dried = models.DateField(null=True, blank=True)
    bags_filled = models.PositiveIntegerField(null=True, blank=True)
    bags_sold = models.PositiveIntegerField(null=True, blank=True)
    price_per_bag = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Computed: bags_sold x price_per_bag — set automatically"
    )
    buyer_name = models.CharField(max_length=200, blank=True)
    payment_received = models.BooleanField(default=False)
    payment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='manure_logs_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Manure - {self.pen.name} on {self.collection_date}"




# MaintenanceFault Model
class MaintenanceFault(models.Model):
    FAULT_TYPE_CHOICES = [
        ('wire_mesh', 'Wire Mesh'),
        ('nipple_drinker', 'Nipple Drinker'),
        ('trough', 'Trough'),
        ('frame', 'Cage Frame'),
        ('latch', 'Latch or Door'),
        ('other', 'Other'),
    ]

    SEVERITY_CHOICES = [
        ('urgent', 'Urgent'),
        ('minor', 'Minor'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    pen = models.ForeignKey(
        Pen,
        on_delete=models.PROTECT,
        related_name='maintenance_faults'
    )
    fault_type = models.CharField(max_length=20, choices=FAULT_TYPE_CHOICES)
    fault_type_other = models.CharField(
    max_length=200,
    blank=True,
    help_text="Describe fault type if you selected Other above"
    )
    fault_description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    reported_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='faults_reported'
    )
    reported_date = models.DateField()
    observed_at = models.TimeField(
        help_text="Time worker physically noticed the fault"
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='open'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_fault_type_display()} - {self.pen.name} ({self.get_status_display()})"



# MaintenanceRepair Model
class MaintenanceRepair(models.Model):
    fault = models.ForeignKey(
        MaintenanceFault,
        on_delete=models.PROTECT,
        related_name='repairs'
    )
    assigned_to = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='repairs_assigned'
    )
    assigned_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='repairs_assigned_by'
    )
    assigned_date = models.DateField()
    repair_date = models.DateField(null=True, blank=True)
    repair_description = models.TextField(blank=True)
    materials_used = models.TextField(blank=True)
    repair_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='repairs_authorized',
        null=True,
        blank=True
    )
    is_temporary_fix = models.BooleanField(
        default=False,
        help_text="If checked the fault stays open until a permanent repair is recorded"
    )
    repaired_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='repairs_carried_out',
        null=True,
        blank=True
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)


    def __str__(self):
        return f"Repair for {self.fault} - assigned to {self.assigned_to.full_name}"



# MaintenanceConfirmation Model
class MaintenanceConfirmation(models.Model):
    repair = models.OneToOneField(
        MaintenanceRepair,
        on_delete=models.PROTECT,
        related_name='confirmation'
    )
    inspection_date = models.DateField()
    fault_resolved = models.BooleanField(default=False)
    confirmed_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='repairs_confirmed'
    )
    confirmed_at = models.DateTimeField(auto_now_add=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(
        blank=True,
        help_text="Describe what still needs to be done if follow up is required"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Confirmation - {self.repair.fault.pen.name} on {self.inspection_date}"

# ══════════════════════════════════════════════════════════════════
# SALES MODULE
# ══════════════════════════════════════════════════════════════════

class Customer(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('wholesale', 'Wholesale'),
        ('retail', 'Retail'),
        ('both', 'Both'),
    ]

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
        default='wholesale'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()})"


class ShopProduct(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('egg', 'Egg'),
        ('drug', 'Drug / Supplement'),
        ('feed', 'Feed'),
        ('other', 'Other'),
    ]

    EGG_GRADE_CHOICES = [
    ('jumbo', 'Jumbo'),
    ('normal', 'Normal'),
    ('new_drop', 'New Drop'),
    ('cracked', 'Cracked'),
    ('not_applicable', 'Not Applicable'),
    ]

    name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    egg_grade = models.CharField(
    max_length=20,
    choices=EGG_GRADE_CHOICES,
    default='not_applicable'
    )
    unit = models.CharField(
        max_length=50,
        help_text="e.g. crate, bag, bottle, sachet"
    )
    cost_price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0,
    help_text="Cost price per unit for profit calculation"
    )
    wholesale_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    retail_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    wholesale_threshold = models.PositiveIntegerField(
        default=5,
        help_text="Minimum quantity to qualify for wholesale price"
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        if self.product_type == 'egg' and self.egg_grade != 'not_applicable':
            return f"Egg — {self.get_egg_grade_display()}"
        return f"{self.name} ({self.get_product_type_display()})"


class ShopStock(models.Model):
    product = models.OneToOneField(
        ShopProduct,
        on_delete=models.PROTECT,
        related_name='stock'
    )
    current_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False
    )
    reorder_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    last_updated = models.DateTimeField(auto_now=True)
    current_batch_number = models.CharField(max_length=100, blank=True)
    current_expiry_date = models.DateField(null=True, blank=True)

    def recalculate_balance(self):
        from django.db.models import Sum
        total_in = self.movements.filter(movement_type='in').aggregate(
            Sum('quantity'))['quantity__sum'] or 0
        total_out = self.movements.filter(movement_type='out').aggregate(
            Sum('quantity'))['quantity__sum'] or 0
        new_balance = max(total_in - total_out, 0)
        ShopStock.objects.filter(pk=self.pk).update(current_quantity=new_balance)

    def __str__(self):
        return f"{self.product.name} — {self.current_quantity} {self.product.unit}"


class ShopStockMovement(models.Model):
    MOVEMENT_TYPE_CHOICES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    ]

    MOVEMENT_REASON_CHOICES = [
        ('farm_delivery', 'Farm Delivery'),
        ('external_purchase', 'External Purchase'),
        ('sale', 'Sale'),
        ('adjustment', 'Adjustment'),
        ('other', 'Other'),
    ]

    shop_stock = models.ForeignKey(
        ShopStock,
        on_delete=models.PROTECT,
        related_name='movements'
    )
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPE_CHOICES)
    movement_reason = models.CharField(max_length=30, choices=MOVEMENT_REASON_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='shop_stock_movements'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    batch_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Batch number for stock-in movements"
    )
    manufacture_date = models.DateField(
        null=True,
        blank=True,
        help_text="Manufacture date for stock-in movements"
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date for stock-in movements"
    )

    def __str__(self):
        return f"{self.get_movement_type_display()} — {self.shop_stock.product.name} — {self.quantity}"

class ShopSale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('pos', 'POS'),
    ]

    DELIVERY_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('partial', 'Partial'),
    ('complete', 'Complete'),
    ]

    delivery_status = models.CharField(
    max_length=20,
    choices=DELIVERY_STATUS_CHOICES,
    default='pending',
    editable=False,
    help_text="Auto-computed from all item delivery statuses"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='shop_sales',
        null=True,
        blank=True,
        help_text="Leave blank for walk-in customers"
    )
    customer_name_walkin = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name for walk-in customers not in the system"
    )
    sale_date = models.DateField()
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0,
        help_text="Computed from all sale items"
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="Transfer reference or POS receipt number"
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='shop_sales_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        customer = self.customer.name if self.customer else self.customer_name_walkin or "Walk-in"
        return f"{customer} — {self.sale_date}"

class ShopSaleItem(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('complete', 'Complete'),
    ]

    delivery_status = models.CharField(
        max_length=20,
        choices=DELIVERY_STATUS_CHOICES,
        default='pending',
        editable=False,
        help_text="Auto-computed from all item delivery statuses"
    )
    sale = models.ForeignKey(
        ShopSale,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        ShopProduct,
        on_delete=models.PROTECT,
        related_name='sale_items'
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )
    pricing_type = models.CharField(
        max_length=20,
        editable=False,
        default='wholesale'
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0
    )
    quantity_delivered_at_sale = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="How much was taken at point of sale"
    )
    quantity_delivered = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        editable=False
    )

    cost_price_per_unit = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    editable=False,
    default=0
    )
    profit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0
    )

    @property
    def quantity_outstanding(self):
        return self.quantity - self.quantity_delivered

    @property
    def amount_paid(self):
        from django.db.models import Sum
        return self.payments.aggregate(Sum('amount'))['amount__sum'] or 0

    @property
    def amount_outstanding_payment(self):
        return self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.product.name} x {self.quantity} — Sale #{self.sale.pk}"


class ShopDelivery(models.Model):
    sale_item = models.ForeignKey(
        ShopSaleItem,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    delivery_date = models.DateField()
    quantity_delivered = models.DecimalField(max_digits=10, decimal_places=2)
    delivered_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='shop_deliveries'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def str(self):
        return f"Delivery {self.quantity_delivered} for Sale #{self.sale.pk} on {self.delivery_date}"


class ShopSalePayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('pos', 'POS'),
    ]

    sale = models.ForeignKey(
        ShopSale,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="Transfer reference or POS receipt number"
    )

    def __str__(self):
        return f"{self.get_payment_method_display()} — ₦{self.amount}"


class ShopOutflow(models.Model):
    OUTFLOW_TYPE_CHOICES = [
        ('cash_withdrawal', 'Cash Withdrawal'),
        ('salary', 'Salary Payment'),
        ('restock', 'External Restock Payment'),
        ('other', 'Other'),
    ]

    outflow_date = models.DateField()
    outflow_type = models.CharField(max_length=20, choices=OUTFLOW_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_to = models.CharField(max_length=200, blank=True)
    authorized_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='shop_outflows_authorized'
    )
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='shop_outflows_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_outflow_type_display()} — {self.amount} on {self.outflow_date}"


class OldLayerSale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('pos', 'POS'),
    ]

    flock = models.ForeignKey(
        Flock,
        on_delete=models.PROTECT,
        related_name='old_layer_sales'
    )
    sale_date = models.DateField()
    quantity_sold = models.PositiveIntegerField()
    price_per_bird = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False,
        default=0
    )
    buyer_name = models.CharField(max_length=200)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='old_layer_sales_recorded'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Layer Sale — {self.flock} — {self.quantity_sold} birds on {self.sale_date}"


class WorkerSalary(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
    ]

    MONTH_CHOICES = [
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December'),
    ]

    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='salaries'
    )
    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    deductions = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        default=0
    )
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    paid_by = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='salaries_paid'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['worker', 'month', 'year']

    def __str__(self):
        return f"{self.worker.full_name} — {self.get_month_display()} {self.year}"