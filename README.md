megumegu.py
===========

ウェブサイト更新チェックスクリプト

主な機能
--------

- サイトの更新情報を取得
- DOM, RSS(v1.0/2.0), ATOMなどの文書フォーマットのパースに対応
- 取得した更新内容を各サービス(Twitter, Slackなど)に通知

TODO
----

- JSONフォーマットのパースに対応
- 画像などのバイナリフォーマットに対応

使い方
------

```bash
python megumegu.py --config settings.cfg
```
