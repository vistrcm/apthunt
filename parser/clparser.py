"""parser module for parsing data from provided urls"""
import json
import locale
import re
import sys
from typing import Dict, Union

from aws_xray_sdk import global_sdk_config
from aws_xray_sdk.core import xray_recorder
from requests_html import HTMLSession, HTMLResponse

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


class PostRemovedException(Exception):
    """Exception to handle post removal situations"""


class CL404Exception(Exception):
    """Exception to handle 404 status codes"""


@xray_recorder.capture('parse_request_body')
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


def parse_price(posting_title_text) -> Dict[str, Union[str, int]]:
    """parse price"""
    price_data = {}
    price_element = posting_title_text.find(".price", first=True)
    if price_element:
        price_text = price_element.text
        no_sign = price_text.strip().strip("$")
        price = locale.atoi(no_sign)
        price_data["price_text"] = price_text
        price_data["price"] = price

    return price_data


def post_removed(post_body):
    """check for post removal.

    search post body for words 'This posting has been flagged for removal.'
    or 'This posting has been deleted by its author.'
    Return True if found False in over case."""
    sel = "#userbody > div.removed"
    div_removed = post_body.find(sel, first=True)
    if div_removed:
        # check for text in div
        flagged_removal = div_removed.text.startswith("This posting has been flagged for removal.")
        removed = div_removed.text.startswith("This posting has been deleted by its author.")
        if flagged_removal or removed:
            return True
    return False


def get_bedrooms(housing):
    """parse amount of bedrooms from 'housing' field"""
    bedrooms = None
    # bedrooms
    match = re.search(r'(\d+)br.*', housing)
    if match:
        bedrooms = float(match.group(1))
    return bedrooms


def get_area(item):
    """parse area from 'housing' field"""
    area = None
    housing = item["housing"]
    match = re.search(r'(\d+)ft2', housing)
    if match:
        area = float(match.group(1))
    return area


def get_type(item):
    """parse type of the item from 'attrs' field"""
    attrs = item["attrs"]
    if not isinstance(attrs, list):
        return None
    types = {"apartment", "townhouse", "loft", "land", "house", "duplex", "flat", "condo", "cottage/cabin"}
    return ",".join(sorted(types & set(attrs)))


@xray_recorder.capture('parse_page')
def parse_page(page_url):
    """retrieve and parse html page"""
    # result format is here to have consistent results with default None
    result = {
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
        "bedrooms": None,
        "area": None,
        "type": None,
        "catsok": None,
        "dogsok": None,
        "garagea": None,
        "garaged": None,
        "furnished": None,
        "laundryb": None,
        "laundrys": None,
        "wd": None,
        "nthumbs": None,
    }

    post_body = get_page(page_url)

    # check for removed
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
    notices = userbody.find("ul.notices", first=True)
    if notices is not None:
        result["notices"] = [n.text for n in userbody.find("ul.notices", first=True).find("li")]

    # additional fields
    result["bedrooms"] = get_bedrooms(result["housing"])
    result["area"] = get_area(result)
    result["type"] = get_type(result)
    result["catsok"] = "cats are OK - purrr" in result.get("attrs", [])
    result["dogsok"] = "dogs are OK - wooof" in result.get("attrs", [])
    result["garagea"] = "attached garage" in result.get("attrs", [])
    result["garaged"] = "detached garage" in result.get("attrs", [])
    result["furnished"] = "furnished" in result.get("attrs", [])
    result["laundryb"] = "laundry in bldg" in result.get("attrs", [])
    result["laundrys"] = "laundry on site" in result.get("attrs", [])
    result["wd"] = "w/d in unit" in result.get("attrs", [])
    result["nthumbs"] = len(result["thumbs"]) if result["thumbs"] is not None else 0
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
    map_link_p = map_and_attrs.find("p.mapaddress", first=True)
    if map_link_p:
        map_link = map_link_p.find("a", first=True)
        if map_link:
            map_data["map_link"] = map_link.attrs["href"]

    return map_data


@xray_recorder.capture('get_page')
def get_page(page_url):
    """get web page. return html representation"""
    session = HTMLSession()
    resp: HTMLResponse = session.get(page_url)
    if resp.status_code == 404:
        raise CL404Exception
    # get post body
    post_body = resp.html.find(".body", first=True)
    return post_body


if __name__ == "__main__":
    global_sdk_config.set_sdk_enabled(False)

    PAGE = sys.argv[1]
    try:
        print(json.dumps(parse_page(PAGE), indent=4))
    except (PostRemovedException, CL404Exception):
        print({"message": "post removed", "item": PAGE})
