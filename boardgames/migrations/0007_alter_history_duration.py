# Generated by Django 5.1.6 on 2025-02-24 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardgames', '0006_alter_history_duration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='duration',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
