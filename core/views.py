import csv

from django.shortcuts import render, get_object_or_404, redirect
from django import forms
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Sum, Count, F
from .permissions import role_required, get_user_context, get_worker_role
from django.utils.decorators import method_decorator
from django.http import JsonResponse, HttpResponse

from .forms import (
    FeedProcurementForm, FeedProcurementItemFormSet,
    FeedDeliveryForm, FeedDeliveryItemFormSet,
    FeedIssuanceForm, FeedIssuanceItemFormSet,
    PenFeedingActivityForm, PenFeedingActivityItemFormSet,
    DrugPurchaseOrderForm, DrugPurchaseItemFormSet,
    MortalityRecordForm, MortalityRecordItemFormSet,
    ShopSaleForm, ShopSaleItemFormSet, ShopSalePaymentFormSet,
    ShopSalePaymentForm,
)

from .models import (
    FarmUnit, Pen, Worker, Flock, Supplier,
    FlockPlacement, FeedType, DrugAndSupplement, FeedProcurement, FeedDelivery, FeedStock,
    FeedIssuance, PenFeedingActivity, PenFeedingSupervision,
    WaterTreatmentLog, MortalityRecord, MortalityAlert, DrugStock,
    DrugPurchaseOrder, EggCollection, EggGrading,
    EggStorageConfirmation, EggTransfer,
    CleaningLog, MaintenanceFault, ManureLog,
    MaintenanceRepair, MaintenanceConfirmation,
    Customer, ShopProduct, ShopStock, ShopStockMovement,
    ShopSale, ShopSaleItem, ShopDelivery, ShopOutflow, OldLayerSale, WorkerSalary,
    ShopSalePayment, CustomerOrder, CustomerDeposit,
    CustomerOrderRelease, CustomerCreditBalance, CustomerCreditTransaction,
)


# ══════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════

