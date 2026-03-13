from django.shortcuts import render
from django.views.generic import ListView, DetailView
from base.models import Item, Category, Tag

# class IndexListViews(ListView):
#   model = Item
#   template_name = 'pages/index.html'


"""
関数で書く場合
---
def indexViews(request):
  object_list = Item.objects.all()
  # Webページに表示したいデータを用意
  context = {
    'object_list' : object_list,
  }
  # 'index.html'に、contextのデータをレンダリングして表示させる
  return render(request, 'pages/index.html', context)
"""
"""
  render() について
  render = レンダリングの略でブラウザが表示できるHTMLを生成する
  例えば
  Pythonコードで用意した具体的な情報であるデータ（コンテキスト）「{'name': '太郎'}」を
  レンダリングしHTMLコード「<p>ユーザー名：太郎</p>」に変換することができる。

"""


class IndexListViews(ListView):
  model = Item
  template_name = 'pages/index.html'
  queryset = Item.objects.filter(is_published=True)   # queryset：querysetを使うことでフィルターを簡単にかけることができる


# 詳細ページ
class ItemDetailView(DetailView):
  model = Item
  template_name = 'pages/item.html'


# カテゴリーを指定した際に表示するアイテム一覧
class CategoryListView(ListView):
  model = Item
  template_name = 'pages/list.html'
  paginate_by = 4   # 1ページにいくつ表示するか

  def get_queryset(self):
    self.category = Category.objects.get(slug=self.kwargs['pk'])
    return Item.objects.filter(
      is_published=True, category=self.category)    # is_published=True：公開されているものだけを表示

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["title"] = f"カテゴリー： #{self.category.name}"
    return context

# タグを指定した際に表示するアイテム一覧
class TagListView(ListView):
  model = Item
  template_name = 'pages/list.html'
  paginate_by = 4

  def get_queryset(self):
    self.tag = Tag.objects.get(slug=self.kwargs['pk'])
    return Item.objects.filter(is_published=True, tags=self.tag)

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context["title"] = f"タグ： #{self.tag.name}"
    return context
  
