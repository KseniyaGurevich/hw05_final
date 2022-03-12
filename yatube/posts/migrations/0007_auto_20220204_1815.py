# Generated by Django 2.2.9 on 2022-02-04 15:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0006_auto_20220204_1740'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='group',
                                    to=settings.AUTH_USER_MODEL),
        ),
    ]
