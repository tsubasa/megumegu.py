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

設定例
------

```
MariaDB [megumegu]> select * from mm_site;
+----+-----------------------------------------+-----------------------------------------------------+------------------+--------+
| id | name                                    | url                                                 | schedule         | enable |
+----+-----------------------------------------+-----------------------------------------------------+------------------+--------+
|  1 | Puella Magi Madoka Magica               | http://www.madoka-magica.com/news/                  | * * * * *        |      1 |
|  2 | Re: Life in a Different World from Zero | http://api.syosetu.com/writernovel/235132.Atom      | 0-2 1 * * *      |      1 |
|  3 | Girls & Panzar Blog                     | http://girls-und-panzer.at.webry.info/rss/index.rdf | * 0,9-23 * * *   |      1 |
|  4 | MADOGATARI-Ten OFFICIAL WEBSITE         | http://www.madogatari.jp/news/news.xml              | */2 0,9-23 * * * |      1 |
|  5 | SHAFT OFFICIAL WEBSITE                  | http://shaft-web.co.jp/news/                        | * * * * *        |      1 |
|  6 | Lovelive! Sunshine!! Official Website   | http://www.lovelive-anime.jp/uranohoshi/news.php    | * 0,7-23 * * *   |      1 |
+----+-----------------------------------------+-----------------------------------------------------+------------------+--------+

MariaDB [megumegu]> select * from mm_option;
+---------+-------+-----------------------+-----------+--------------------+------------+--------------------+---------+-----------+---------+
| site_id | model | query_entry           | query_id  | query_title        | query_link | query_content      | options | start_tag | end_tag |
+---------+-------+-----------------------+-----------+--------------------+------------+--------------------+---------+-----------+---------+
|       1 | DOM   | #newsList li          | .newsSets | p.newsTitle::text  | NULL       | dd                 | NULL    | NULL      | NULL    |
|       2 | ATOM  | NULL                  | NULL      | NULL               | NULL       | NULL               | NULL    | NULL      | NULL    |
|       3 | XML   | NULL                  | NULL      | NULL               | NULL       | NULL               | NULL    | NULL      | NULL    |
|       4 | DOM   | resultset content     | id        | title              | NULL       | message            | escape  | NULL      | NULL    |
|       5 | DOM   | #news .entry          | NULL      | .entry-title::text | NULL       | .entry-content p   | trim    | <body     | </body> |
|       6 | DOM   | #contents .infobox    | .infobox  | .title::text       | NULL       | p::text            | NULL    | NULL      | NULL    |
+---------+-------+-----------------------+-----------+--------------------+------------+--------------------+---------+-----------+---------+
```
