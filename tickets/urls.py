from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('usuario/', views.panel_usuario_login, name='panel_usuario_login'),
    path('mi-panel/', views.panel_usuario, name='panel_usuario'),
    path('mi-panel/nuevo-ticket/', views.crear_ticket, name='crear_ticket'),
    path('mi-panel/salir/', views.cerrar_sesion_usuario, name='cerrar_sesion_usuario'),
    path('mi-panel/ticket/<int:ticket_id>/', views.ver_ticket_usuario, name='ver_ticket_usuario'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/nuevo-ticket/', views.crear_ticket_staff, name='crear_ticket_staff'),
    path('tickets/<int:ticket_id>/', views.detalle_ticket, name='detalle_ticket'),
    path('tickets/<int:ticket_id>/pdf/', views.ticket_pdf, name='ticket_pdf'),
    path('tickets/pdf/', views.tickets_pdf, name='tickets_pdf'),
    path('tickets/excel/', views.tickets_excel, name='tickets_excel'),
    path('reportes/', views.reportes, name='reportes'),
    path('ayuda/manual/', views.ayuda_manual, name='ayuda_manual'),
    path('ayuda/manual/pdf/', views.manual_pdf, name='manual_pdf'),
    path('ayuda/guia-rapida/', views.ayuda_guia_rapida, name='ayuda_guia_rapida'),
    path('ayuda/acerca-de/', views.ayuda_acerca_de, name='ayuda_acerca_de'),
    path('notificaciones/', views.notificaciones_json, name='notificaciones_json'),
    path('notificaciones/<int:notif_id>/leer/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),
    path('notificaciones-usuario/', views.notificaciones_usuario_json, name='notificaciones_usuario_json'),
    path('notificaciones-usuario/<int:notif_id>/leer/', views.marcar_notificacion_usuario_leida, name='marcar_notificacion_usuario_leida'),
    path('auditoria/', views.auditoria_list, name='auditoria_list'),
    path('auditoria/<int:pk>/', views.auditoria_detalle, name='auditoria_detalle'),
]
