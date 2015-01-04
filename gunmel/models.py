from django.core.exceptions import ValidationError
from django.db import models


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
    desc = models.TextField(max_length=1024, verbose_name="Product Description")
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
            if current.price != self.price:
                if current.price > self.price:
                    self.price_drop = int((float(current.price) - float(self.price)) / float(current.price) * 100)
                self.clean()
                super(Product, self).save(**kwargs)
        else:
            self.clean()
            super(Product, self).save(**kwargs)

    class Meta:
        verbose_name = "Product"

class PriceHistoryManager(models.Manager):
    def price_history(self, product):
        return self.get_queryset().filter(product__pid=product.pid)


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


