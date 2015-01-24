from django.views.generic import View
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from matplotlib.ticker import FormatStrFormatter, FixedLocator
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
		return self.format_price(object.price)

	def get_context_data(self, **kwargs):
		context = super(PriceHistoryView, self).get_context_data(**kwargs)
		obj = self.get_object()
		history = PriceHistory.objects.price_history(obj)
		date_price_list = map(lambda entry: (entry.timestamp, float(entry.price)), history)
		date_price_list.reverse()
		min_price_date, min_price = date_price_list[0]
		for (timestamp, price) in date_price_list[1:]:
			if price <= min_price:
				min_price = price
				min_price_date = timestamp

		max_price_date, max_price = max(date_price_list, key=lambda (timestamp, price): price)

		date_price_list = map(lambda (d, p): (self.format_date(d), self.format_price(p)), date_price_list)
		if len(date_price_list) < 5:
			last_five = date_price_list + [('N/A', 'N/A')] * (5 - len(date_price_list))
		else:
			last_five = date_price_list[:5]

		context['max_price'] = self.format_price(max_price)
		context['max_price_date'] = self.format_date(max_price_date)
		context['min_price'] = self.format_price(min_price)
		context['min_price_date'] = self.format_date(min_price_date)

		context['last_five'] = last_five

		return context

	def format_price(self, price):
		return "%0.2f" % price

	def format_date(self, date):
		return date.strftime('%m/%d/%Y')


class ChartView(View):
	_last_n = 5

	def __init__(self, *arg, **kwargs):
		super(ChartView, self).__init__(*arg, **kwargs)

	def get(self, request, *arg, **kwargs):
		pk = kwargs.get('pk')
		product = get_object_or_404(Product, pk=pk)

		history = PriceHistory.objects.price_history(product)

		response = HttpResponse(content_type='image/png')
		self.populate(product, history, response)
		return response

	def populate(self, product, history, response):

		date_price_list = map(lambda entry: (entry.timestamp, float(entry.price)), history)

		min_price_date, min_price = date_price_list[0]
		for (timestamp, price) in date_price_list[1:]:
			if price <= min_price:
				min_price = price
				min_price_date = timestamp

		max_price_date, max_price = max(date_price_list, key=lambda (timestamp, price): price)

		# append today's date and price for plotting
		date_price_list.append((timezone.now(), date_price_list[-1][1]))
		dates, prices = zip(* date_price_list)


		fig = Figure(frameon=False)

		# price history step plot
		ax = fig.add_subplot(111)
		ax.step(dates, prices, where='post')		
		ax.xaxis_date()
		ax.xaxis.set_major_formatter(DateFormatter('%x'))
		ax.yaxis.set_major_formatter(FormatStrFormatter('$%d'))
		ax.grid()
		ax.set_title(product.headline)
		fig.autofmt_xdate()

		# min, max lines
		ax2 = ax.twinx()
		ax2.axhline(y=min_price, color='g', linestyle='--')
		ax2.axhline(y=max_price, color='r', linestyle='--')
		#ax2.yaxis.set_major_formatter(FormatStrFormatter('$%0.2f'))
		ax2.yaxis.set_major_locator(FixedLocator([min_price, max_price]))
		min_price_tick_label_text = '$%0.2f\n%s' % (min_price, min_price_date.strftime('%x'))
		max_price_tick_label_text = '$%0.2f\n%s' % (max_price, max_price_date.strftime('%x'))
		ax2.set_yticklabels([min_price_tick_label_text, max_price_tick_label_text])
		min_price_tick_label, max_price_tick_label = ax2.get_yticklabels()
		min_price_tick_label.set_color('green')
		max_price_tick_label.set_color('red')
		# ax2.annotate('arc', xy=(dates[5], max_price), xycoords='data', xytext=(-30, -30), textcoords='offset points', arrowprops=dict(arrowstyle='->',
		# 	connectionstyle='arc,angleA=0,armA=30,rad=10'))

		fig.tight_layout()
		canvas = FigureCanvasAgg(fig)
		canvas.print_png(response)
		
