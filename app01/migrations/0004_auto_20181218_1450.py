# Generated by Django 2.1.1 on 2018-12-18 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_auto_20181218_1402'),
    ]

    operations = [
        migrations.RenameField(
            model_name='olt',
            old_name='selent_onus',
            new_name='silent_onus',
        ),
        migrations.AlterField(
            model_name='onu',
            name='interface',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
