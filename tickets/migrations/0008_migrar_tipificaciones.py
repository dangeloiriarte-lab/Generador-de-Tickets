from django.db import migrations


TIPOS = [
    {'slug': 'hardware', 'nombre': 'Hardware'},
    {'slug': 'software', 'nombre': 'Software'},
    {'slug': 'red', 'nombre': 'Red'},
    {'slug': 'otro', 'nombre': 'Solicitud de servicio'},
]


def crear_tipificaciones(apps, schema_editor):
    Tipificacion = apps.get_model('tickets', 'Tipificacion')
    for t in TIPOS:
        Tipificacion.objects.get_or_create(slug=t['slug'], defaults={'nombre': t['nombre']})


def migrar_tipo_falla(apps, schema_editor):
    Ticket = apps.get_model('tickets', 'Ticket')
    Tipificacion = apps.get_model('tickets', 'Tipificacion')
    tipo_map = {}
    for t in TIPOS:
        tipo_map[t['slug']] = Tipificacion.objects.get(slug=t['slug'])
    for ticket in Ticket.objects.all():
        if ticket.tipo_falla and ticket.tipo_falla in tipo_map:
            ticket.tipificaciones.add(tipo_map[ticket.tipo_falla])


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0007_tipificacion_ticket_tipificaciones'),
    ]

    operations = [
        migrations.RunPython(crear_tipificaciones, migrations.RunPython.noop),
        migrations.RunPython(migrar_tipo_falla, migrations.RunPython.noop),
    ]
