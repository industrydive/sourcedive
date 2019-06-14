# Generated by Django 2.2.2 on 2019-06-14 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0009_add_expertise_and_org_models'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expertise',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Type of expertise'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Organization name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='pronouns',
            field=models.CharField(blank=True, help_text='If provided by source (e.g. she/her, they/their, etc.)', max_length=255, null=True, verbose_name='Pronouns'),
        ),
        migrations.AlterField(
            model_name='person',
            name='type_of_expert',
            field=models.CharField(blank=True, help_text='If applicable (e.g. economist, engineer, researcher, etc.)', max_length=255, null=True, verbose_name='Type of expert'),
        ),
    ]
