# Generated by Django 2.1.5 on 2019-01-19 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_auto_20190119_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='pay_status',
            field=models.CharField(choices=[('WAIT_BUYER_PAY', '交易创建'), ('TRADE_CLOSE', '交易关闭'), ('paying', '待支付'), ('TRADE_FINISHED', '交易结束'), ('TRADE_SUCCESS', '成功')], default='paying', max_length=20, verbose_name='交易状态'),
        ),
    ]
