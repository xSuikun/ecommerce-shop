# Generated by Django 3.2.8 on 2022-01-18 04:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_rename_viewer_product_viewers'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=None, max_digits=2, null=True),
        ),
    ]
