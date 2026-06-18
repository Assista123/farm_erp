from django.contrib import admin
from .models import (
    FarmUnit, Pen, Worker, PenWorkerAssignment,
    Flock, Supplier, FlockPlacement,
    FeedType, DrugAndSupplement,
    FeedProcurement, FeedProcurementItem,
    FeedPayment, FeedDelivery, FeedDeliveryItem,
    FeedStock, FeedStockMovement,
    FeedIssuance, FeedIssuanceItem,
    PenFeedingActivity, PenFeedingActivityItem,
    PenFeedingSupervision,
    DrugPurchaseOrder, DrugPurchaseItem,
    DrugStock, DrugStockMovement,
    WaterTreatmentLog,
    EggCollection, EggGrading,
    EggStorageConfirmation, EggTransfer,
    MortalityRecord, MortalityRecordItem, MortalityAlert,
    CleaningLog, ManureLog,
    MaintenanceFault, MaintenanceRepair, MaintenanceConfirmation,
     Customer, ShopProduct, ShopStock, ShopStockMovement,
    ShopSale, ShopDelivery, ShopOutflow, OldLayerSale, WorkerSalary,
    ShopSalePayment, ProductTypeThreshold,
)


@admin.register(FarmUnit)
class FarmUnitAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Pen)
class PenAdmin(admin.ModelAdmin):
    list_display = ['name', 'farm_unit', 'capacity', 'is_active']
    list_filter = ['farm_unit', 'is_active']
    search_fields = ['name']


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['full_name']


@admin.register(PenWorkerAssignment)
class PenWorkerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['worker', 'pen', 'assigned_date', 'is_active']
    list_filter = ['is_active']


@admin.register(Flock)
class FlockAdmin(admin.ModelAdmin):
    list_display = ['pen', 'bird_type', 'initial_count',
                    'current_count', 'date_placed', 'is_active']
    list_filter = ['bird_type', 'is_active']
    readonly_fields = ['current_count']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'supplier_type', 'phone', 'is_active']
    list_filter = ['supplier_type', 'is_active']
    search_fields = ['name']


@admin.register(FlockPlacement)
class FlockPlacementAdmin(admin.ModelAdmin):
    list_display = ['flock', 'supplier', 'quantity_received',
                    'cost_per_bird', 'total_cost', 'placement_date']
    readonly_fields = ['total_cost']


@admin.register(FeedType)
class FeedTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(DrugAndSupplement)
class DrugAndSupplementAdmin(admin.ModelAdmin):
    list_display = ['name', 'treatment_type', 'default_dosage_unit', 'is_active']
    list_filter = ['treatment_type', 'is_active']
    search_fields = ['name']


@admin.register(FeedProcurement)
class FeedProcurementAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'order_date',
                    'expected_delivery_date', 'status', 'ordered_by']
    list_filter = ['status']


@admin.register(FeedProcurementItem)
class FeedProcurementItemAdmin(admin.ModelAdmin):
    list_display = ['procurement', 'feed_type', 'quantity_ordered',
                    'price_per_bag', 'total_cost']
    readonly_fields = ['total_cost']


@admin.register(FeedPayment)
class FeedPaymentAdmin(admin.ModelAdmin):
    list_display = ['procurement', 'payment_date', 'amount_paid', 'payment_method']
    list_filter = ['payment_method']


@admin.register(FeedDelivery)
class FeedDeliveryAdmin(admin.ModelAdmin):
    list_display = ['procurement', 'delivery_date', 'invoice_number',
                    'delivery_confirmed_by']


@admin.register(FeedDeliveryItem)
class FeedDeliveryItemAdmin(admin.ModelAdmin):
    list_display = ['delivery', 'feed_type', 'quantity_received', 'quantity_rejected']


@admin.register(FeedStock)
class FeedStockAdmin(admin.ModelAdmin):
    list_display = ['feed_type', 'current_balance', 'reorder_threshold', 'is_active']
    readonly_fields = ['current_balance']


@admin.register(FeedStockMovement)
class FeedStockMovementAdmin(admin.ModelAdmin):
    list_display = ['feed_stock', 'movement_type', 'movement_reason',
                    'quantity', 'balance_after', 'recorded_at']
    list_filter = ['movement_type', 'movement_reason']
    readonly_fields = ['balance_after']


