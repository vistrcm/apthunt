"""parser module for parsing data from provided urls"""
import json

from requests_html import HTMLSession


def parse_body(raw_body):
    """parse data represented as string to json"""
    body = raw_body.replace("\n", "\\n")  # repace newlines to be able to parse json'
    body = json.loads(body)
    return body


def parse_page(page_url):
    """retrieve and parse html page"""
    result = {
        "page_text": None,
        "page_head": None,
        "postingtitletext": None,
        "price_text": None,
        "price": None,
        "housing": None,
        "titletextonly": None
    }
    session = HTMLSession()
    r = session.get(page_url)

    result["page_text"] = r.text  # raw page
    result["page_head"] = r.html.xpath('head/title')[0].text  # html head

    # get post body
    post_body = r.html.find(".body", first=True)

    # posting title
    postingtitletext = post_body.find(".postingtitle", first=True).find(".postingtitletext", first=True)
    result["postingtitletext"] = postingtitletext.text

    # price
    price_text = postingtitletext.find(".price", first=True).text
    price = int(price_text.strip().replace("$", ""))
    result["price_text"] = price_text
    result["price"] = price

    # housing
    housing = postingtitletext.find(".housing", first=True).text
    result["housing"] = housing

    # titletextonly
    titletextonly = postingtitletext.find("#titletextonly", first=True).text
    result["titletextonly"] = titletextonly

    # district ?
    district = postingtitletext.find("small", first=True).text
    result["district"] = district

    return result