@login_required
def dashboard(request):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)
    role = get_worker_role(request.user)
    default_view = 'shop' if role in ['salesperson', 'accountant'] else 'farm'
    view = request.GET.get('view', default_view)

    total_birds = Flock.objects.filter(
        is_active=True).aggregate(
        Sum('current_count'))['current_count__sum'] or 0

    todays_eggs = EggCollection.objects.filter(
        collection_date=today).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0

    weekly_eggs = EggCollection.objects.filter(
        collection_date__gte=week_start).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0

    last_week_start = week_start - timedelta(days=7)
    last_week_eggs = EggCollection.objects.filter(
        collection_date__gte=last_week_start,
        collection_date__lt=week_start).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0

    weekly_lay_pct = round(
        (weekly_eggs / (total_birds * 7)) * 100, 1
    ) if total_birds > 0 else 0
    last_week_lay_pct = round(
        (last_week_eggs / (total_birds * 7)) * 100, 1
    ) if total_birds > 0 else 0
    lay_trend = 'up' if weekly_lay_pct >= last_week_lay_pct else 'down'

    todays_mortality = MortalityRecord.objects.filter(
        date_found=today).aggregate(
        Sum('total_count'))['total_count__sum'] or 0

    todays_sales = ShopSale.objects.filter(sale_date=today)
    todays_total = todays_sales.aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_cash = todays_sales.filter(
        payment_method='cash').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_transfer = todays_sales.filter(
        payment_method='transfer').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_pos = todays_sales.filter(
        payment_method='pos').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0

    todays_outflow = ShopOutflow.objects.filter(
        outflow_date=today).aggregate(
        Sum('amount'))['amount__sum'] or 0

    weekly_sales = ShopSale.objects.filter(
        sale_date__gte=week_start).aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    weekly_outflow = ShopOutflow.objects.filter(
        outflow_date__gte=week_start).aggregate(
        Sum('amount'))['amount__sum'] or 0
    weekly_profit = weekly_sales - weekly_outflow

    monthly_sales = ShopSale.objects.filter(
        sale_date__gte=month_start).aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    monthly_outflow = ShopOutflow.objects.filter(
        outflow_date__gte=month_start).aggregate(
        Sum('amount'))['amount__sum'] or 0
    monthly_profit = monthly_sales - monthly_outflow

    outstanding_deliveries = ShopSaleItem.objects.filter(
        delivery_status__in=['pending', 'partial']).count()
    customers_today = todays_sales.values('customer').distinct().count()
    low_stock = ShopStock.objects.filter(
        current_quantity__lte=F('reorder_threshold')
    ).select_related('product')

    context = {
        'today': today,
        'view': view,
        'total_birds': total_birds,
        'todays_eggs': todays_eggs,
        'weekly_eggs': weekly_eggs,
        'weekly_lay_pct': weekly_lay_pct,
        'last_week_lay_pct': last_week_lay_pct,
        'lay_trend': lay_trend,
        'todays_mortality': todays_mortality,
        'open_faults': MaintenanceFault.objects.filter(status='open').count(),
        'pending_cleaning': CleaningLog.objects.filter(
            confirmation_status='pending').count(),
        'high_mortality_today': MortalityRecord.objects.filter(
            is_high_mortality=True, date_found=today).count(),
        'active_flocks': Flock.objects.filter(is_active=True).count(),
        'todays_total': todays_total,
        'todays_cash': todays_cash,
        'todays_transfer': todays_transfer,
        'todays_pos': todays_pos,
        'todays_outflow': todays_outflow,
        'weekly_profit': weekly_profit,
        'monthly_profit': monthly_profit,
        'outstanding_deliveries': outstanding_deliveries,
        'customers_today': customers_today,
        'low_stock': low_stock,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/dashboard.html', context)


@login_required
def shopstock_movement_create(request):
    from .forms import ShopStockMovementForm
    if request.method == 'POST':
        form = ShopStockMovementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shopstock-list')
        else:
            return render(request, 'core/form.html', {
                'form': form,
                'title': 'Record Stock Movement',
                'cancel_url': reverse_lazy('shopstock-list')
            })
    else:
        form = ShopStockMovementForm()
    return render(request, 'core/form.html', {
        'form': form,
        'title': 'Record Stock Movement',
        'cancel_url': reverse_lazy('shopstock-list')
    })


# ══════════════════════════════════════════════════════════════════
# REPORTS
# ══════════════════════════════════════════════════════════════════

@login_required
def feed_stock_report(request):
    stocks = FeedStock.objects.select_related('feed_type').all()
    low_stocks = stocks.filter(current_balance__lte=F('reorder_threshold'))
    context = {
        'stocks': stocks,
        'low_stocks': low_stocks,
        'low_stock_count': low_stocks.count(),
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/report_feed_stock.html', context)


@login_required
def egg_production_report(request):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)

    weekly_collections = EggCollection.objects.filter(
        collection_date__gte=week_start
    ).values('pen__name').annotate(
        total_observed=Sum('observed_count')
    ).order_by('pen__name')

    monthly_collections = EggCollection.objects.filter(
        collection_date__gte=month_start
    ).values('pen__name').annotate(
        total_observed=Sum('observed_count')
    ).order_by('pen__name')

    weekly_grading = EggGrading.objects.filter(
        grading_date__gte=week_start
    ).aggregate(
        total_whole=Sum('whole_eggs'),
        total_broken=Sum('broken_eggs'),
        total_dirty=Sum('dirty_eggs'),
        total_graded=Sum('total_graded'),
    )

    context = {
        'weekly_collections': weekly_collections,
        'monthly_collections': monthly_collections,
        'weekly_grading': weekly_grading,
        'week_start': week_start,
        'month_start': month_start,
        'today': today,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/report_egg_production.html', context)


@login_required
def mortality_report(request):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)

    weekly_mortality = MortalityRecord.objects.filter(
        date_found__gte=week_start
    ).values('pen__name').annotate(
        total_deaths=Sum('total_count')
    ).order_by('pen__name')

    monthly_mortality = MortalityRecord.objects.filter(
        date_found__gte=month_start
    ).values('pen__name').annotate(
        total_deaths=Sum('total_count')
    ).order_by('pen__name')

    high_mortality_records = MortalityRecord.objects.filter(
        is_high_mortality=True
    ).order_by('-date_found')[:10]

    context = {
        'weekly_mortality': weekly_mortality,
        'monthly_mortality': monthly_mortality,
        'high_mortality_records': high_mortality_records,
        'week_start': week_start,
        'month_start': month_start,
        'today': today,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/report_mortality.html', context)


@login_required
def maintenance_report(request):
    open_faults = MaintenanceFault.objects.filter(
        status='open').order_by('-reported_date')
    in_progress_faults = MaintenanceFault.objects.filter(
        status='in_progress').order_by('-reported_date')
    urgent_faults = MaintenanceFault.objects.filter(
        status__in=['open', 'in_progress'],
        severity='urgent').order_by('-reported_date')

    context = {
        'open_faults': open_faults,
        'in_progress_faults': in_progress_faults,
        'urgent_faults': urgent_faults,
        'open_count': open_faults.count(),
        'urgent_count': urgent_faults.count(),
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/report_maintenance.html', context)


@login_required
def pending_confirmations_report(request):
    pending_cleaning = CleaningLog.objects.filter(
        confirmation_status='pending').order_by('-cleaning_date')
    pending_feeding = PenFeedingActivity.objects.filter(
        supervision__isnull=True).order_by('-feeding_date')
    pending_storage = EggGrading.objects.filter(
        storage_confirmation__isnull=True).order_by('-grading_date')

    context = {
        'pending_cleaning': pending_cleaning,
        'pending_feeding': pending_feeding,
        'pending_storage': pending_storage,
        'pending_cleaning_count': pending_cleaning.count(),
        'pending_feeding_count': pending_feeding.count(),
        'pending_storage_count': pending_storage.count(),
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/report_pending_confirmations.html', context)


# ══════════════════════════════════════════════════════════════════
# FARM SETUP
# ══════════════════════════════════════════════════════════════════

class FarmUnitListView(LoginRequiredMixin, ListView):
    model = FarmUnit
    template_name = 'core/farmunit_list.html'
    context_object_name = 'farm_units'


class FarmUnitDetailView(LoginRequiredMixin, DetailView):
    model = FarmUnit
    template_name = 'core/farmunit_detail.html'
    context_object_name = 'farm_unit'


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class FarmUnitCreateView(LoginRequiredMixin, CreateView):
    model = FarmUnit
    template_name = 'core/form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('farmunit-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Farm Unit'
        context['cancel_url'] = reverse_lazy('farmunit-list')
        return context


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class FarmUnitUpdateView(LoginRequiredMixin, UpdateView):
    model = FarmUnit
    template_name = 'core/form.html'
    fields = ['name', 'description']
    success_url = reverse_lazy('farmunit-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Farm Unit'
        context['cancel_url'] = reverse_lazy('farmunit-list')
        return context


class PenListView(LoginRequiredMixin, ListView):
    model = Pen
    template_name = 'core/pen_list.html'
    context_object_name = 'pens'


class PenDetailView(LoginRequiredMixin, DetailView):
    model = Pen
    template_name = 'core/pen_detail.html'
    context_object_name = 'pen'


class PenCreateView(LoginRequiredMixin, CreateView):
    model = Pen
    template_name = 'core/form.html'
    fields = ['name', 'farm_unit', 'capacity', 'is_active']
    success_url = reverse_lazy('pen-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Pen'
        context['cancel_url'] = reverse_lazy('pen-list')
        return context


class PenUpdateView(LoginRequiredMixin, UpdateView):
    model = Pen
    template_name = 'core/form.html'
    fields = ['name', 'farm_unit', 'capacity', 'is_active']
    success_url = reverse_lazy('pen-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Pen'
        context['cancel_url'] = reverse_lazy('pen-list')
        return context


class WorkerListView(LoginRequiredMixin, ListView):
    model = Worker
    template_name = 'core/worker_list.html'
    context_object_name = 'workers'


class WorkerDetailView(LoginRequiredMixin, DetailView):
    model = Worker
    template_name = 'core/worker_detail.html'
    context_object_name = 'worker'


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class WorkerCreateView(LoginRequiredMixin, CreateView):
    model = Worker
    template_name = 'core/form.html'
    fields = ['full_name', 'role', 'phone', 'date_joined', 'is_active']
    success_url = reverse_lazy('worker-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Worker'
        context['cancel_url'] = reverse_lazy('worker-list')
        return context


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    template_name = 'core/form.html'
    fields = ['full_name', 'role', 'phone', 'date_joined', 'is_active']
    success_url = reverse_lazy('worker-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Worker'
        context['cancel_url'] = reverse_lazy('worker-list')
        return context


class FlockListView(LoginRequiredMixin, ListView):
    model = Flock
    template_name = 'core/flock_list.html'
    context_object_name = 'flocks'
    queryset = Flock.objects.filter(is_active=True)


class FlockDetailView(LoginRequiredMixin, DetailView):
    model = Flock
    template_name = 'core/flock_detail.html'
    context_object_name = 'flock'


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class FlockCreateView(LoginRequiredMixin, CreateView):
    model = Flock
    template_name = 'core/form.html'
    fields = ['pen', 'bird_type', 'initial_count', 'date_placed', 'is_active']
    success_url = reverse_lazy('flock-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Flock'
        context['cancel_url'] = reverse_lazy('flock-list')
        return context


@method_decorator([login_required, role_required('manager', 'director')], name='dispatch')
class FlockUpdateView(LoginRequiredMixin, UpdateView):
    model = Flock
    template_name = 'core/form.html'
    fields = ['pen', 'bird_type', 'initial_count', 'date_placed', 'date_removed', 'is_active']
    success_url = reverse_lazy('flock-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Flock'
        context['cancel_url'] = reverse_lazy('flock-list')
        return context


class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'core/supplier_list.html'
    context_object_name = 'suppliers'


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'core/supplier_detail.html'
    context_object_name = 'supplier'


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'core/form.html'
    fields = ['name', 'supplier_type', 'phone', 'address', 'is_active']
    success_url = reverse_lazy('supplier-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Supplier'
        context['cancel_url'] = reverse_lazy('supplier-list')
        return context


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'core/form.html'
    fields = ['name', 'supplier_type', 'phone', 'address', 'is_active']
    success_url = reverse_lazy('supplier-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Supplier'
        context['cancel_url'] = reverse_lazy('supplier-list')
        return context


class FlockPlacementListView(LoginRequiredMixin, ListView):
    model = FlockPlacement
    template_name = 'core/flockplacement_list.html'
    context_object_name = 'placements'
    ordering = ['-placement_date']


class FlockPlacementDetailView(LoginRequiredMixin, DetailView):
    model = FlockPlacement
    template_name = 'core/flockplacement_detail.html'
    context_object_name = 'placement'


class FlockPlacementCreateView(LoginRequiredMixin, CreateView):
    model = FlockPlacement
    template_name = 'core/form.html'
    fields = ['flock', 'supplier', 'quantity_received', 'cost_per_bird',
              'placement_date', 'recorded_by', 'notes']
    success_url = reverse_lazy('flockplacement-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Flock Placement'
        context['cancel_url'] = reverse_lazy('flockplacement-list')
        return context


class FeedTypeListView(LoginRequiredMixin, ListView):
    model = FeedType
    template_name = 'core/feedtype_list.html'
    context_object_name = 'feed_types'


class FeedTypeCreateView(LoginRequiredMixin, CreateView):
    model = FeedType
    template_name = 'core/form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('feedtype-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Feed Type'
        context['cancel_url'] = reverse_lazy('feedtype-list')
        return context


class FeedTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = FeedType
    template_name = 'core/form.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('feedtype-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Feed Type'
        context['cancel_url'] = reverse_lazy('feedtype-list')
        return context


class DrugAndSupplementListView(LoginRequiredMixin, ListView):
    model = DrugAndSupplement
    template_name = 'core/drugandsupplement_list.html'
    context_object_name = 'drugs'


class DrugAndSupplementCreateView(LoginRequiredMixin, CreateView):
    model = DrugAndSupplement
    template_name = 'core/form.html'
    fields = ['name', 'treatment_type', 'default_dosage_unit', 'manufacturer', 'is_active']
    success_url = reverse_lazy('drugandsupplement-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Drug or Supplement'
        context['cancel_url'] = reverse_lazy('drugandsupplement-list')
        return context


class DrugAndSupplementUpdateView(LoginRequiredMixin, UpdateView):
    model = DrugAndSupplement
    template_name = 'core/form.html'
    fields = ['name', 'treatment_type', 'default_dosage_unit', 'manufacturer', 'is_active']
    success_url = reverse_lazy('drugandsupplement-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Drug or Supplement'
        context['cancel_url'] = reverse_lazy('drugandsupplement-list')
        return context


# ══════════════════════════════════════════════════════════════════
# FEED
# ══════════════════════════════════════════════════════════════════

class FeedProcurementListView(LoginRequiredMixin, ListView):
    model = FeedProcurement
    template_name = 'core/feedprocurement_list.html'
    context_object_name = 'procurements'
    ordering = ['-order_date']


class FeedProcurementDetailView(LoginRequiredMixin, DetailView):
    model = FeedProcurement
    template_name = 'core/feedprocurement_detail.html'
    context_object_name = 'procurement'


@login_required
@role_required('manager', 'director')
def feedprocurement_create(request):
    if request.method == 'POST':
        form = FeedProcurementForm(request.POST)
        formset = FeedProcurementItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            procurement = form.save()
            formset.instance = procurement
            formset.save()
            return redirect('feedprocurement-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'New Feed Order',
                'cancel_url': reverse_lazy('feedprocurement-list')
            })
    else:
        form = FeedProcurementForm()
        formset = FeedProcurementItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'New Feed Order',
        'cancel_url': reverse_lazy('feedprocurement-list')
    })


class FeedProcurementUpdateView(LoginRequiredMixin, UpdateView):
    model = FeedProcurement
    template_name = 'core/form.html'
    fields = ['supplier', 'order_date', 'expected_delivery_date',
              'status', 'ordered_by', 'notes']
    success_url = reverse_lazy('feedprocurement-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Feed Order'
        context['cancel_url'] = reverse_lazy('feedprocurement-list')
        return context


class FeedDeliveryListView(LoginRequiredMixin, ListView):
    model = FeedDelivery
    template_name = 'core/feeddelivery_list.html'
    context_object_name = 'deliveries'
    ordering = ['-delivery_date']


class FeedDeliveryDetailView(LoginRequiredMixin, DetailView):
    model = FeedDelivery
    template_name = 'core/feeddelivery_detail.html'
    context_object_name = 'delivery'


@login_required
def feeddelivery_create(request):
    if request.method == 'POST':
        form = FeedDeliveryForm(request.POST)
        formset = FeedDeliveryItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            delivery = form.save()
            formset.instance = delivery
            formset.save()
            return redirect('feeddelivery-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'Record Feed Delivery',
                'cancel_url': reverse_lazy('feeddelivery-list')
            })
    else:
        form = FeedDeliveryForm()
        formset = FeedDeliveryItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Record Feed Delivery',
        'cancel_url': reverse_lazy('feeddelivery-list')
    })


class FeedDeliveryUpdateView(LoginRequiredMixin, UpdateView):
    model = FeedDelivery
    template_name = 'core/form.html'
    fields = ['procurement', 'delivery_date', 'invoice_number',
              'delivery_confirmed_by', 'received_at', 'notes']
    success_url = reverse_lazy('feeddelivery-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Feed Delivery'
        context['cancel_url'] = reverse_lazy('feeddelivery-list')
        return context


class FeedStockListView(LoginRequiredMixin, ListView):
    model = FeedStock
    template_name = 'core/feedstock_list.html'
    context_object_name = 'stocks'


class FeedStockDetailView(LoginRequiredMixin, DetailView):
    model = FeedStock
    template_name = 'core/feedstock_detail.html'
    context_object_name = 'stock'


class FeedIssuanceListView(LoginRequiredMixin, ListView):
    model = FeedIssuance
    template_name = 'core/feedissuance_list.html'
    context_object_name = 'issuances'
    ordering = ['-issuance_date']


class FeedIssuanceDetailView(LoginRequiredMixin, DetailView):
    model = FeedIssuance
    template_name = 'core/feedissuance_detail.html'
    context_object_name = 'issuance'


@login_required
def feedissuance_create(request):
    if request.method == 'POST':
        form = FeedIssuanceForm(request.POST)
        formset = FeedIssuanceItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            issuance = form.save()
            formset.instance = issuance
            formset.save()
            return redirect('feedissuance-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'Record Feed Issuance',
                'cancel_url': reverse_lazy('feedissuance-list')
            })
    else:
        form = FeedIssuanceForm()
        formset = FeedIssuanceItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Record Feed Issuance',
        'cancel_url': reverse_lazy('feedissuance-list')
    })


class PenFeedingActivityListView(LoginRequiredMixin, ListView):
    model = PenFeedingActivity
    template_name = 'core/penfeedingactivity_list.html'
    context_object_name = 'feeding_activities'
    ordering = ['-feeding_date']


class PenFeedingActivityDetailView(LoginRequiredMixin, DetailView):
    model = PenFeedingActivity
    template_name = 'core/penfeedingactivity_detail.html'
    context_object_name = 'feeding_activity'


@login_required
def penfeedingactivity_create(request):
    if request.method == 'POST':
        form = PenFeedingActivityForm(request.POST)
        formset = PenFeedingActivityItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            activity = form.save()
            formset.instance = activity
            formset.save()
            return redirect('penfeedingactivity-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'Record Feeding Activity',
                'cancel_url': reverse_lazy('penfeedingactivity-list')
            })
    else:
        form = PenFeedingActivityForm()
        formset = PenFeedingActivityItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Record Feeding Activity',
        'cancel_url': reverse_lazy('penfeedingactivity-list')
    })


# ══════════════════════════════════════════════════════════════════
# HEALTH
# ══════════════════════════════════════════════════════════════════

class WaterTreatmentLogListView(LoginRequiredMixin, ListView):
    model = WaterTreatmentLog
    template_name = 'core/watertreatmentlog_list.html'
    context_object_name = 'treatments'
    ordering = ['-treatment_date']


class WaterTreatmentLogDetailView(LoginRequiredMixin, DetailView):
    model = WaterTreatmentLog
    template_name = 'core/watertreatmentlog_detail.html'
    context_object_name = 'treatment'


class WaterTreatmentLogCreateView(LoginRequiredMixin, CreateView):
    model = WaterTreatmentLog
    template_name = 'core/form.html'
    fields = ['flock', 'pen', 'treatment_date', 'drug', 'is_plain_water',
              'dosage', 'dosage_unit', 'adjusted_dosage', 'adjustment_reason',
              'administered_by', 'authorized_by', 'substitute_authorization',
              'observed_at', 'notes']
    success_url = reverse_lazy('watertreatmentlog-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Water Treatment'
        context['cancel_url'] = reverse_lazy('watertreatmentlog-list')
        return context


@login_required
def mortalityrecord_list(request):
    from datetime import timedelta
    today = date.today()
    three_days_ago = today - timedelta(days=3)

    mortality_records = MortalityRecord.objects.all().order_by('-date_found')
    alerts_today = MortalityRecord.objects.filter(
        is_high_mortality=True, date_found=today).count()
    alerts_three_days = MortalityRecord.objects.filter(
        is_high_mortality=True, date_found__gte=three_days_ago).count()

    context = {
        'mortality_records': mortality_records,
        'alerts_today': alerts_today,
        'alerts_three_days': alerts_three_days,
        'today': today,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/mortalityrecord_list.html', context)

@login_required
def mortalityrecord_create(request):
    if request.method == 'POST':
        form = MortalityRecordForm(request.POST)
        formset = MortalityRecordItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            record = form.save()
            formset.instance = record
            formset.save()
            return redirect('mortalityrecord-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'Record Mortality',
                'cancel_url': reverse_lazy('mortalityrecord-list')
            })
    else:
        form = MortalityRecordForm()
        formset = MortalityRecordItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Record Mortality',
        'cancel_url': reverse_lazy('mortalityrecord-list')
    })


class MortalityRecordDetailView(LoginRequiredMixin, DetailView):
    model = MortalityRecord
    template_name = 'core/mortalityrecord_detail.html'
    context_object_name = 'mortality_record'


class MortalityRecordCreateView(LoginRequiredMixin, CreateView):
    model = MortalityRecord
    template_name = 'core/form.html'
    fields = ['flock', 'pen', 'date_found', 'discovered_by',
              'recorded_by', 'observed_at', 'notes']
    success_url = reverse_lazy('mortalityrecord-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Mortality'
        context['cancel_url'] = reverse_lazy('mortalityrecord-list')
        return context


class MortalityRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = MortalityRecord
    template_name = 'core/confirm_delete.html'
    success_url = reverse_lazy('mortalityrecord-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Delete Mortality Record'
        context['message'] = f'Are you sure you want to delete the mortality record for {self.object.pen.name} on {self.object.date_found}?'
        context['cancel_url'] = reverse_lazy('mortalityrecord-list')
        return context


class MortalityRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = MortalityRecord
    template_name = 'core/form.html'
    fields = ['flock', 'pen', 'date_found', 'discovered_by',
              'recorded_by', 'observed_at', 'notes']
    success_url = reverse_lazy('mortalityrecord-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Mortality Record'
        context['cancel_url'] = reverse_lazy('mortalityrecord-list')
        return context


class MortalityAlertListView(LoginRequiredMixin, ListView):
    model = MortalityAlert
    template_name = 'core/mortalityalert_list.html'
    context_object_name = 'alerts'
    ordering = ['-alert_date']


class MortalityAlertDetailView(LoginRequiredMixin, DetailView):
    model = MortalityAlert
    template_name = 'core/mortalityalert_detail.html'
    context_object_name = 'alert'


class MortalityAlertCreateView(LoginRequiredMixin, CreateView):
    model = MortalityAlert
    template_name = 'core/form.html'
    fields = ['mortality_record', 'threshold_exceeded', 'notified_by',
              'notified_persons', 'response_action', 'response_by',
              'response_at', 'resolved', 'resolved_at', 'notes']
    success_url = reverse_lazy('mortalityalert-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Mortality Alert Response'
        context['cancel_url'] = reverse_lazy('mortalityalert-list')
        return context


class DrugStockListView(LoginRequiredMixin, ListView):
    model = DrugStock
    template_name = 'core/drugstock_list.html'
    context_object_name = 'drug_stocks'


class DrugStockDetailView(LoginRequiredMixin, DetailView):
    model = DrugStock
    template_name = 'core/drugstock_detail.html'
    context_object_name = 'drug_stock'


class DrugPurchaseOrderListView(LoginRequiredMixin, ListView):
    model = DrugPurchaseOrder
    template_name = 'core/drugpurchaseorder_list.html'
    context_object_name = 'drug_orders'
    ordering = ['-purchase_date']


class DrugPurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = DrugPurchaseOrder
    template_name = 'core/drugpurchaseorder_detail.html'
    context_object_name = 'drug_order'


@role_required('manager', 'director')
@login_required
def drugpurchaseorder_create(request):
    if request.method == 'POST':
        form = DrugPurchaseOrderForm(request.POST)
        formset = DrugPurchaseItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save()
            formset.instance = order
            formset.save()
            return redirect('drugpurchaseorder-list')
        else:
            return render(request, 'core/formset_form.html', {
                'form': form,
                'formset': formset,
                'title': 'New Drug Purchase Order',
                'cancel_url': reverse_lazy('drugpurchaseorder-list')
            })
    else:
        form = DrugPurchaseOrderForm()
        formset = DrugPurchaseItemFormSet()
    return render(request, 'core/formset_form.html', {
        'form': form,
        'formset': formset,
        'title': 'New Drug Purchase Order',
        'cancel_url': reverse_lazy('drugpurchaseorder-list')
    })


# ══════════════════════════════════════════════════════════════════
# PRODUCTION
# ══════════════════════════════════════════════════════════════════

class EggCollectionListView(LoginRequiredMixin, ListView):
    model = EggCollection
    template_name = 'core/eggcollection_list.html'
    context_object_name = 'collections'
    ordering = ['-collection_date']


class EggCollectionDetailView(LoginRequiredMixin, DetailView):
    model = EggCollection
    template_name = 'core/eggcollection_detail.html'
    context_object_name = 'collection'


class EggCollectionCreateView(LoginRequiredMixin, CreateView):
    model = EggCollection
    template_name = 'core/form.html'
    fields = ['flock', 'pen', 'collection_date', 'observed_count',
              'collected_by', 'observed_at', 'notes']
    success_url = reverse_lazy('eggcollection-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Egg Collection'
        context['cancel_url'] = reverse_lazy('eggcollection-list')
        return context


class EggTransferListView(LoginRequiredMixin, ListView):
    model = EggTransfer
    template_name = 'core/eggtransfer_list.html'
    context_object_name = 'transfers'
    ordering = ['-transfer_date']


class EggTransferDetailView(LoginRequiredMixin, DetailView):
    model = EggTransfer
    template_name = 'core/eggtransfer_detail.html'
    context_object_name = 'transfer'


class EggTransferCreateView(LoginRequiredMixin, CreateView):
    model = EggTransfer
    template_name = 'core/form.html'
    fields = ['transfer_date', 'whole_eggs', 'broken_eggs',
              'transferred_by', 'received_by', 'notes']
    success_url = reverse_lazy('eggtransfer-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Egg Transfer'
        context['cancel_url'] = reverse_lazy('eggtransfer-list')
        return context


class EggGradingListView(LoginRequiredMixin, ListView):
    model = EggGrading
    template_name = 'core/egggrading_list.html'
    context_object_name = 'gradings'
    ordering = ['-grading_date']


class EggGradingDetailView(LoginRequiredMixin, DetailView):
    model = EggGrading
    template_name = 'core/egggrading_detail.html'
    context_object_name = 'grading'


class EggGradingCreateView(LoginRequiredMixin, CreateView):
    model = EggGrading
    template_name = 'core/form.html'
    fields = ['grading_date', 'whole_eggs', 'broken_eggs',
              'graded_by', 'support_staff', 'notes']
    success_url = reverse_lazy('egggrading-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Egg Grading'
        context['cancel_url'] = reverse_lazy('egggrading-list')
        return context


class EggStorageConfirmationListView(LoginRequiredMixin, ListView):
    model = EggStorageConfirmation
    template_name = 'core/eggstorageconfirmation_list.html'
    context_object_name = 'confirmations'
    ordering = ['-confirmed_at']


class EggStorageConfirmationDetailView(LoginRequiredMixin, DetailView):
    model = EggStorageConfirmation
    template_name = 'core/eggstorageconfirmation_detail.html'
    context_object_name = 'confirmation'


class EggStorageConfirmationCreateView(LoginRequiredMixin, CreateView):
    model = EggStorageConfirmation
    template_name = 'core/form.html'
    fields = ['grading', 'whole_eggs_stored', 'broken_eggs_stored',
              'confirmed_by', 'notes']
    success_url = reverse_lazy('eggstorageconfirmation-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Egg Storage Confirmation'
        context['cancel_url'] = reverse_lazy('eggstorageconfirmation-list')
        return context


# ══════════════════════════════════════════════════════════════════
# OPERATIONS
# ══════════════════════════════════════════════════════════════════

class CleaningLogListView(LoginRequiredMixin, ListView):
    model = CleaningLog
    template_name = 'core/cleaninglog_list.html'
    context_object_name = 'cleaning_logs'
    ordering = ['-cleaning_date']


class CleaningLogDetailView(LoginRequiredMixin, DetailView):
    model = CleaningLog
    template_name = 'core/cleaninglog_detail.html'
    context_object_name = 'cleaning_log'


class CleaningLogCreateView(LoginRequiredMixin, CreateView):
    model = CleaningLog
    template_name = 'core/form.html'
    fields = ['pen', 'cleaning_date', 'cleaning_type', 'swept',
              'general_tidying_done', 'gutter_cleared', 'recorded_by', 'notes']
    success_url = reverse_lazy('cleaninglog-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Cleaning'
        context['cancel_url'] = reverse_lazy('cleaninglog-list')
        return context


class MaintenanceRepairListView(LoginRequiredMixin, ListView):
    model = MaintenanceRepair
    template_name = 'core/maintenancerepair_list.html'
    context_object_name = 'repairs'
    ordering = ['-assigned_date']


class MaintenanceRepairDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceRepair
    template_name = 'core/maintenancerepair_detail.html'
    context_object_name = 'repair'


class MaintenanceRepairCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceRepair
    template_name = 'core/form.html'
    fields = ['fault', 'assigned_to', 'assigned_by', 'assigned_date',
              'repair_date', 'repair_description', 'materials_used',
              'repair_cost', 'authorized_by', 'is_temporary_fix',
              'repaired_by', 'notes']
    success_url = reverse_lazy('maintenancerepair-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Repair'
        context['cancel_url'] = reverse_lazy('maintenancerepair-list')
        return context


class MaintenanceConfirmationListView(LoginRequiredMixin, ListView):
    model = MaintenanceConfirmation
    template_name = 'core/maintenanceconfirmation_list.html'
    context_object_name = 'confirmations'
    ordering = ['-confirmed_at']


class MaintenanceConfirmationDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceConfirmation
    template_name = 'core/maintenanceconfirmation_detail.html'
    context_object_name = 'confirmation'


class MaintenanceConfirmationCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceConfirmation
    template_name = 'core/form.html'
    fields = ['repair', 'inspection_date', 'fault_resolved', 'confirmed_by',
              'follow_up_required', 'follow_up_notes', 'notes']
    success_url = reverse_lazy('maintenanceconfirmation-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Repair Confirmation'
        context['cancel_url'] = reverse_lazy('maintenanceconfirmation-list')
        return context


class MaintenanceFaultListView(LoginRequiredMixin, ListView):
    model = MaintenanceFault
    template_name = 'core/maintenancefault_list.html'
    context_object_name = 'faults'
    ordering = ['-reported_date']


class MaintenanceFaultDetailView(LoginRequiredMixin, DetailView):
    model = MaintenanceFault
    template_name = 'core/maintenancefault_detail.html'
    context_object_name = 'fault'


class MaintenanceFaultCreateView(LoginRequiredMixin, CreateView):
    model = MaintenanceFault
    template_name = 'core/form.html'
    fields = ['pen', 'fault_type', 'fault_description', 'severity',
              'reported_by', 'reported_date', 'observed_at', 'notes']
    success_url = reverse_lazy('maintenancefault-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Report Maintenance Fault'
        context['cancel_url'] = reverse_lazy('maintenancefault-list')
        return context


class ManureLogListView(LoginRequiredMixin, ListView):
    model = ManureLog
    template_name = 'core/manurelog_list.html'
    context_object_name = 'manure_logs'
    ordering = ['-collection_date']


class ManureLogDetailView(LoginRequiredMixin, DetailView):
    model = ManureLog
    template_name = 'core/manurelog_detail.html'
    context_object_name = 'manure_log'


class ManureLogCreateView(LoginRequiredMixin, CreateView):
    model = ManureLog
    template_name = 'core/form.html'
    fields = ['pen', 'collection_date', 'collected_by', 'drying_done',
              'dried_by', 'date_dried', 'bags_filled', 'bags_sold',
              'price_per_bag', 'buyer_name', 'payment_received',
              'payment_amount', 'recorded_by', 'notes']
    success_url = reverse_lazy('manurelog-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Manure Log'
        context['cancel_url'] = reverse_lazy('manurelog-list')
        return context


class PenFeedingSupervisionListView(LoginRequiredMixin, ListView):
    model = PenFeedingSupervision
    template_name = 'core/penfeedingsupervision_list.html'
    context_object_name = 'supervisions'
    ordering = ['-supervised_at']


class PenFeedingSupervisionDetailView(LoginRequiredMixin, DetailView):
    model = PenFeedingSupervision
    template_name = 'core/penfeedingsupervision_detail.html'
    context_object_name = 'supervision'


class PenFeedingSupervisionCreateView(LoginRequiredMixin, CreateView):
    model = PenFeedingSupervision
    template_name = 'core/form.html'
    fields = ['feeding_activity', 'distribution_even', 'trough_condition',
              'bird_behavior', 'confirmation_status', 'supervised_by', 'notes']
    success_url = reverse_lazy('penfeedingsupervision-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Feeding Supervision'
        context['cancel_url'] = reverse_lazy('penfeedingsupervision-list')
        return context


class OldLayerSaleListView(LoginRequiredMixin, ListView):
    model = OldLayerSale
    template_name = 'core/oldlayersale_list.html'
    context_object_name = 'sales'
    ordering = ['-sale_date']


class OldLayerSaleCreateView(LoginRequiredMixin, CreateView):
    model = OldLayerSale
    template_name = 'core/form.html'
    fields = ['flock', 'sale_date', 'quantity_sold', 'price_per_bird',
              'buyer_name', 'payment_method', 'payment_reference',
              'recorded_by', 'notes']
    success_url = reverse_lazy('oldlayersale-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Layer Sale'
        context['cancel_url'] = reverse_lazy('oldlayersale-list')
        return context


class WorkerSalaryListView(LoginRequiredMixin, ListView):
    model = WorkerSalary
    template_name = 'core/workersalary_list.html'
    context_object_name = 'salaries'
    ordering = ['-year', '-month']


class WorkerSalaryCreateView(LoginRequiredMixin, CreateView):
    model = WorkerSalary
    template_name = 'core/form.html'
    fields = ['worker', 'month', 'year', 'basic_salary', 'allowances',
              'deductions', 'payment_date', 'payment_method', 'paid_by', 'notes']
    success_url = reverse_lazy('workersalary-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Salary Payment'
        context['cancel_url'] = reverse_lazy('workersalary-list')
        return context


# ══════════════════════════════════════════════════════════════════
# DASHBOARDS
# ══════════════════════════════════════════════════════════════════

@login_required
def farm_dashboard(request):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=7)

    total_birds = Flock.objects.filter(
        is_active=True).aggregate(
        Sum('current_count'))['current_count__sum'] or 0
    todays_eggs = EggCollection.objects.filter(
        collection_date=today).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0
    weekly_eggs = EggCollection.objects.filter(
        collection_date__gte=week_start).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0
    last_week_start = week_start - timedelta(days=7)
    last_week_eggs = EggCollection.objects.filter(
        collection_date__gte=last_week_start,
        collection_date__lt=week_start).aggregate(
        Sum('observed_count'))['observed_count__sum'] or 0
    weekly_lay_pct = round(
        (weekly_eggs / (total_birds * 7)) * 100, 1) if total_birds > 0 else 0
    last_week_lay_pct = round(
        (last_week_eggs / (total_birds * 7)) * 100, 1) if total_birds > 0 else 0
    lay_trend = 'up' if weekly_lay_pct >= last_week_lay_pct else 'down'
    todays_mortality = MortalityRecord.objects.filter(
        date_found=today).aggregate(
        Sum('total_count'))['total_count__sum'] or 0

    context = {
        'today': today,
        'total_birds': total_birds,
        'todays_eggs': todays_eggs,
        'weekly_eggs': weekly_eggs,
        'weekly_lay_pct': weekly_lay_pct,
        'last_week_lay_pct': last_week_lay_pct,
        'lay_trend': lay_trend,
        'todays_mortality': todays_mortality,
        'open_faults': MaintenanceFault.objects.filter(status='open').count(),
        'pending_cleaning': CleaningLog.objects.filter(
            confirmation_status='pending').count(),
        'high_mortality_today': MortalityRecord.objects.filter(
            is_high_mortality=True, date_found=today).count(),
        'active_flocks': Flock.objects.filter(is_active=True).count(),
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/farm_dashboard.html', context)


@login_required
def shop_dashboard(request):
    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today.replace(day=1)

    todays_sales = ShopSale.objects.filter(sale_date=today)
    todays_total = todays_sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    todays_cash = todays_sales.filter(payment_method='cash').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_transfer = todays_sales.filter(payment_method='transfer').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_pos = todays_sales.filter(payment_method='pos').aggregate(
        Sum('total_amount'))['total_amount__sum'] or 0
    todays_outflow = ShopOutflow.objects.filter(
        outflow_date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    weekly_sales = ShopSale.objects.filter(
        sale_date__gte=week_start).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    weekly_outflow = ShopOutflow.objects.filter(
        outflow_date__gte=week_start).aggregate(Sum('amount'))['amount__sum'] or 0
    weekly_profit = weekly_sales - weekly_outflow
    monthly_sales = ShopSale.objects.filter(
        sale_date__gte=month_start).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    monthly_outflow = ShopOutflow.objects.filter(
        outflow_date__gte=month_start).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_profit = monthly_sales - monthly_outflow

    # Fixed — was using delivered=False which doesn't exist
    outstanding_deliveries = ShopSaleItem.objects.filter(
        delivery_status__in=['pending', 'partial']).count()
    customers_today = todays_sales.values('customer').distinct().count()
    low_stock = ShopStock.objects.filter(
        current_quantity__lte=F('reorder_threshold')
    ).select_related('product')

    context = {
        'today': today,
        'todays_total': todays_total,
        'todays_cash': todays_cash,
        'todays_transfer': todays_transfer,
        'todays_pos': todays_pos,
        'todays_outflow': todays_outflow,
        'weekly_profit': weekly_profit,
        'monthly_profit': monthly_profit,
        'outstanding_deliveries': outstanding_deliveries,
        'customers_today': customers_today,
        'low_stock': low_stock,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/shop_dashboard.html', context)


# ══════════════════════════════════════════════════════════════════
# CUSTOMER
# ══════════════════════════════════════════════════════════════════

class CustomerListView(LoginRequiredMixin, ListView):
    model = Customer
    template_name = 'core/customer_list.html'
    context_object_name = 'customers'


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = 'core/customer_detail.html'
    context_object_name = 'customer'


class CustomerCreateView(LoginRequiredMixin, CreateView):
    model = Customer
    template_name = 'core/form.html'
    fields = ['name', 'phone', 'address', 'customer_type', 'notes']
    success_url = reverse_lazy('customer-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Customer'
        context['cancel_url'] = reverse_lazy('customer-list')
        return context


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    template_name = 'core/form.html'
    fields = ['name', 'phone', 'address', 'customer_type', 'is_active', 'notes']
    success_url = reverse_lazy('customer-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Customer'
        context['cancel_url'] = reverse_lazy('customer-list')
        return context


# ══════════════════════════════════════════════════════════════════
# SHOP PRODUCT
# ══════════════════════════════════════════════════════════════════

class ShopProductListView(LoginRequiredMixin, ListView):
    model = ShopProduct
    template_name = 'core/shopproduct_list.html'
    context_object_name = 'products'


class ShopProductCreateView(LoginRequiredMixin, CreateView):
    model = ShopProduct
    template_name = 'core/form.html'
    fields = ['name', 'product_type', 'egg_grade', 'unit', 'wholesale_price',
              'retail_price', 'wholesale_threshold', 'notes']
    success_url = reverse_lazy('shopproduct-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Shop Product'
        context['cancel_url'] = reverse_lazy('shopproduct-list')
        return context


class ShopProductUpdateView(LoginRequiredMixin, UpdateView):
    model = ShopProduct
    template_name = 'core/form.html'
    fields = ['name', 'product_type', 'egg_grade', 'unit', 'wholesale_price',
              'retail_price', 'wholesale_threshold', 'is_active', 'notes']
    success_url = reverse_lazy('shopproduct-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Shop Product'
        context['cancel_url'] = reverse_lazy('shopproduct-list')
        return context


# ══════════════════════════════════════════════════════════════════
# SHOP STOCK
# ══════════════════════════════════════════════════════════════════

class ShopStockListView(LoginRequiredMixin, ListView):
    model = ShopStock
    template_name = 'core/shopstock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        return ShopStock.objects.select_related('product').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        for stock in context['stocks']:
            stock.expiry_alert = None
            if stock.current_expiry_date:
                days_left = (stock.current_expiry_date - today).days
                threshold_days = 150 if stock.product.product_type == 'feed' else 90
                if days_left < 0:
                    stock.expiry_alert = 'expired'
                elif days_left <= threshold_days:
                    stock.expiry_alert = 'warning'
        context['expiry_alert_count'] = sum(
            1 for s in context['stocks'] if s.expiry_alert in ['expired', 'warning']
        )
        return context


@login_required
def shop_stock_expiry_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shop_stock_expiry.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Product', 'Unit', 'Current Stock',
        'Retail Price', 'Wholesale Price',
        'Stock Value (Retail)', 'Batch Number', 'Expiry Date'
    ])
    stocks = ShopStock.objects.select_related('product').order_by('current_expiry_date')
    for stock in stocks:
        retail_value = stock.current_quantity * stock.product.retail_price
        writer.writerow([
            stock.product.name,
            stock.product.unit,
            stock.current_quantity,
            stock.product.retail_price,
            stock.product.wholesale_price,
            retail_value,
            stock.current_batch_number or '—',
            stock.current_expiry_date or '—',
        ])
    return response


class ShopStockDetailView(LoginRequiredMixin, DetailView):
    model = ShopStock
    template_name = 'core/shopstock_detail.html'
    context_object_name = 'stock'


# ══════════════════════════════════════════════════════════════════
# SHOP SALE
# ══════════════════════════════════════════════════════════════════

class ShopSaleListView(LoginRequiredMixin, ListView):
    model = ShopSale
    template_name = 'core/shopsale_list.html'
    context_object_name = 'sales'
    ordering = ['-sale_date']


class ShopSaleDetailView(LoginRequiredMixin, DetailView):
    model = ShopSale
    template_name = 'core/shopsale_detail.html'
    context_object_name = 'sale'


@login_required
def shopsale_create(request):
    if request.method == 'POST':
        form = ShopSaleForm(request.POST)
        formset = ShopSaleItemFormSet(request.POST, prefix='items')
        payment_formset = ShopSalePaymentFormSet(request.POST, prefix='payments')

        if form.is_valid() and formset.is_valid() and payment_formset.is_valid():
            sale = form.save()
            for item_form in formset:
                if not item_form.has_changed():
                    continue
                if item_form.cleaned_data.get('DELETE'):
                    continue
                item = item_form.save(commit=False)
                item.sale = sale
                item.save()
            for payment_form in payment_formset:
                if not payment_form.has_changed():
                    continue
                if payment_form.cleaned_data.get('DELETE'):
                    continue
                payment = payment_form.save(commit=False)
                payment.sale = sale
                payment.save()
            return redirect('shopsale-list')
        else:
            return render(request, 'core/shopsale_form.html', {
                'form': form,
                'formset': formset,
                'payment_formset': payment_formset,
                'title': 'Record Sale',
                'cancel_url': reverse_lazy('shopsale-list'),
            })
    else:
        form = ShopSaleForm()
        formset = ShopSaleItemFormSet(prefix='items')
        payment_formset = ShopSalePaymentFormSet(prefix='payments')

    return render(request, 'core/shopsale_form.html', {
        'form': form,
        'formset': formset,
        'payment_formset': payment_formset,
        'title': 'Record Sale',
        'cancel_url': reverse_lazy('shopsale-list'),
    })


@login_required
def shop_sale_receipt(request, pk):
    sale = get_object_or_404(ShopSale, pk=pk)
    return render(request, 'core/shopsale_receipt.html', {'sale': sale})


class ShopDeliveryCreateView(LoginRequiredMixin, CreateView):
    model = ShopDelivery
    template_name = 'core/form.html'
    fields = ['delivery_date', 'quantity_delivered', 'delivered_by', 'notes']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['delivery_date'].widget = forms.DateInput(attrs={'type': 'date'})
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Delivery'
        context['cancel_url'] = self.get_success_url()
        return context

    def form_valid(self, form):
        sale_item_pk = self.request.GET.get('sale_item')
        form.instance.sale_item = get_object_or_404(ShopSaleItem, pk=sale_item_pk)
        return super().form_valid(form)

    def get_success_url(self):
        sale_item_pk = self.request.GET.get('sale_item')
        if sale_item_pk:
            sale_item = get_object_or_404(ShopSaleItem, pk=sale_item_pk)
            return reverse_lazy('shopsale-detail', kwargs={'pk': sale_item.sale.pk})
        return reverse_lazy('shopsale-list')


# ══════════════════════════════════════════════════════════════════
# SHOP OUTFLOW
# ══════════════════════════════════════════════════════════════════

class ShopOutflowListView(LoginRequiredMixin, ListView):
    model = ShopOutflow
    template_name = 'core/shopoutflow_list.html'
    context_object_name = 'outflows'
    ordering = ['-outflow_date']


class ShopOutflowCreateView(LoginRequiredMixin, CreateView):
    model = ShopOutflow
    template_name = 'core/form.html'
    fields = ['outflow_date', 'outflow_type', 'amount', 'paid_to',
              'authorized_by', 'recorded_by', 'notes']
    success_url = reverse_lazy('shopoutflow-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Outflow'
        context['cancel_url'] = reverse_lazy('shopoutflow-list')
        return context


# ══════════════════════════════════════════════════════════════════
# SHOP PRODUCT PRICES API
# ══════════════════════════════════════════════════════════════════

@login_required
def shop_product_prices(request):
    product_id = request.GET.get('product_id')
    if not product_id:
        return JsonResponse({}, status=400)
    try:
        product = ShopProduct.objects.get(pk=product_id)
        try:
            current_stock = str(product.stock.current_quantity)
        except Exception:
            current_stock = '0'
        return JsonResponse({
            'retail_price': str(product.retail_price),
            'wholesale_price': str(product.wholesale_price),
            'wholesale_threshold': str(product.wholesale_threshold),
            'unit': product.unit,
            'current_stock': current_stock,
        })
    except ShopProduct.DoesNotExist:
        return JsonResponse({}, status=404)


@login_required
def shopsalepayment_create(request, pk):
    sale = get_object_or_404(ShopSale, pk=pk)
    if request.method == 'POST':
        form = ShopSalePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.sale = sale
            payment.save()
            return redirect('shopsale-detail', pk=sale.pk)
    else:
        form = ShopSalePaymentForm()
    return render(request, 'core/form.html', {
        'form': form,
        'title': f'Record Payment — {sale.customer.name if sale.customer else sale.customer_name_walkin or "Walk-in"}',
        'cancel_url': reverse_lazy('shopsale-detail', kwargs={'pk': sale.pk}),
    })


# ══════════════════════════════════════════════════════════════════
# CUSTOMER ORDERS
# ══════════════════════════════════════════════════════════════════

class CustomerOrderListView(LoginRequiredMixin, ListView):
    model = CustomerOrder
    template_name = 'core/customerorder_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return CustomerOrder.objects.select_related(
            'customer', 'product').all().order_by('-created_at')


class CustomerOrderDetailView(LoginRequiredMixin, DetailView):
    model = CustomerOrder
    template_name = 'core/customerorder_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        from django.db.models import Sum
        context = super().get_context_data(**kwargs)
        context['total_deposits_migrated'] = self.object.releases.aggregate(
            Sum('deposits_migrated'))['deposits_migrated__sum'] or 0
        return context

@login_required
def customerorder_create(request):
    from .forms import CustomerOrderForm
    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customerorder-list')
    else:
        form = CustomerOrderForm()
    return render(request, 'core/customerorder_form.html', {
        'form': form,
        'title': 'Record Customer Order',
        'cancel_url': reverse_lazy('customerorder-list'),
    })


@login_required
def customerdeposit_create(request, pk):
    from .forms import CustomerDepositForm
    order = get_object_or_404(CustomerOrder, pk=pk)
    if request.method == 'POST':
        form = CustomerDepositForm(request.POST)
        if form.is_valid():
            deposit = form.save(commit=False)
            deposit.order = order
            deposit.save()
            return redirect('customerorder-detail', pk=order.pk)
    else:
        form = CustomerDepositForm()
    return render(request, 'core/form.html', {
        'form': form,
        'title': f'Record Deposit — {order.customer.name}',
        'cancel_url': reverse_lazy('customerorder-detail', kwargs={'pk': order.pk}),
    })


@login_required
def customerorder_release(request, pk):
    from django.contrib import messages
    from decimal import Decimal

    order = get_object_or_404(CustomerOrder, pk=pk)

    if order.status in ['completed', 'cancelled']:
        messages.error(request, 'Order is already completed or cancelled.')
        return redirect('customerorder-detail', pk=order.pk)

    if order.quantity_outstanding <= 0:
        messages.error(request, 'All quantity has already been released.')
        return redirect('customerorder-detail', pk=order.pk)

    if request.method == 'POST':
        quantity_to_release = Decimal(
            request.POST.get('quantity_to_release', order.quantity_outstanding)
        )
        close_order = request.POST.get('close_order') == 'yes'
        excess_action = request.POST.get('excess_action', 'credit')

        if quantity_to_release > order.quantity_outstanding:
            messages.error(request, 'Cannot release more than outstanding quantity.')
            return redirect('customerorder-release', pk=order.pk)

        # Capture outstanding BEFORE creating release record
        quantity_outstanding_before = order.quantity_outstanding

        # Create the sale
        sale = ShopSale.objects.create(
            customer=order.customer,
            sale_date=date.today(),
            recorded_by=order.recorded_by,
            notes=f'Released from order #{order.pk}',
            payment_method='transfer',
        )

        # Create sale item
        ShopSaleItem.objects.create(
            sale=sale,
            product=order.product,
            quantity=quantity_to_release,
            quantity_delivered_at_sale=0,
        )

        # Calculate deposits to migrate
        release_value = quantity_to_release * order.agreed_price
        total_deposited = order.total_deposited
        amount_to_apply = min(total_deposited, release_value)

        # Migrate deposits as payment on sale
        if amount_to_apply > 0:
            ShopSalePayment.objects.create(
                sale=sale,
                payment_method='transfer',
                amount=amount_to_apply,
                payment_reference=f'Deposits migrated from order #{order.pk}'
            )

        # Create release record — after this, quantity_outstanding changes
        CustomerOrderRelease.objects.create(
            order=order,
            sale=sale,
            quantity=quantity_to_release,
            deposits_migrated=amount_to_apply,
            released_by=order.recorded_by,
        )

        # Handle excess deposit if closing order
        excess = total_deposited - amount_to_apply
        if excess > 0 and close_order:
            if excess_action == 'credit':
                credit, _ = CustomerCreditBalance.objects.get_or_create(
                    customer=order.customer,
                    defaults={'balance': 0}
                )
                CustomerCreditBalance.objects.filter(pk=credit.pk).update(
                    balance=credit.balance + excess
                )
                CustomerCreditTransaction.objects.create(
                    customer=order.customer,
                    transaction_type='credit',
                    amount=excess,
                    order=order,
                    notes=f'Excess deposit from order #{order.pk}',
                    recorded_by=order.recorded_by
                )

        # Use captured value — not recalculated after release record created
        remaining_after_release = quantity_outstanding_before - quantity_to_release

        if close_order or remaining_after_release <= 0:
            new_status = 'completed'
        else:
            new_status = 'partially_released'

        CustomerOrder.objects.filter(pk=order.pk).update(status=new_status)

        messages.success(request, f'Goods released. Sale #{sale.pk} created.')
        return redirect('shopsale-detail', pk=sale.pk)

    return render(request, 'core/customerorder_confirm_release.html', {
        'order': order,
    })


@login_required
def customer_ledger(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    entries = []

    # Deposits
    for order in customer.orders.prefetch_related('deposits').all():
        for d in order.deposits.all():
            entries.append({
                'date': d.payment_date,
                'type': 'Deposit',
                'description': f'Deposit on Order #{order.pk} ({order.product})',
                'debit': 0,
                'credit': d.amount,
            })

    # Releases — goods dispatched create a debit
    for release in CustomerOrderRelease.objects.filter(
        order__customer=customer
    ).select_related('sale', 'order'):
        entries.append({
            'date': release.sale.sale_date,
            'type': 'Release',
            'description': f'Goods Released — Order #{release.order.pk} — Sale #{release.sale.pk} — {release.quantity} {release.order.product.unit}',
            'debit': release.sale.total_amount,
            'credit': 0,
        })

    # Post-release payments — exclude migrated deposits to avoid double counting
    for sale in ShopSale.objects.filter(customer=customer):
        for payment in sale.payments.all():
            if payment.payment_reference.startswith('Deposits migrated'):
                continue
            entries.append({
                'date': sale.sale_date,
                'type': 'Payment',
                'description': f'Payment on Sale #{sale.pk}',
                'debit': 0,
                'credit': payment.amount,
            })


    # Sort by date
    entries.sort(key=lambda x: x['date'])

    # Running balance
    running_balance = 0
    for entry in entries:
        running_balance += entry['debit'] - entry['credit']
        entry['balance'] = running_balance

    context = {
        'customer': customer,
        'entries': entries,
        'total_balance': running_balance,
    }
    context.update(get_user_context(request.user))
    return render(request, 'core/customer_ledger.html', context)