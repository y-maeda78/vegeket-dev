from django.shortcuts import redirect
from django.views.generic import View, TemplateView
from django.conf import settings
# from stripe.api_resources import tax_rate
from base.models import Item, Order
import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
import json
from django.contrib import messages


stripe.api_key = settings.STRIPE_API_SECRET_KEY

# 決済完了の場合の処理
class PaySuccessView(LoginRequiredMixin, TemplateView):
  template_name = 'pages/success.html'

  
  def get(self, request, *args, **kwargs):
    # checkout_sessionで渡したクエリを取得
    order_id = request.GET.get('order_id')

    # idと現userでOrderオブジェクトのリストを取得
    orders = Order.objects.filter(user=request.user, id=order_id)

    # もし要素数が1でなければ以降に進まないようにここでreturn
    if len(orders) != 1:
      # 好みでリダイレクトやメッセージを表示してあげてもいいかもしれません。
      return super().get(request, *args, **kwargs)
    
    # １つの要素を変数へ代入
    order = orders[0]

    # 最新のOrderオブジェクトを取得し、注文確定に変更
    # 既にis_confirmed=Trueなら以降に進まないようにここでreturn
    if order.is_confirmed:
      # 好みでリダイレクトやメッセージを表示してあげてもいいかもしれません。
      return super().get(request, *args, **kwargs)

    order.is_confirmed = True  # 注文確定
    order.save()

    # 購入済みなのでカート情報を削除する
    if 'cart' in request.session:
      del request.session['cart']
    return super().get(request, *args, **kwargs)


# 処理がうまくいかなかった場合の処理
class PayCancelView(LoginRequiredMixin, TemplateView):
  template_name = 'pages/cancel.html'

  # 最新のOrderオブジェクトを取得
  def get(self, request, *args, **kwargs):

  # 現userの仮Orderのリストをすべて取得  
    orders = Order.objects.filter(user=request.user, is_confirmed=False)

    for order in orders:
      # 在庫数と販売数を元の状態に戻す
      for elem in json.loads(order.items):
        item = Item.objects.get(pk=elem['pk'])
        item.sold_count -= elem['quantity']
        item.stock += elem['quantity']
        item.save()

    # 仮オーダーを全て削除
    orders.delete()

    return super().get(request, *args, **kwargs)


# 消費税と通貨（円）の設定
tax_rate = stripe.TaxRate.create(
    display_name='消費税',
    description='消費税',
    country='JP',
    jurisdiction='JP',
    percentage=settings.TAX_RATE * 100,
    inclusive=False,  # 外税を指定（内税の場合はTrue）
)

def create_line_item(unit_amount, name, quantity):
  return {
    'price_data': {
      'currency': 'JPY',
      'unit_amount': unit_amount,
      'product_data': {'name': name, }
    },
    'quantity': quantity,
    'tax_rates': [tax_rate.id]
  }


# プロフィールが登録されているかどうかを判定する（発送に必要な項目が埋まっているか）
def check_profile_filled(profile):
    if profile.name is None or profile.name == '':
      return False
    elif profile.zipcode is None or profile.zipcode == '':
      return False
    elif profile.prefecture is None or profile.prefecture == '':
      return False
    elif profile.city is None or profile.city == '':
      return False
    elif profile.address1 is None or profile.address1 == '':
      return False
    elif profile.tel is None or profile.tel == '':
      return False
    return True


# カートに入れた商品の代金を支払う処理
# Stripeの用意した安全な支払い画面へユーザーを自動的に移動（リダイレクト）させる
class PayWithStripe(LoginRequiredMixin, View):

  def post(self, request, *args, **kwargs):
    # プロフィールが埋まっているかどうか確認
    if not check_profile_filled(request.user.profile):
      messages.error(self.request, 'エラー：住所が登録されていないため決済を行うことができません。プロフィールを入力してください。')
      return redirect('/profile/')
        
    cart = request.session.get('cart', None)
    if cart is None or len(cart) == 0:
      messages.error(self.request, 'エラー：カートが空のため決済を行うことができません。商品を追加してください。')
      return redirect('/')

    items = []  # Orderモデル用に追記
    line_items = []     # Stripeに渡すための空のリストを準備
    for item_pk, quantity in cart['items'].items():     # カートに入っている全ての商品を一つずつ取り出す
      item = Item.objects.get(pk=item_pk)               # データベースから商品の詳細（名前や価格）を取得
      line_item = create_line_item(                     # 定義した関数を使って、Stripeが読み取れる形式の商品情報を作成
          item.price, item.name, quantity)
      line_items.append(line_item)                      # 作成した商品情報をリストに追加

      # Orderモデル用に追記
      items.append({
        "pk": item.pk,
        "name": item.name,
        "image": str(item.image),
        "price": item.price,
        "quantity": quantity,
      })

      # 在庫をこの時点で引いておく、注文キャンセルの場合は在庫を戻す
      # 売上も加算しておく
      item.stock -= quantity        # 在庫数からマイナス
      item.sold_count += quantity   # 売上はプラス
      item.save()


    # 仮注文を作成（is_confirmed=False）
    # 決済が成功したか確認できていないが、事前にOrder情報を作成しておく    
    order = Order.objects.create(
      user=request.user,
      uid=request.user.pk,
      items=json.dumps(items),
      shipping=serializers.serialize("json", [request.user.profile]),
      amount=cart['total'],
      tax_included=cart['tax_included_total']
    )


    checkout_session = stripe.checkout.Session.create(
      customer_email=request.user.email,
      payment_method_types=['paypay', 'card', 'konbini'],   # 支払方法の指定（'konbini','paypay'など）
      line_items=line_items,                            # 左側の line_items はStripeの設定項目名、右側の line_items はfor文で作成した商品リストの変数
      mode='payment',
      # success_urlには、クエリで注文IDを渡しておく
      success_url=f'{settings.MY_URL}/pay/success/?order_id={order.pk}',    # 決済が成功したときに戻すurl
      cancel_url=f'{settings.MY_URL}/pay/cancel/',      # 決済に失敗したときに戻すurl
    )
    return redirect(checkout_session.url)               # Stripeが作った決済セッションのページへのURL


