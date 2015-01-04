# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClickLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Price Check Log',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PriceHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('price', models.DecimalField(verbose_name=b'Product Price', max_digits=9, decimal_places=2)),
                ('timestamp', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Price History',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('pid', models.IntegerField(serialize=False, verbose_name=b'Product ID', primary_key=True)),
                ('url', models.URLField(max_length=2000, verbose_name=b'Product URL')),
                ('img', models.URLField(max_length=2000, verbose_name=b'Product Image')),
                ('headline', models.CharField(max_length=256)),
                ('desc', models.TextField(max_length=1024, verbose_name=b'Product Description')),
                ('vendor', models.CharField(max_length=128)),
                ('price', models.DecimalField(verbose_name=b'Product Price', max_digits=9, decimal_places=2)),
                ('price_drop', models.IntegerField(default=0, verbose_name=b'Product Price Drop Percentage', db_index=True)),
                ('oos', models.BooleanField(default=False, verbose_name=b'Product Out of Stock')),
                ('last_modified', models.DateTimeField(verbose_name=b'Last modified time')),
            ],
            options={
                'verbose_name': 'Product',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pricehistory',
            name='product',
            field=models.ForeignKey(to='gunmel.Product'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='clicklog',
            name='product',
            field=models.ForeignKey(to='gunmel.Product', db_index=False),
            preserve_default=True,
        ),
    ]
