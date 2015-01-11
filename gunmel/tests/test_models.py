from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from gunmel.models import Product, PriceHistory, ClickLog
from decimal import Decimal


# create products and populate price history (via signal)
def populate_prod_db():
    Product.objects.create(pid=1,url="1",
                               img="1",headline="1",
                               price=5.555,
                               price_drop=3,last_modified=timezone.now())
    Product.objects.create(pid=2,url="2",
                               img="2",headline="2",
                               price=99,
                               price_drop=30,last_modified=timezone.now())
    Product.objects.create(pid=3,url="3",
                               img="3",headline="3",
                               price=6,
                               price_drop=0,last_modified=timezone.now())


class ProductTestCase(TestCase):
    def setUp(self):
        populate_prod_db()

    def test_top_drops(self):
        top_drops = Product.objects.top_drops(2)
        self.assertEquals(len(top_drops), 2)
        p1,p2 = top_drops
        self.assertEquals(p1.pid, 2)
        self.assertEquals(p2.pid, 1)

    def test_save_2_digits(self):
        p1 = Product.objects.get(pid=1)
        self.assertEquals(p1.price, Decimal('5.55'))

    def test_clean(self):
        p4 = Product(pid=4, url='4', img='4',
                    headline='4', price=4,
                    price_drop=101, last_modified=timezone.now())
        try:
            p4.clean()
            self.fail("should have failed due to out of range price drop")
        except ValidationError:
            pass

        p5 = Product(pid=5, url='5', img='5',
                    headline='5', price=-0.5,
                    price_drop=10, last_modified=timezone.now())
        try:
            p5.clean()
            self.fail("should have failed due to negative price")
        except ValidationError:
            pass

        p6 = Product(pid=1, url='6', img='6',
                    headline='6', price=0.5,
                    price_drop=10, last_modified=timezone.now())
        try:
            p6.clean()
            p6.save(force_insert=True)
            self.fail("should have failed due to duplicated pid")
        except IntegrityError:
            pass


class PriceHistoryTestCase(TestCase):
    def setUp(self):
        populate_prod_db()

    def test_price_history(self):
        for product in Product.objects.all():
            self.assertEquals(len(PriceHistory.objects.price_history(product)), 1)

        p1 = Product.objects.get(pid=1)
        p1.price = 50
        p1.last_modified = timezone.now()
        p1.save(update_fields=['price', 'last_modified'])

        p1.url = 'http'
        p1.last_modified = timezone.now()
        p1.save()

        last_modified = p1.last_modified
        p1.price = 100.001
        p1.last_modified = timezone.now()
        p1.save()

        self.assertEquals(len(PriceHistory.objects.price_history(p1)), 4)

        p1.last_modified = timezone.now() + timezone.timedelta(days=1)
        p1.save()
        p1.save()
        self.assertEquals(len(PriceHistory.objects.price_history(p1)), 4)


    def test_foreign_key(self):
        p4 = Product(pid=4, url='4', img='4',
                    headline='4', price=4,
                    price_drop=101, last_modified=timezone.now())

        try:
            PriceHistory.objects.create(product=p4, price=p4.price, timestamp=timezone.now())
            self.fail("should have failed due to foreign key constraints")
        except IntegrityError:
            pass


class ClickLogTestCase(TestCase):
    def setUp(self):
        populate_prod_db()
        p1 = Product.objects.get(pid=1)
        ClickLog.objects.create(product=p1, timestamp=timezone.now() - timezone.timedelta(days=1))
        p2 = Product.objects.get(pid=2)
        ClickLog.objects.create(product=p2, timestamp=timezone.now() - timezone.timedelta(days=1))
        ClickLog.objects.create(product=p2, timestamp=timezone.now() - timezone.timedelta(hours=1))
        p3 = Product.objects.get(pid=3)
        ClickLog.objects.create(product=p3, timestamp=timezone.now() - timezone.timedelta(days=1))
        ClickLog.objects.create(product=p3, timestamp=timezone.now() - timezone.timedelta(hours=1))
        ClickLog.objects.create(product=p3, timestamp=timezone.now() - timezone.timedelta(seconds=1))


    def test_click_log_expired(self):
        self.assertEquals(len(ClickLog.objects.expired(timezone.now() - timezone.timedelta(hours=8))), 3)
        self.assertEquals(len(ClickLog.objects.expired(timezone.now() - timezone.timedelta(minutes=8))), 5)
        self.assertEquals(len(ClickLog.objects.expired(timezone.now())), 6)

    def test_click_log_top(self):
        tops = Product.objects.top_clicks(3)
        self.assertEquals(tops[0].pid, 3)
        self.assertEquals(tops[0].clicks, 3)
        self.assertEquals(tops[1].pid, 2)
        self.assertEquals(tops[2].pid, 1)

        p1 = Product.objects.get(pid=1)
        p1.price = 50
        p1.price = 20
        p1.save()
        ClickLog.objects.create(product=p1, timestamp=timezone.now())
        ClickLog.objects.create(product=p1, timestamp=timezone.now())
        ClickLog.objects.create(product=p1, timestamp=timezone.now())

        tops = Product.objects.top_clicks(1)
        self.assertEquals(len(tops), 1)
        self.assertEquals(tops[0].pid, 1)
        self.assertEquals(tops[0].clicks, 4)

    def test_foreign_key(self):
        p4 = Product(pid=4, url='4', img='4',
                    headline='4', price=4,
                    price_drop=101, last_modified=timezone.now())

        try:
            ClickLog.objects.create(product=p4, timestamp=timezone.now())
            self.fail("should have failed due to foreign key constraints")
        except IntegrityError:
            pass



