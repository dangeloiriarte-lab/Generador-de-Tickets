from django.contrib import admin
from .models import Ticket, Notificacion, NotificacionUsuario, AuditLog, Tipificacion


@admin.register(Tipificacion)
class TipificacionAdmin(admin.ModelAdmin):
    list_display = ('slug', 'nombre')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'solicitante', 'nombres_tipificacion', 'estado', 'tecnico_asignado', 'fecha_creacion')
    list_filter = ('estado', 'tipificaciones', 'tecnico_asignado', 'direccion_area')
    search_fields = ('solicitante', 'contacto', 'descripcion', 'direccion_area')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_creacion',)


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('mensaje', 'usuario', 'leido', 'creado_en')
    list_filter = ('leido', 'usuario')
    search_fields = ('mensaje',)


@admin.register(NotificacionUsuario)
class NotificacionUsuarioAdmin(admin.ModelAdmin):
    list_display = ('mensaje', 'solicitante', 'direccion_area', 'leido', 'creado_en')
    list_filter = ('leido',)
    search_fields = ('mensaje', 'solicitante', 'direccion_area')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'accion', 'modelo', 'direccion_ip', 'fecha')
    list_filter = ('accion', 'modelo', 'fecha')
    search_fields = ('nombre_completo', 'detalles', 'direccion_ip')
    readonly_fields = ('usuario', 'nombre_completo', 'accion', 'modelo', 'id_objeto', 'detalles', 'direccion_ip', 'fecha')
