from django.shortcuts import redirect
from django.conf import settings
from django.views.generic import View, ListView
from base.models import Item
from collections import OrderedDict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
 
class CartListView(LoginRequiredMixin, ListView):
  model = Item
  template_name = 'pages/cart.html'

  def get_queryset(self):
    cart = self.request.session.get('cart', None)
    if cart is None or len(cart) == 0:
      return redirect('/')
    self.queryset = []
    self.total = 0
    for item_pk, quantity in cart['items'].items():
      obj = Item.objects.get(pk=item_pk)
      obj.quantity = quantity
      obj.subtotal = int(obj.price * quantity)
      self.queryset.append(obj)
      self.total += obj.subtotal
    self.tax_included_total = int(self.total * (settings.TAX_RATE + 1))
    cart['total'] = self.total
    cart['tax_included_total'] = self.tax_included_total
    self.request.session['cart'] = cart
    return super().get_queryset()

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    try:
      context["total"] = self.total
      context["tax_included_total"] = self.tax_included_total
    except Exception:
      pass
    return context

 
class AddCartView(LoginRequiredMixin, View):
 
  # getメソッドでトップへリダイレクトする場合はこのようにかけます。
  # def get(self, request):
  #     return redirect('/')
 
  def post(self, request):
    item_pk = request.POST.get('item_pk')
    quantity = int(request.POST.get('quantity'))
    cart = request.session.get('cart', None)
    if cart is None or len(cart) == 0:
      items = OrderedDict()
      cart = {'items': items}
    if item_pk in cart['items']:
      cart['items'][item_pk] += quantity
      messages.success(self.request, 'カートに追加されました。')
    else:
      cart['items'][item_pk] = quantity
      messages.success(self.request, 'カートに追加されました。')
    request.session['cart'] = cart
    return redirect('/cart/')
  
# カート内のアイテム削除
@login_required
def remove_from_cart(request, pk):
    cart = request.session.get('cart', None)
    if cart is not None:
        del cart['items'][pk]
        request.session['cart'] = cart
    return redirect('/cart/')


# カート内の個数変更
# views.py に以下のクラスを追加

from django.views import View # Viewクラスをインポートしていることを確認

class UpdateCartView(View):
    
    def post(self, request):
        # フォームから送られてきた商品と数量を取得
        item_pk = request.POST.get('item_pk')
        quantity = int(request.POST.get('quantity'))

        # 現在のカート情報をセッションから取得
        cart = request.session.get('cart', None)
        
        # カートが空ではないことを確認
        if cart is not None and item_pk in cart['items']:
            
            # 数量を上書きする
            if quantity > 0:
                # 数量が1以上であれば、新しい数量で上書き
                cart['items'][item_pk] = quantity
            else:
                # 数量が0以下であれば、商品をカートから削除
                # 削除機能も兼ねることで、削除ボタンを置き換えることも可能
                del cart['items'][item_pk] 
                
            # セッション情報を更新
            request.session['cart'] = cart
            
        return redirect('/cart/')