from django.urls import path
from . import views

urlpatterns = [

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Farm Setup
    path('farm-units/', views.FarmUnitListView.as_view(), name='farmunit-list'),
    path('farm-units/add/', views.FarmUnitCreateView.as_view(), name='farmunit-create'),
    path('farm-units/<int:pk>/', views.FarmUnitDetailView.as_view(), name='farmunit-detail'),
    path('farm-units/<int:pk>/edit/', views.FarmUnitUpdateView.as_view(), name='farmunit-update'),

    path('pens/', views.PenListView.as_view(), name='pen-list'),
    path('pens/add/', views.PenCreateView.as_view(), name='pen-create'),
    path('pens/<int:pk>/', views.PenDetailView.as_view(), name='pen-detail'),
    path('pens/<int:pk>/edit/', views.PenUpdateView.as_view(), name='pen-update'),

    path('workers/', views.WorkerListView.as_view(), name='worker-list'),
    path('workers/add/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('workers/<int:pk>/', views.WorkerDetailView.as_view(), name='worker-detail'),
    path('workers/<int:pk>/edit/', views.WorkerUpdateView.as_view(), name='worker-update'),

    path('flocks/', views.FlockListView.as_view(), name='flock-list'),
    path('flocks/add/', views.FlockCreateView.as_view(), name='flock-create'),
    path('flocks/<int:pk>/', views.FlockDetailView.as_view(), name='flock-detail'),
    path('flocks/<int:pk>/edit/', views.FlockUpdateView.as_view(), name='flock-update'),

    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/add/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier-detail'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier-update'),

    path('flock-placements/', views.FlockPlacementListView.as_view(), name='flockplacement-list'),
    path('flock-placements/add/', views.FlockPlacementCreateView.as_view(), name='flockplacement-create'),
    path('flock-placements/<int:pk>/', views.FlockPlacementDetailView.as_view(), name='flockplacement-detail'),

    # Feed Types
    path('feed-types/', views.FeedTypeListView.as_view(), name='feedtype-list'),
    path('feed-types/add/', views.FeedTypeCreateView.as_view(), name='feedtype-create'),
    path('feed-types/<int:pk>/edit/', views.FeedTypeUpdateView.as_view(), name='feedtype-update'),

    # Drugs and Supplements
    path('drugs/', views.DrugAndSupplementListView.as_view(), name='drugandsupplement-list'),
    path('drugs/add/', views.DrugAndSupplementCreateView.as_view(), name='drugandsupplement-create'),
    path('drugs/<int:pk>/edit/', views.DrugAndSupplementUpdateView.as_view(), name='drugandsupplement-update'),

    # Feed
    path('feed/procurement/', views.FeedProcurementListView.as_view(), name='feedprocurement-list'),
    path('feed/procurement/add/', views.feedprocurement_create, name='feedprocurement-create'),
    path('feed/procurement/<int:pk>/', views.FeedProcurementDetailView.as_view(), name='feedprocurement-detail'),
    path('feed/procurement/<int:pk>/edit/', views.FeedProcurementUpdateView.as_view(), name='feedprocurement-update'),

    path('feed/deliveries/', views.FeedDeliveryListView.as_view(), name='feeddelivery-list'),
    path('feed/deliveries/add/', views.feeddelivery_create, name='feeddelivery-create'),
    path('feed/deliveries/<int:pk>/', views.FeedDeliveryDetailView.as_view(), name='feeddelivery-detail'),
    path('feed/deliveries/<int:pk>/edit/', views.FeedDeliveryUpdateView.as_view(), name='feeddelivery-update'),

    path('feed/stock/', views.FeedStockListView.as_view(), name='feedstock-list'),
    path('feed/stock/<int:pk>/', views.FeedStockDetailView.as_view(), name='feedstock-detail'),

    path('feed/issuance/', views.FeedIssuanceListView.as_view(), name='feedissuance-list'),
    path('feed/issuance/add/', views.feedissuance_create, name='feedissuance-create'),
    path('feed/issuance/<int:pk>/', views.FeedIssuanceDetailView.as_view(), name='feedissuance-detail'),

    path('feed/feeding/', views.PenFeedingActivityListView.as_view(), name='penfeedingactivity-list'),
    path('feed/feeding/add/', views.penfeedingactivity_create, name='penfeedingactivity-create'),
    path('feed/feeding/<int:pk>/', views.PenFeedingActivityDetailView.as_view(), name='penfeedingactivity-detail'),

    path('feed/supervision/', views.PenFeedingSupervisionListView.as_view(), name='penfeedingsupervision-list'),
    path('feed/supervision/add/', views.PenFeedingSupervisionCreateView.as_view(), name='penfeedingsupervision-create'),
    path('feed/supervision/<int:pk>/', views.PenFeedingSupervisionDetailView.as_view(), name='penfeedingsupervision-detail'),

    # Health
    path('water-treatments/', views.WaterTreatmentLogListView.as_view(), name='watertreatmentlog-list'),
    path('water-treatments/add/', views.WaterTreatmentLogCreateView.as_view(), name='watertreatmentlog-create'),
    path('water-treatments/<int:pk>/', views.WaterTreatmentLogDetailView.as_view(), name='watertreatmentlog-detail'),

    path('mortality/', views.mortalityrecord_list, name='mortalityrecord-list'),
    path('mortality/add/', views.mortalityrecord_create, name='mortalityrecord-create'),
    path('mortality/alerts/', views.MortalityAlertListView.as_view(), name='mortalityalert-list'),
    path('mortality/alerts/add/', views.MortalityAlertCreateView.as_view(), name='mortalityalert-create'),
    path('mortality/alerts/<int:pk>/', views.MortalityAlertDetailView.as_view(), name='mortalityalert-detail'),
    path('mortality/<int:pk>/', views.MortalityRecordDetailView.as_view(), name='mortalityrecord-detail'),
    path('mortality/<int:pk>/edit/', views.MortalityRecordUpdateView.as_view(), name='mortalityrecord-update'),
    path('mortality/<int:pk>/delete/', views.MortalityRecordDeleteView.as_view(), name='mortalityrecord-delete'),

    path('drug-stock/', views.DrugStockListView.as_view(), name='drugstock-list'),
    path('drug-stock/<int:pk>/', views.DrugStockDetailView.as_view(), name='drugstock-detail'),

    path('drug-purchases/', views.DrugPurchaseOrderListView.as_view(), name='drugpurchaseorder-list'),
    path('drug-purchases/add/', views.drugpurchaseorder_create, name='drugpurchaseorder-create'),
    path('drug-purchases/<int:pk>/', views.DrugPurchaseOrderDetailView.as_view(), name='drugpurchaseorder-detail'),

    # Production
    path('eggs/collection/', views.EggCollectionListView.as_view(), name='eggcollection-list'),
    path('eggs/collection/add/', views.EggCollectionCreateView.as_view(), name='eggcollection-create'),
    path('eggs/collection/<int:pk>/', views.EggCollectionDetailView.as_view(), name='eggcollection-detail'),

    path('eggs/grading/', views.EggGradingListView.as_view(), name='egggrading-list'),
    path('eggs/grading/add/', views.EggGradingCreateView.as_view(), name='egggrading-create'),
    path('eggs/grading/<int:pk>/', views.EggGradingDetailView.as_view(), name='egggrading-detail'),

    path('eggs/storage/', views.EggStorageConfirmationListView.as_view(), name='eggstorageconfirmation-list'),
    path('eggs/storage/add/', views.EggStorageConfirmationCreateView.as_view(), name='eggstorageconfirmation-create'),
    path('eggs/storage/<int:pk>/', views.EggStorageConfirmationDetailView.as_view(), name='eggstorageconfirmation-detail'),

    path('eggs/transfer/', views.EggTransferListView.as_view(), name='eggtransfer-list'),
    path('eggs/transfer/add/', views.EggTransferCreateView.as_view(), name='eggtransfer-create'),
    path('eggs/transfer/<int:pk>/', views.EggTransferDetailView.as_view(), name='eggtransfer-detail'),

    # Operations
    path('cleaning/', views.CleaningLogListView.as_view(), name='cleaninglog-list'),
    path('cleaning/add/', views.CleaningLogCreateView.as_view(), name='cleaninglog-create'),
    path('cleaning/<int:pk>/', views.CleaningLogDetailView.as_view(), name='cleaninglog-detail'),

    path('maintenance/', views.MaintenanceFaultListView.as_view(), name='maintenancefault-list'),
    path('maintenance/add/', views.MaintenanceFaultCreateView.as_view(), name='maintenancefault-create'),
    path('maintenance/<int:pk>/', views.MaintenanceFaultDetailView.as_view(), name='maintenancefault-detail'),

    path('maintenance/repairs/', views.MaintenanceRepairListView.as_view(), name='maintenancerepair-list'),
    path('maintenance/repairs/add/', views.MaintenanceRepairCreateView.as_view(), name='maintenancerepair-create'),
    path('maintenance/repairs/<int:pk>/', views.MaintenanceRepairDetailView.as_view(), name='maintenancerepair-detail'),

    path('maintenance/confirmations/', views.MaintenanceConfirmationListView.as_view(), name='maintenanceconfirmation-list'),
    path('maintenance/confirmations/add/', views.MaintenanceConfirmationCreateView.as_view(), name='maintenanceconfirmation-create'),
    path('maintenance/confirmations/<int:pk>/', views.MaintenanceConfirmationDetailView.as_view(), name='maintenanceconfirmation-detail'),

    path('manure/', views.ManureLogListView.as_view(), name='manurelog-list'),
    path('manure/add/', views.ManureLogCreateView.as_view(), name='manurelog-create'),
    path('manure/<int:pk>/', views.ManureLogDetailView.as_view(), name='manurelog-detail'),

    # Reports
    path('reports/feed-stock/', views.feed_stock_report, name='report-feed-stock'),
    path('reports/egg-production/', views.egg_production_report, name='report-egg-production'),
    path('reports/mortality/', views.mortality_report, name='report-mortality'),
    path('reports/maintenance/', views.maintenance_report, name='report-maintenance'),
    path('reports/pending/', views.pending_confirmations_report, name='report-pending'),

    # Customers
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/add/', views.CustomerCreateView.as_view(), name='customer-create'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='customer-update'),

    # Shop Products
    path('shop/stock/movement/add/', views.shopstock_movement_create, name='shopstockmovement-create'),
    path('shop/products/', views.ShopProductListView.as_view(), name='shopproduct-list'),
    path('shop/products/add/', views.ShopProductCreateView.as_view(), name='shopproduct-create'),
    path('shop/products/<int:pk>/edit/', views.ShopProductUpdateView.as_view(), name='shopproduct-update'),

    # Shop Stock
    path('shop/stock/', views.ShopStockListView.as_view(), name='shopstock-list'),
    path('shop/stock/<int:pk>/', views.ShopStockDetailView.as_view(), name='shopstock-detail'),

    # Shop Sales
    path('shop/sales/', views.ShopSaleListView.as_view(), name='shopsale-list'),
    path('shop/sales/add/', views.shopsale_create, name='shopsale-create'),
    path('shop/sales/<int:pk>/', views.ShopSaleDetailView.as_view(), name='shopsale-detail'),
    path('shop/sales/<int:pk>/receipt/', views.shop_sale_receipt, name='shopsale-receipt'),
    path('shop/deliveries/add/', views.ShopDeliveryCreateView.as_view(), name='shopdelivery-create'),

    # Shop Outflow
    path('shop/outflows/', views.ShopOutflowListView.as_view(), name='shopoutflow-list'),
    path('shop/outflows/add/', views.ShopOutflowCreateView.as_view(), name='shopoutflow-create'),
    path('shop/stock/export/expiry/', views.shop_stock_expiry_export, name='shopstock-expiry-export'),
    
    # Old Layer Sales
    path('farm/layer-sales/', views.OldLayerSaleListView.as_view(), name='oldlayersale-list'),
    path('farm/layer-sales/add/', views.OldLayerSaleCreateView.as_view(), name='oldlayersale-create'),

    # Worker Salary
    path('salaries/', views.WorkerSalaryListView.as_view(), name='workersalary-list'),
    path('salaries/add/', views.WorkerSalaryCreateView.as_view(), name='workersalary-create'),

    # Product Prices
    path('shop/product/prices/', views.shop_product_prices, name='shopproduct-prices'),

    path('shop/sales/<int:pk>/pay/', views.shopsalepayment_create, name='shopsalepayment-create'),

    path('shop/orders/', views.CustomerOrderListView.as_view(), name='customerorder-list'),

    path('shop/orders/add/', views.customerorder_create, name='customerorder-create'),
    path('shop/orders/<int:pk>/', views.CustomerOrderDetailView.as_view(), name='customerorder-detail'),
    path('shop/orders/<int:pk>/deposit/', views.customerdeposit_create, name='customerdeposit-create'),
    path('shop/orders/<int:pk>/release/', views.customerorder_release, name='customerorder-release'),

    path('customers/<int:pk>/ledger/', views.customer_ledger, name='customer-ledger'),

    path('shop/reports/director/', views.director_report, name='director-report'),
]