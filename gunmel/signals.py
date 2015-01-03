from django.dispatch import receiver
from django.db.backends.signals import connection_created
from django.db.models.signals import post_save
from django.utils import timezone

from gunmel.models import Product, PriceHistory


@receiver(connection_created)
def activate_foreign_keys(sender, connection, **kwargs):
    """Enable integrity constraint with sqlite."""
    if connection.vendor == 'sqlite':
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')


@receiver(post_save, sender=Product)
def add_to_history(instance, created, update_fields, **kwargs):
    if (created or
        update_fields is not None and 'price_drop' in update_fields or
        instance.price_drop > 0):
        PriceHistory.objects.create(product=instance, price=instance.price, timestamp=timezone.now())