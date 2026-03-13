# VegeKet（ベジケット）
公開中URL：
https://vegeket-app-v1-f32319ce22f2.herokuapp.com/

---

## 概要
VegeKetは、Djangoを使用して構築された、野菜・果物の産地直送をコンセプトにしたオンライン売買プラットフォームです。
ユーザー登録をはじめ、顧客管理、商品管理、決済、発送までの一連のフローを行えるよう設計されています。

## 主な機能
- **ユーザー管理機能**: 
  - カスタムユーザーモデル（Email認証ベース）によるログイン・会員登録
- **商品管理・画像保存**:
  - `Cloudinary` を使用したクラウドストレージへの画像保存
- **決済システム**:
  - `Stripe API` を利用した安全なオンライン決済の実装


## 使用技術
- **Backend**: Python 3.9 / Django 3.2.13
- **Database**: MySQL (Heroku JAWSDB)
- **Frontend**: HTML5 / CSS3 / Bootstrap 5 / JavaScript
- **Infrastructure**: Heroku / Cloudinary (Image Hosting)
- **Payment**: Stripe API

