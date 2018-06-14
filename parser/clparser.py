"""parser module for parsing data from provided urls"""
import json
import sys

from requests_html import HTMLSession, HTMLResponse


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
    result["postingbody"] = userbody.find("section#postingbody", first=True).text

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
    print(json.dumps(parse_page(sys.argv[1]), indent=4))
    # print(parse_page(parse_page(sys.argv[1])))
