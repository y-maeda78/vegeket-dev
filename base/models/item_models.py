from django.db import models
from django.utils.crypto import get_random_string
import os

def create_id():
    return get_random_string(22)

def upload_image_to(instance, filename):
    item_id = instance.id
    return os.path.join('static', 'items', str(item_id), filename)

# カテゴリーの作成
class Category(models.Model):
    slug = models.CharField(max_length=32, primary_key=True)    # URLに表示するようにslugに
    name = models.CharField(max_length=32)                      # 画面上に表示される名前 
    def __str__(self):
        return self.name

# タグの作成
class Tag(models.Model):
    slug = models.CharField(max_length=32,primary_key=True)
    name = models.CharField(max_length=32)
    def __str__(self):
        return self.name


# Itemで呼び出せるように定義
class Item(models.Model):   # Modelは、jangoのクラスで継承している
    id = models.CharField(default=create_id, primary_key=True,
                          max_length=22, editable=False)
    # id = models.AutoField(primary_key=True) 
    name = models.CharField(default='', max_length=50)
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField(default='', blank=True, verbose_name='説明')
    sold_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False, verbose_name='公開')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(default="", blank=True,
                              upload_to=upload_image_to)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                 null=True, blank=True) # ForeignKeyとon_delete=はセット
    tags = models.ManyToManyField(Tag)   #複数設定することを前提にtagsとしManyToManyFieldで定義

    # インスタンスの生成（returnでnameを返すことで、一覧画面で名前が表示される）
    def __str__(self):
        return self.name