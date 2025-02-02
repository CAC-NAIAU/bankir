from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, View
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .filters import FigurantFilter
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
from io import BytesIO
from rest_framework import viewsets
from .serializers import FigurantSerializer, TransactionSerializer
import traceback

from .forms import (
                    FigurantForm,
                    TransactionFormSet
                    )

from .models import (
                    Figurant,
                    FigAccount,
                    Transaction,
                    )

class FigurantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Figurant.objects.all()
    serializer_class = FigurantSerializer

class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class FigurantList(ListView):
    model = Figurant
    template_name = "tranz/figurant_list.html"
    context_object_name = "figurants"

    def get_queryset(self):
        queryset = Figurant.objects.all()
        status = self.request.GET.get('status')
        if status:
            if status == 'total':
                queryset = queryset
            elif status == 'in_progress':
                queryset = queryset.filter(status='У роботі')
            elif status == 'done':
                queryset = queryset.filter(status='Відпрацьовано')
            elif status == 'basket':
                queryset = queryset.filter(status='Кошик')
        self.filterset = FigurantFilter(self.request.GET, queryset=queryset)
        filtered_queryset = self.filterset.qs
        return filtered_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Figurant.objects.all()
        
        myFilter = FigurantFilter(self.request.GET, queryset=queryset)
        filtered_queryset = myFilter.qs
        
        context['total_figurants'] = filtered_queryset.count()
        context['progress_figurants'] = filtered_queryset.filter(status='У роботі').count()
        context['done_figurants'] = filtered_queryset.filter(status='Відпрацьовано').count()
        context['basket_figurants'] = filtered_queryset.filter(status='Кошик').count()
        context['myFilter'] = myFilter
        
        return context

class FigurantInline():
    form_class = FigurantForm
    model = Figurant
    template_name = "tranz/figurant_create_or_update.html"

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        named_formsets = self.get_named_formsets()

        self.object = form.save()

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()
        
        formatted_time = datetime.now(timezone(timedelta(hours=3))).strftime('%d.%m.%Y %H:%M:%S')
        messages.success(self.request, f'Дані збережені успішно. Час збереження: {formatted_time}')
        
        return redirect('tranz:update_figurant', pk=form.instance.pk)

    def formset_transactions_valid(self, formset):
        """
        Hook for custom formset saving.. useful if you have multiple formsets
        """
        transactions = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for transaction in transactions:
            transaction.figurant = self.object
            transaction.save()

class FigurantCreate(FigurantInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(FigurantCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'transactions': TransactionFormSet(prefix='transactions'),
            }
        else:
            return {
                'transactions': TransactionFormSet(self.request.POST or None, self.request.FILES or None, prefix='transactions'),
            }

class FigurantUpdate(FigurantInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(FigurantUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        fig_account = FigAccount.objects.filter(figurant=self.object).first() 
        return {
            'transactions': TransactionFormSet(
                self.request.POST or None,
                self.request.FILES or None,
                instance=fig_account,
                prefix='transactions'
            ),
        }

def convertator(request):
    if request.method == 'POST' and request.FILES.getlist('files'):
        file_type = request.POST.get('file_type')
        uploaded_files = request.FILES.getlist('files')
        combined_data = []

        try:
            for uploaded_file in uploaded_files:
                save_path = os.path.join(settings.MEDIA_ROOT, 'sayari', uploaded_file.name)

                if not uploaded_file.name.endswith('.csv'):
                    return render(request, 'products/convertator.html', {
                        'error': f"{uploaded_file.name} не формату CSV з системи Sayari",
                    })
                
                #
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                #
                with open(save_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                try:
                    df = pd.read_csv(save_path, delimiter=',')
                except:
                    df = pd.read_csv(save_path, delimiter=';')

                df['arrival_date'] = df['arrival_date'].str.replace('[', '', regex=False).str.replace(']', '', regex=False).str.replace('"', '', regex=False).str.replace("'", '', regex=False)

                combined_data.append(df)

            combined_df = pd.concat(combined_data, ignore_index=True)

            if file_type == 'Excel':
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    combined_df.to_excel(writer, index=False, sheet_name='Sayari')
                buffer.seek(0)

                response = HttpResponse(
                        buffer,
                        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    )
                current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
                response['Content-Disposition'] = f'attachment; filename="data_sayari_{current_datetime}.xlsx"'
                return response
            
            elif file_type == 'i2':
                return render(request, "tranz/convertator.html", {"error": "Функціонал не працює - у процесі розробки"})

        except Exception as e:
            tb = traceback.format_exc()
            return render(request, 'tranz/convertator.html', {
                'error': f"Помилка {str(uploaded_file)}: {str(tb)}"
            })
    return render(request, 'tranz/convertator.html', {'message': 'Файли успішно опрацьовано'})

def global_search(request):
    return JsonResponse({"message": "У процесі розробки"})

def network_analysis(request):
    return JsonResponse({"message": "У процесі розробки"})

def create_chart(request):
    return JsonResponse({"message": "У процесі розробки"})

def generate_reports(request):
    return JsonResponse({"message": "У процесі розробки"})

def procurement_pivot(request):
    return JsonResponse({"message": "У процесі розробки"})

def procurement_download(request):
    return JsonResponse({"message": "У процесі розробки"})

def procurement_update(request):
    return JsonResponse({"message": "У процесі розробки"})
