from django import forms
from django.forms.models import ModelChoiceField
from django.forms import CheckboxSelectMultiple
from .models import Ticket, Tipificacion
from django.contrib.auth.models import User


class TecnicoChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        nombre = obj.get_full_name().strip()
        return nombre if nombre else obj.username

DIRECCIONES_AREA_CHOICES = [
    ('', 'Seleccione una dirección/departamento'),
    ('Auditoria Interna', 'Auditoria Interna'),
    ('Consultoría Jurídica', 'Consultoría Jurídica'),
    ('Corporación Caracas Productiva', 'Corporación Caracas Productiva'),
    ('Despacho', 'Despacho'),
    ('Estacionamiento', 'Estacionamiento'),
    ('Gestión Administrativa', 'Gestión Administrativa'),
    ('Mercado', 'Mercado'),
    ('Oficina de atención al ciudadano', 'Oficina de atención al ciudadano'),
    ('Planificación y Presupuesto', 'Planificación y Presupuesto'),
    ('Producción y Gestión de Espacios Agricolas', 'Producción y Gestión de Espacios Agricolas'),
    ('Secretaría', 'Secretaría'),
    ('Talento Humano', 'Talento Humano'),
    ('Tecnología', 'Tecnología'),
]


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['solicitante', 'contacto', 'descripcion', 'direccion_area']
        widgets = {
            'solicitante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico o teléfono'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa el problema en detalle'}),
            'direccion_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Área o departamento'}),
        }
        labels = {
            'solicitante': 'Nombre del solicitante',
            'contacto': 'Email/Contacto',
            'descripcion': 'Descripción del problema',
            'direccion_area': 'Dirección/Departamento',
        }


class StaffTicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['solicitante', 'contacto', 'direccion_area', 'tipificaciones', 'descripcion', 'tecnico_asignado']
        widgets = {
            'solicitante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico o teléfono'}),
            'direccion_area': forms.Select(attrs={'class': 'form-select'}),
            'tipificaciones': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describa el problema en detalle'}),
            'tecnico_asignado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'solicitante': 'Nombre del solicitante',
            'contacto': 'Email/Contacto',
            'direccion_area': 'Dirección/Departamento',
            'tipificaciones': 'Tipificación',
            'descripcion': 'Descripción del problema',
            'tecnico_asignado': 'Asignar técnico',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion_area'].widget.choices = DIRECCIONES_AREA_CHOICES
        self.fields['tipificaciones'].queryset = Tipificacion.objects.all()
        qs = User.objects.filter(groups__name='Tecnico')
        if self.instance and self.instance.tecnico_asignado_id:
            qs = qs | User.objects.filter(pk=self.instance.tecnico_asignado_id)
        self.fields['tecnico_asignado'] = TecnicoChoiceField(
            queryset=qs.distinct(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            label='Asignar técnico',
            required=False,
        )


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['estado', 'tipificaciones', 'tecnico_asignado', 'notas']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'tipificaciones': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'tecnico_asignado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Agregue notas de seguimiento...'}),
        }
        labels = {
            'estado': 'Estado del ticket',
            'tipificaciones': 'Tipificación',
            'tecnico_asignado': 'Asignar técnico',
            'notas': 'Notas de seguimiento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipificaciones'].queryset = Tipificacion.objects.all()
        qs = User.objects.filter(groups__name='Tecnico')
        if self.instance and self.instance.tecnico_asignado_id:
            qs = qs | User.objects.filter(pk=self.instance.tecnico_asignado_id)
        self.fields['tecnico_asignado'] = TecnicoChoiceField(
            queryset=qs.distinct(),
            widget=forms.Select(attrs={'class': 'form-select'}),
            label='Asignar técnico',
            required=False,
        )
