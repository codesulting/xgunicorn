from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import model_to_dict
from decimal import Decimal


# Create your models here.
class ProductManager(models.Manager):
    def top_drops(self, n):
        return self.get_queryset().order_by('-price_drop')[:n]

    def top_clicks(self, n):
        return self.get_queryset().annotate(clicks=models.Count('clicklog')).order_by('-clicks')[:n]


class Product(models.Model):
    pid = models.IntegerField(primary_key=True, verbose_name="Product ID")  # generated using murmur3 on url
    url = models.URLField(max_length=2000, verbose_name="Product URL")
    img = models.URLField(max_length=2000, verbose_name="Product Image")
    headline = models.CharField(max_length=256)
    vendor = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Product Price")
    price_drop = models.IntegerField(verbose_name="Product Price Drop Percentage",
                                     db_index=True, default=0)
    oos = models.BooleanField(default=False, verbose_name="Product Out of Stock")
    last_modified = models.DateTimeField(verbose_name="Last modified time")

    objects = ProductManager()

    def clean(self):
        if self.price < 0.0:
            raise ValidationError('Price cannot be negative')
        if self.price_drop < 0 or self.price_drop > 100:
            raise ValidationError('Price drop out of range of 0-100%')

    def __str__(self):
        return self.headline

    # only save if price changes
    def save(self, **kwargs):
        if Product.objects.filter(pid=self.pid).exists():
            current = Product.objects.get(pid=self.pid)
            dict_new = model_to_dict(self)
            dict_current = model_to_dict(current)
            diff = filter(lambda (k, v): v != dict_new[k] and k != 'last_modified' and k != 'price', dict_current.items())


            new_price = Decimal("%.2f" % self.price)
            if current.price != new_price:
                if current.price > new_price:
                    self.price_drop = int((current.price - new_price) / current.price * 100)
                else:
                    self.price_drop = 0
                diff.append('price')

            if len(diff) > 0:
                self.clean()
                super(Product, self).save(**kwargs)

        else:
            self.price = Decimal("%.2f" % self.price)
            self.clean()
            super(Product, self).save(**kwargs)


    class Meta:
        verbose_name = "Product"

class PriceHistoryManager(models.Manager):
    def price_history(self, product):
        return self.get_queryset().filter(product__pid=product.pid).order_by('timestamp')

    def min(self, product):
        min_price = self.get_queryset().filter(product__pid=product.pid).aggregate(min_price=models.Min('price'))['min_price']
        return self.get_queryset().filter(product__pid=product.pid).filter(price=min_price).order_by('-timestamp')[0]

    def max(self, product):
        max_price = self.get_queryset().filter(product__pid=product.pid).aggregate(max_price=models.Max('price'))['max_price']
        return self.get_queryset().filter(product__pid=product.pid).filter(price=max_price).order_by('-timestamp')[0]

    def last_n(self, product, n):
        return self.get_queryset().filter(product__pid=product.pid).order_by('-timestamp')[:n]

class PriceHistory(models.Model):
    product = models.ForeignKey(Product)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name="Product Price")
    timestamp = models.DateTimeField()

    objects = PriceHistoryManager()

    class Meta:
        verbose_name = "Price History"


class ClickLogManager(models.Manager):
    def expired(self, cutoff_time):
        return self.get_queryset().filter(timestamp__lt = cutoff_time)


class ClickLog(models.Model):
    product = models.ForeignKey(Product, db_index=False)
    timestamp = models.DateTimeField()

    objects = ClickLogManager()

    class Meta:
        verbose_name = "Price Check Log"


