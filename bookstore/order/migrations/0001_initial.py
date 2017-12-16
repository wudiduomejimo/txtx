# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInfo',
            fields=[
                ('is_delete', models.BooleanField(default=False, validators='删除标记')),
                ('create_time', models.DateField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateField(verbose_name='更新时间', auto_now=True)),
                ('order_id', models.CharField(max_length=64, verbose_name='订单编号', serialize=False, primary_key=True)),
                ('total_count', models.IntegerField(verbose_name='商品总数', default=1)),
                ('total_price', models.DecimalField(verbose_name='商品总价', max_digits=10, decimal_places=2)),
                ('transit_price', models.DecimalField(verbose_name='订单运费', max_digits=10, decimal_places=2)),
                ('pay_method', models.SmallIntegerField(choices=[(1, '货到付款'), (2, '微信支付'), (3, '支付宝'), (4, '银联支付')], default=1, verbose_name='支付方式')),
                ('status', models.SmallIntegerField(choices=[(1, '待支付'), (2, '待发货'), (3, '待收货'), (4, '待评价'), (5, '已完成')], default=1, verbose_name='订单状态')),
                ('trade_id', models.CharField(max_length=100, null=True, verbose_name='支付编号', unique=True, blank=True)),
                ('addr', models.ForeignKey(verbose_name='收货地址', to='user.Address')),
                ('passport', models.ForeignKey(verbose_name='下单账户', to='user.Passport')),
            ],
            options={
                'db_table': 's_order_info',
            },
        ),
    ]
