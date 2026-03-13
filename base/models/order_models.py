"""
注文履歴のモデル
"""

from django.db import models
import datetime
from django.contrib.auth import get_user_model
 
# datetimeを使って日時をマイクロ秒単位まで取得
def custom_timestamp_id():
    dt = datetime.datetime.now()
    return dt.strftime('%Y%m%d%H%M%S%f')
 
# 注文履歴のモデル 
class Order(models.Model):
    # 注文ID
    id = models.CharField(default=custom_timestamp_id,
                          editable=False, primary_key=True, max_length=50)
    # ユーザー情報を渡している
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    # 注文履歴におけるユーザーid
    uid = models.CharField(editable=False, max_length=50)
    # 決済処理済みかどうか（success.viwesに行ったときのみだけtrue）
    is_confirmed = models.BooleanField(default=False)
    # 合計金額
    amount = models.PositiveIntegerField(default=0)
    # 税込み金額
    tax_included = models.PositiveIntegerField(default=0)
    # 購入した商品詳細
    items = models.JSONField()
    # プロフィール情報の配送先住所
    shipping = models.JSONField()
    # 発送された日付
    shipped_at = models.DateTimeField(blank=True, null=True)
    # キャンセルされた日付
    canceled_at = models.DateTimeField(blank=True, null=True)
    # 管理者だけのメモ書き
    memo = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 履歴の作成日
    updated_at = models.DateTimeField(auto_now=True)      # 履歴の最終更新日
 
    def __str__(self):
        return self.id
