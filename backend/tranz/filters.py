from django_filters import FilterSet, CharFilter

from .models import Figurant

class FigurantFilter(FilterSet):
    fig_inn = CharFilter(field_name='fig_inn', lookup_expr='icontains')
    fig_name = CharFilter(field_name='fig_name', lookup_expr='icontains')

    class Meta:
        model = Figurant
        fields = ['fig_inn', 'fig_name', 'status']
