# Generated by Django 5.1.6 on 2025-03-05 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardgames', '0009_alter_result_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='score',
            field=models.PositiveBigIntegerField(),
        ),
    ]
