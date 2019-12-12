# Generated by Django 2.2.3 on 2019-07-25 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0012_add_indstry_model_update_source_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='privacy_level',
            field=models.CharField(choices=[('public', 'Public (whole newsroom)'), ('searchable', 'Semi-private (searchable by newsroom)'), ('private_individual', 'Private (only me)')], default='public', help_text='Who has access to view? Searchable (semi-private) means the general information is available, but not the contact info.', max_length=255),
        ),
    ]