from django.views.generic import ListView, DetailView
from base.models import Order
import json
from django.contrib.auth.mixins import LoginRequiredMixin
 
 
class OrderIndexView(LoginRequiredMixin, ListView):
  model = Order
  template_name = 'pages/orders.html'
  ordering = '-created_at'  # -:ハイフンありで降順（日付が直近から並ぶ）、ハイフンなしで昇順（日付が古い方から並ぶ）

  def get_queryset(self):
    return Order.objects.filter(user=self.request.user).order_by('-created_at')
 
 
class OrderDetailView(LoginRequiredMixin, DetailView):
  model = Order
  template_name = 'pages/order.html'
  
  # ＊get_querysetメソッドの追記
  def get_queryset(self):
    return Order.objects.filter(user=self.request.user)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    obj = self.get_object()

    if isinstance(obj.items, str):
      context["items"] = json.loads(obj.items)
    else:
      context["items"] = obj.items
          
    # shippingの処理
    if isinstance(obj.shipping, str):
      context["shipping"] = json.loads(obj.shipping)
    else:
      context["shipping"] = obj.shipping

    return context