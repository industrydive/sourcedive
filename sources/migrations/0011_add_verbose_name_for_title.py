# Generated by Django 2.2.2 on 2019-06-14 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0010_update_verbose_names_on_org_expertise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Job title'),
        ),
    ]
