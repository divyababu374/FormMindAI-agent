import pytest
from app.services.ingestion.url_parser import parse_and_validate_url

def test_valid_google_form_urls():
    url1 = "https://docs.google.com/forms/d/e/1FAIpQLSc9876543210abcdef/viewform"
    res1 = parse_and_validate_url(url1)
    assert res1["is_valid"] is True
    assert res1["source_type"] == "google_form"
    assert res1["resource_id"] == "1FAIpQLSc9876543210abcdef"

    url2 = "https://docs.google.com/forms/d/1a2b3c4d5e6f7g8h/edit"
    res2 = parse_and_validate_url(url2)
    assert res2["is_valid"] is True
    assert res2["source_type"] == "google_form"
    assert res2["resource_id"] == "1a2b3c4d5e6f7g8h"

    url3 = "https://forms.gle/XYZ98765abc"
    res3 = parse_and_validate_url(url3)
    assert res3["is_valid"] is True
    assert res3["source_type"] == "google_form"
    assert res3["resource_id"] == "XYZ98765abc"
    assert res3["normalized_url"] == "https://forms.gle/XYZ98765abc"

def test_valid_google_sheet_urls():
    url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0"
    res = parse_and_validate_url(url)
    assert res["is_valid"] is True
    assert res["source_type"] == "google_sheet"
    assert res["resource_id"] == "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"

def test_valid_microsoft_form_urls():
    # Response Page with ?id=
    url1 = "https://forms.office.com/Pages/ResponsePage.aspx?id=v4j5cvGGr0GRqy180BHbR6xK1o435"
    res1 = parse_and_validate_url(url1)
    assert res1["is_valid"] is True
    assert res1["source_type"] == "microsoft_form"
    assert res1["resource_id"] == "v4j5cvGGr0GRqy180BHbR6xK1o435"

    # Short URL format: forms.office.com/r/...
    url2 = "https://forms.office.com/r/k7Y8z9A1b2"
    res2 = parse_and_validate_url(url2)
    assert res2["is_valid"] is True
    assert res2["source_type"] == "microsoft_form"
    assert res2["resource_id"] == "k7Y8z9A1b2"
    assert res2["is_short_url"] is True

    # Design Page format: FormId=...
    url3 = "https://forms.office.com/Pages/DesignPageV2.aspx?subpage=design&FormId=v4j5cvGGr0GRqy180BHbR6xK1o435"
    res3 = parse_and_validate_url(url3)
    assert res3["is_valid"] is True
    assert res3["source_type"] == "microsoft_form"
    assert res3["resource_id"] == "v4j5cvGGr0GRqy180BHbR6xK1o435"

    # forms.microsoft.com domain
    url4 = "https://forms.microsoft.com/r/xyz9876"
    res4 = parse_and_validate_url(url4)
    assert res4["is_valid"] is True
    assert res4["source_type"] == "microsoft_form"

def test_invalid_urls():
    res_empty = parse_and_validate_url("")
    assert res_empty["is_valid"] is False

    res_random = parse_and_validate_url("https://random-website.com/my-survey")
    assert res_random["is_valid"] is False
    assert "Microsoft Forms" in res_random["error_message"]

