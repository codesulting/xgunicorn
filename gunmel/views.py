from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from gunmel.models import Product
import mmh3

class PriceHistoryView(DetailView):
	template_name = 'gunmel/price_history.html'
	model = Product

	def __init__(self, *args, **kwargs):
		self.product_url = None
		super(PriceHistoryView, self).__init__(*args, **kwargs)

	def get(self, request, *args, **kwargs):
		self.product_url = request.GET.get('product-url')
		return super(PriceHistoryView, self).get(request, *args, **kwargs)

	def get_object(self, queryset=None):
		if queryset is None:
			queryset = self.get_queryset()
		
		try:
			pid = mmh3.hash(self.product_url)
			queryset = queryset.filter(pid=pid)
			obj = queryset.get()
		except ObjectDoesNotExist:
			raise Http404(u"Not record found for product URL %s" % self.product_url)

		return obj

	def formatted_object_price(self):
		object = self.get_object()
		return "%0.2f" % object.price