@admin.register(FeedIssuance)
class FeedIssuanceAdmin(admin.ModelAdmin):
    list_display = ['pen', 'flock', 'issuance_date', 'issued_by', 'received_by']
    list_filter = ['issuance_date']


@admin.register(FeedIssuanceItem)
class FeedIssuanceItemAdmin(admin.ModelAdmin):
    list_display = ['issuance', 'feed_type', 'bags_issued']


@admin.register(PenFeedingActivity)
class PenFeedingActivityAdmin(admin.ModelAdmin):
    list_display = ['flock', 'feeding_date', 'leftover_observed', 'fed_by']
    list_filter = ['feeding_date', 'leftover_observed']


@admin.register(PenFeedingActivityItem)
class PenFeedingActivityItemAdmin(admin.ModelAdmin):
    list_display = ['feeding_activity', 'feed_type', 'bags_used',
                    'empty_bags_returned', 'bags_discrepancy']
    readonly_fields = ['bags_discrepancy']


@admin.register(PenFeedingSupervision)
class PenFeedingSupervisionAdmin(admin.ModelAdmin):
    list_display = ['feeding_activity', 'confirmation_status',
                    'supervised_by', 'supervised_at']
    list_filter = ['confirmation_status']


@admin.register(DrugPurchaseOrder)
class DrugPurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'purchase_date',
                    'purchased_by', 'authorized_by']


@admin.register(DrugPurchaseItem)
class DrugPurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'drug', 'quantity_purchased',
                    'quantity_unit', 'total_cost']
    readonly_fields = ['total_cost']


@admin.register(DrugStock)
class DrugStockAdmin(admin.ModelAdmin):
    list_display = ['drug', 'current_quantity', 'quantity_unit',
                    'reorder_threshold', 'is_active']
    readonly_fields = ['current_quantity']


@admin.register(DrugStockMovement)
class DrugStockMovementAdmin(admin.ModelAdmin):
    list_display = ['drug_stock', 'movement_type', 'movement_reason',
                    'quantity', 'balance_after', 'recorded_at']
    list_filter = ['movement_type', 'movement_reason']
    readonly_fields = ['balance_after']


@admin.register(WaterTreatmentLog)
class WaterTreatmentLogAdmin(admin.ModelAdmin):
    list_display = ['pen', 'treatment_date', 'drug', 'is_plain_water',
                    'administered_by']
    list_filter = ['treatment_date', 'is_plain_water']


@admin.register(EggCollection)
class EggCollectionAdmin(admin.ModelAdmin):
    list_display = ['pen', 'collection_date', 'observed_count', 'collected_by']
    list_filter = ['collection_date']


@admin.register(EggGrading)
class EggGradingAdmin(admin.ModelAdmin):
    list_display = ['grading_date', 'whole_eggs', 'broken_eggs',
                    'dirty_eggs', 'total_graded', 'total_collected',
                    'grading_discrepancy', 'graded_by']
    readonly_fields = ['total_graded', 'total_collected', 'grading_discrepancy']


@admin.register(EggStorageConfirmation)
class EggStorageConfirmationAdmin(admin.ModelAdmin):
    list_display = ['grading', 'total_stored', 'storage_discrepancy', 'confirmed_by']
    readonly_fields = ['total_stored', 'storage_discrepancy']


@admin.register(EggTransfer)
class EggTransferAdmin(admin.ModelAdmin):
    list_display = ['transfer_date', 'total_eggs', 'transferred_by', 'received_by']
    readonly_fields = ['total_eggs']


@admin.register(MortalityRecord)
class MortalityRecordAdmin(admin.ModelAdmin):
    list_display = ['pen', 'date_found', 'total_count',
                    'is_high_mortality', 'discovered_by']
    list_filter = ['date_found', 'is_high_mortality']
    readonly_fields = ['total_count', 'is_high_mortality']


@admin.register(MortalityRecordItem)
class MortalityRecordItemAdmin(admin.ModelAdmin):
    list_display = ['mortality_record', 'count', 'condition',
                    'disposal_method', 'suspected_cause']
    list_filter = ['condition', 'disposal_method']


