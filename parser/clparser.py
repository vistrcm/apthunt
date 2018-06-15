"""parser module for parsing data from provided urls"""
import json
import sys

from requests_html import HTMLSession, HTMLResponse


class PostRemovedException(Exception):
    """Exception to handle post removal situations"""
    pass


def parse_request_body(raw_body):
    """parse data represented as string to json"""
    body = raw_body.replace("\n", "\\n")  # repace newlines to be able to parse json'
    body = json.loads(body)
    return body


def parse_attr_groups(attrgroups):
    """parse attribute groups

    return list of text values of all spans"""
    attrs = []
    for group in attrgroups:
        for attr in group.find("span"):
            attrs.append(attr.text)
    return attrs


def parse_price(posting_title_text):
    """parse price"""
    price_data = {}
    price_element = posting_title_text.find(".price", first=True)
    if price_element:
        price_text = price_element.text
        price = int(price_text.strip().replace("$", ""))
        price_data["price_text"] = price_text
        price_data["price"] = price

    return price_data


def post_removed(post_body):
    """check for post removal.

    search post body for words 'This posting has been flagged for removal.'
    Return True if found False in over case."""
    sel = "#userbody > div.removed"
    div_removed = post_body.find(sel, first=True)
    if div_removed and div_removed.text.startswith("This posting has been flagged for removal."):
        return True
    return False


def parse_page(page_url):
    """retrieve and parse html page"""
    # result format is here to have consistent results with default None
    result = {
        "page_head": None,
        "postingtitletext": None,
        "price_text": None,
        "price": None,
        "housing": None,
        "titletextonly": None,
        "thumbs": None,
        "data_latitude": None,
        "data_longitude": None,
        "map_address": None,
        "map_link": None,
        "attrs": None,
        "postingbody": None,
        "notices": None,
    }

    post_body = get_page(page_url)

    # chef for removed
    if post_removed(post_body):
        raise PostRemovedException(post_body)

    # posting title
    posting_title = post_body.find(".postingtitle", first=True)
    posting_title_text = posting_title.find(".postingtitletext", first=True)
    result["postingtitletext"] = posting_title_text.text

    # price
    result.update(parse_price(posting_title_text))

    # housing
    housing_el = posting_title_text.find(".housing", first=True)
    if housing_el is not None:
        result["housing"] = housing_el.text.strip(" /-")

    # titletextonly
    result["titletextonly"] = posting_title_text.find("#titletextonly", first=True).text

    # district ?
    district_el = posting_title_text.find("small", first=True)
    if district_el is not None:
        result["district"] = district_el.text.strip(" ()")

    # userbody
    userbody = post_body.find(".userbody", first=True)
    thumbs = userbody.find("#thumbs", first=True)
    if thumbs:
        result["thumbs"] = list(thumbs.links)

    # map
    map_and_attrs = userbody.find(".mapAndAttrs", first=True)
    result.update(parse_map(map_and_attrs))

    # attrgroups
    attrgroups = map_and_attrs.find("p.attrgroup")
    attrs = parse_attr_groups(attrgroups)
    if attrs:
        result["attrs"] = attrs

    # posting body
    postingbody_raw = userbody.find("section#postingbody", first=True).text
    result["postingbody"] = postingbody_raw.replace("QR Code Link to This Post\n", "")

    # notices
    result["notices"] = [n.text for n in userbody.find("ul.notices", first=True).find("li")]
    return result


def parse_map(map_and_attrs):
    """parse mapAndAttrs. extract map data. return as dict"""
    map_data = {}

    posting_map = map_and_attrs.find("#map", first=True)
    if not posting_map:  # no map found
        return {}

    map_data["data_latitude"] = float(posting_map.attrs["data-latitude"])
    map_data["data_longitude"] = float(posting_map.attrs["data-longitude"])
    map_address = map_and_attrs.find(".mapaddress", first=True)
    if map_address:
        map_data["map_address"] = map_address.text
    map_link = map_and_attrs.find("p.mapaddress", first=True).find("a", first=True)
    if map_link:
        map_data["map_link"] = map_link.attrs["href"]

    return map_data


def get_page(page_url):
    """get web page. return html representation"""
    session = HTMLSession()
    resp: HTMLResponse = session.get(page_url)
    # get post body
    post_body = resp.html.find(".body", first=True)
    return post_body


if __name__ == "__main__":
    page = sys.argv[1]
    try:
        resp = json.dumps(parse_page(page), indent=4)
    except PostRemovedException:
        resp = {"message": "post removed", "item": page}
    print(resp)
    # print(parse_page(parse_page(sys.argv[1])))
