# Generated by Django 5.0.4 on 2024-04-30 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sim', '0003_class_class_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='class_code',
            field=models.IntegerField(unique=True),
        ),
    ]
