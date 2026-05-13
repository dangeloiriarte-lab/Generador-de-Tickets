from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0006_auditlog'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tipificacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'Tipificación',
                'verbose_name_plural': 'Tipificaciones',
                'ordering': ['slug'],
            },
        ),
        migrations.AddField(
            model_name='ticket',
            name='tipificaciones',
            field=models.ManyToManyField(blank=True, to='tickets.tipificacion', verbose_name='Tipificación'),
        ),
    ]
