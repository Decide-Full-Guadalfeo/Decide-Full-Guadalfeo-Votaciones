# Generated by Django 2.0 on 2020-12-18 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0007_auto_20201218_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='question',
            field=models.ManyToManyField(blank=True, related_name='voting', to='voting.Question'),
        ),
    ]