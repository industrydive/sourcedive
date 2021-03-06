# Generated by Django 2.2.1 on 2019-05-29 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0007_add_ordering_for_person_and_interaction_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['-updated'], 'verbose_name': 'Source'},
        ),
        migrations.AlterField(
            model_name='interaction',
            name='interviewee',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interviewee', to='sources.Person', verbose_name='Interviewee'),
        ),
    ]
