import io
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import patch

from scrapper_kb.ingest import ingest
from scrapper_kb.rss import MAX_FEED_BYTES, load_rss

SOURCE = {"type": "rss", "category": "development",
          "params": {"url": "https://feed.example/rss", "max_age_hours": 48}}


def item(link="/article", date=None, title="Angular update"):
    date = date or format_datetime(datetime.now(timezone.utc) - timedelta(hours=1))
    return (f"<item><title>{title}</title><link>{link}</link><pubDate>{date}</pubDate>"
            "<description>&lt;p&gt;Angular &amp;amp; TypeScript&lt;/p&gt;</description></item>")


def rss(*items):
    return ("<rss version='2.0'><channel>" + "".join(items) + "</channel></rss>").encode()


class RssTests(unittest.TestCase):
    def load(self, payload, source=SOURCE):
        with patch("scrapper_kb.rss.urlopen", return_value=io.BytesIO(payload)) as fetch:
            docs = load_rss(source)
        return docs, fetch

    def test_rss_plain_text_stable_ids_and_duplicate_links(self):
        payload = rss(item(), item(), item("/second"))
        docs, fetch = self.load(payload)
        self.assertEqual(len(docs), 2)
        self.assertEqual(docs[0].source_url, "https://feed.example/article")
        self.assertEqual(docs[0].content, "Angular & TypeScript")
        self.assertEqual(docs[0].category, "development")
        self.assertEqual(docs[0].id, self.load(payload)[0][0].id)
        self.assertNotEqual(docs[0].id, docs[1].id)
        self.assertEqual(fetch.call_args.kwargs["timeout"], 10)
        self.assertEqual(fetch.call_count, 1)

    def test_atom_alternate_link_updated_date_and_xhtml_content(self):
        date = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        payload = f"""<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><title>Angular</title><link rel="self" href="/metadata"/>
          <link href="/article"/><updated>{date}</updated>
          <content type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">
          <p>Angular &amp; TypeScript</p></div></content></entry></feed>""".encode()
        docs, _ = self.load(payload)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].source_url, "https://feed.example/article")
        self.assertEqual(docs[0].content, "Angular & TypeScript")

    def test_invalid_old_future_missing_dates_and_unsafe_links_are_skipped(self):
        old = format_datetime(datetime.now(timezone.utc) - timedelta(days=10))
        future = format_datetime(datetime.now(timezone.utc) + timedelta(days=1))
        payload = rss(item("/old", old), item("/future", future),
                      item("/bad", "garbage"), item("javascript:alert(1)"),
                      item(title=""), "<item><title>Undated</title><link>/undated</link></item>",
                      item())
        docs, _ = self.load(payload)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].source_url, "https://feed.example/article")

    def test_max_items(self):
        source = {**SOURCE, "params": {**SOURCE["params"], "max_items": 1}}
        docs, _ = self.load(rss(item(), item("/second")), source)
        self.assertEqual(len(docs), 1)

    def test_failed_feed_does_not_prevent_other_sources(self):
        with patch("scrapper_kb.rss.urlopen",
                   side_effect=[OSError("offline"), io.BytesIO(rss(item()))]):
            with self.assertLogs("scrapper_kb.rss", level="WARNING"):
                docs = ingest([SOURCE, SOURCE])
        self.assertEqual(len(docs), 1)

    def test_invalid_oversized_and_dtd_feeds_are_rejected(self):
        for payload in (b"<broken", b"<html/>", b"x" * (MAX_FEED_BYTES + 1),
                        b"<!DOCTYPE rss [<!ENTITY x 'boom'>]><rss/>",
                        "<!DOCTYPE rss><rss/>".encode("utf-16")):
            with self.subTest(payload=payload[:40]):
                with self.assertLogs("scrapper_kb.rss", level="WARNING"):
                    docs, _ = self.load(payload)
                self.assertEqual(docs, [])

    def test_bad_configuration_fails_before_fetching(self):
        for params in ({"url": "file:///secret"}, {"timeout_seconds": 0},
                       {"max_items": 0}, {"max_age_hours": -1}):
            source = {**SOURCE, "params": {**SOURCE["params"], **params}}
            with self.subTest(params=params):
                with patch("scrapper_kb.rss.urlopen") as fetch:
                    with self.assertRaises(ValueError):
                        load_rss(source)
                    fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()

