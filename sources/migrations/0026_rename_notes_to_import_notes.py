# Generated by Django 2.2.10 on 2020-02-25 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0025_change_prefix_to_free_text'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='notes',
        ),
        migrations.AddField(
            model_name='person',
            name='import_notes',
            field=models.TextField(blank=True, help_text='Any information deemed relevant to the source at the time of import.', null=True),
        ),
    ]
