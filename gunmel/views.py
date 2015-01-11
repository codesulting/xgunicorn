from django.views.generic import View
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
import mmh3

from gunmel.models import Product, PriceHistory


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


class ChartView(View):
	def __init__(self, *arg, **kwargs):
		super(ChartView, self).__init__(*arg, **kwargs)

	def get(self, request, *arg, **kwargs):
		pk = kwargs.get('pk')
		product = get_object_or_404(Product, pk=pk)

		history = PriceHistory.objects.price_history(product)
		dates, prices = zip(* map(lambda entry: (entry.timestamp, float(entry.price)), history))

		response = HttpResponse(content_type='image/png')
		self.populate(product, dates, prices, response)
		return response

	def populate(self, product, dates, prices, response):
		fig = Figure()
		ax = fig.add_subplot(111)
		ax.step(dates, prices)
		ax.xaxis_date()
		ax.xaxis.set_major_formatter(DateFormatter('%b-%d-%Y'))
		fig.autofmt_xdate()
		canvas = FigureCanvasAgg(fig)
		canvas.print_png(response)
		
