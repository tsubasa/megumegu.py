from .config import MeguTestCase

from megumegu.parsers import DomParser, AtomParser

class MeguParserTests(MeguTestCase):

    def testdomparser(self):
        data = """<html>
            <body>
                <div>
                    <h1>hogehoge</h1>
                    <p>fugafuga</p>
                </div>
            </body>
            </html>
            """

        ret = DomParser(data=data,
                        url='http://example.com', url2=None,
                        query_contents='div',
                        query_title='h1::text',
                        query_content='p').parse()

        self.assertEqual(ret['title'], 'hogehoge')
        self.assertEqual(ret['content'], 'fugafuga')

    def testatomparser(self):
        data = """<?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
              <id>http://mypage.syosetu.com/235132/</id>
              <title><![CDATA[EXAMPLE_TITLE]]></title>
              <author>
                <name>EXAMPLE_AUTHOR_NAME</name>
              </author>
              <updated>1971-01-01T00:00:00+00:00</updated>
              <link rel="self" href="http://example.com"/>
              <subtitle><![CDATA[EXAMPLE_SUB_TITLE]]></subtitle>
              <generator>FEED</generator>
              <entry>
                <id>1</id>
                <title><![CDATA[EXAMPLE_ENTRY_TITLE]]></title>
                <updated>1971-01-01T00:00:00+00:00</updated>
                <link rel="alternate" href="http://example.com"/>
                <summary><![CDATA[]]></summary>
              </entry>
              <entry>
                <id>2</id>
                <title><![CDATA[EXAMPLE_ENTRY_TITLE]]></title>
                <updated>1971-01-01T00:00:00+00:00</updated>
                <link rel="alternate" href="http://example.com"/>
                <summary><![CDATA[]]></summary>
              </entry>
            </feed>
            """

        ret = AtomParser(data=data).parse()

        self.assertEqual(ret['title'], 'EXAMPLE_ENTRY_TITLE')
        self.assertEqual(ret['url'], 'http://example.com')

        self.assertEqual(len(AtomParser(data=data)), 2)
