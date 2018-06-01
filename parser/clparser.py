"""parser module for parsing data from provided urls"""
import json

from requests import Response
from requests_html import HTMLSession


def parse_body(raw_body):
    """parse data represented as string to json"""
    body = raw_body.replace("\n", "\\n")  # repace newlines to be able to parse json'
    body = json.loads(body)
    return body


def parse_page(page_url):
    """retrieve and parse html page"""
    result = {
        "page_head": None,
        "postingtitletext": None,
        "price_text": None,
        "price": None,
        "housing": None,
        "titletextonly": None,
        "thumbs": None,
    }
    session = HTMLSession()
    resp: Response = session.get(page_url)

    # get post body
    post_body = resp.html.find(".body", first=True)

    # posting title
    posting_title = post_body.find(".postingtitle", first=True)
    posting_title_text = posting_title.find(".postingtitletext", first=True)
    result["postingtitletext"] = posting_title_text.text

    # price
    price_text = posting_title_text.find(".price", first=True).text
    price = int(price_text.strip().replace("$", ""))
    result["price_text"] = price_text
    result["price"] = price

    # housing
    housing_el = posting_title_text.find(".housing", first=True)
    if housing_el is not None:
        result["housing"] = housing_el.text

    # titletextonly
    titletextonly = posting_title_text.find("#titletextonly", first=True).text
    result["titletextonly"] = titletextonly

    # district ?
    district_el = posting_title_text.find("small", first=True)
    if district_el is not None:
        result["district"] = district_el.text


    # userbody
    userbody = post_body.find(".userbody", first=True)
    thumbs = userbody.find("#thumbs", first=True).links
    result["thumbs"] = list(thumbs)

    return result
