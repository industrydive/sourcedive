# Generated by Django 2.2.1 on 2019-05-29 15:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sources', '0008_rename_people_model_to_display_as_source'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expertise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, help_text='This is when the item was updated in the system.', null=True, verbose_name='Updated in system')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': 'Expertise',
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, help_text='This is when the item was updated in the system.', null=True, verbose_name='Updated in system')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='person',
            name='expertise',
        ),
        migrations.AlterField(
            model_name='person',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sources.Organization'),
        ),
        migrations.AddField(
            model_name='person',
            name='expertise',
            field=models.ManyToManyField(blank=True, to='sources.Expertise'),
        ),
    ]