@admin.register(MortalityAlert)
class MortalityAlertAdmin(admin.ModelAdmin):
    list_display = ['mortality_record', 'alert_date', 'response_action', 'resolved']
    list_filter = ['resolved']


@admin.register(CleaningLog)
class CleaningLogAdmin(admin.ModelAdmin):
    list_display = ['pen', 'cleaning_date', 'cleaning_type',
                    'confirmation_status', 'confirmed_by']
    list_filter = ['cleaning_date', 'confirmation_status']


@admin.register(ManureLog)
class ManureLogAdmin(admin.ModelAdmin):
    list_display = ['pen', 'collection_date', 'drying_done',
                    'bags_filled', 'bags_sold', 'total_revenue']
    readonly_fields = ['total_revenue']


@admin.register(MaintenanceFault)
class MaintenanceFaultAdmin(admin.ModelAdmin):
    list_display = ['pen', 'fault_type', 'severity', 'reported_date', 'status']
    list_filter = ['severity', 'status', 'fault_type']


@admin.register(MaintenanceRepair)
class MaintenanceRepairAdmin(admin.ModelAdmin):
    list_display = ['fault', 'assigned_to', 'assigned_date',
                    'repair_date', 'is_temporary_fix', 'repair_cost']
    list_filter = ['is_temporary_fix']


@admin.register(MaintenanceConfirmation)
class MaintenanceConfirmationAdmin(admin.ModelAdmin):
    list_display = ['repair', 'inspection_date', 'fault_resolved',
                    'follow_up_required', 'confirmed_by']
    list_filter = ['fault_resolved', 'follow_up_required']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'customer_type', 'is_active']
    list_filter = ['customer_type', 'is_active']
    search_fields = ['name', 'phone']


@admin.register(ShopProduct)
class ShopProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'product_type', 'unit', 'wholesale_price',
                    'retail_price', 'wholesale_threshold', 'is_active']
    list_filter = ['product_type', 'is_active']
    search_fields = ['name']


@admin.register(ShopStock)
class ShopStockAdmin(admin.ModelAdmin):
    list_display = ['product', 'current_quantity', 'reorder_threshold']
    readonly_fields = ['current_quantity']


@admin.register(ShopStockMovement)
class ShopStockMovementAdmin(admin.ModelAdmin):
    list_display = ['shop_stock', 'movement_type', 'movement_reason',
                    'quantity', 'balance_after', 'recorded_at']
    list_filter = ['movement_type', 'movement_reason']
    readonly_fields = ['balance_after']


@admin.register(ShopSale)
class ShopSaleAdmin(admin.ModelAdmin):
    list_display = ['sale_date', 'customer', 'total_amount', 'payment_method']
    list_filter = ['sale_date', 'payment_method']
    readonly_fields = ['total_amount']


@admin.register(ShopOutflow)
class ShopOutflowAdmin(admin.ModelAdmin):
    list_display = ['outflow_date', 'outflow_type', 'amount',
                    'paid_to', 'authorized_by']
    list_filter = ['outflow_type', 'outflow_date']


@admin.register(OldLayerSale)
class OldLayerSaleAdmin(admin.ModelAdmin):
    list_display = ['sale_date', 'flock', 'quantity_sold',
                    'price_per_bird', 'total_amount', 'buyer_name']
    readonly_fields = ['total_amount']


@admin.register(WorkerSalary)
class WorkerSalaryAdmin(admin.ModelAdmin):
    list_display = ['worker', 'month', 'year', 'basic_salary',
                    'net_salary', 'payment_date']
    list_filter = ['month', 'year']
    readonly_fields = ['net_salary']


@admin.register(ShopSalePayment)
class ShopSalePaymentAdmin(admin.ModelAdmin):
    list_display = ['sale', 'payment_method', 'amount', 'payment_reference']
    list_filter = ['payment_method']


@admin.register(ShopDelivery)
class ShopDeliveryAdmin(admin.ModelAdmin):
    list_display = ['sale_item', 'delivery_date', 'quantity_delivered', 'delivered_by']

@admin.register(ProductTypeThreshold)
class ProductTypeThresholdAdmin(admin.ModelAdmin):
    list_display = ['product_type', 'reorder_threshold']