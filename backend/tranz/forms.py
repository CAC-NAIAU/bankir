from typing import Any, Mapping
from django import forms
from django.forms import inlineformset_factory, modelformset_factory

from .models import (
    Figurant,
    FigAccount,
    Transaction
)

from django.utils.translation import gettext_lazy as _

class FigurantForm(forms.ModelForm):

    class Meta:
        model = Figurant
        fields = '__all__'
        labels = {
            "fig_inn": "Код фігуранта",
            "fig_name": "Назва фігуранта",
            "activity_info": "Діяльність",
            "add_info": "Додаткова інформація",
            "fig_logo": "Фото/лого фігуранта",
            "status": "Статус",
        }
       
        widgets = {
            'fig_inn': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
            'fig_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
        }

class FigAccForm(forms.ModelForm):

    class Meta:
        model = FigAccount
        fields = '__all__'
        labels = {
            "account": "Рахунок",
            "currency": "Валюта",
            "bank_code": "Код банку",
            "bank_name": "Назва банку",
        }
       
        widgets = {
            'account': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
            'currency': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
            'bank_code': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
            'bank_name': forms.TextInput(
                attrs={
                    'class': 'form-control'
                    }
                ),
        }

class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = '__all__'
        labels = {
            "contr_acc": "07. Контрагент_Рахунок",
            "contr_name": "08. Контрагент_ПІБ",
            "contr_ipn": "09. Контрагент_ІПН",
            "contr_bank_code": "10. Контрагент_Код банку",
            "contr_bank_name": "11. Контрагент_Найменування банку",
            "pay_purp": "12. Призначення платежу",
            "doc_num": "13. Номер документа",
            "doc_date": "14. Дата документа",
            "direction": "15. Напрямок",
            "sum_ct": "16. Сумма операції Кт",
            "sum_dt": "17. Сумма операції Дт",
        }

FigurantFormSet = modelformset_factory(
    Figurant, fields=('fig_inn', 'fig_name'),
    extra=1, can_delete=True)

FigAccFormSet = inlineformset_factory(
    Figurant, FigAccount, form=TransactionForm,
    extra=1, can_delete=True,
    can_delete_extra=True
)

TransactionFormSet = inlineformset_factory(
    FigAccount, Transaction, form=FigAccForm,
    extra=1, can_delete=True,
    can_delete_extra=True
)
