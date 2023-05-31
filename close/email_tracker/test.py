import pytracking

click_tracking_url = pytracking.get_click_tracking_url(
    "http://www.example.com/?query=value", {"customer_id": 1},
    base_click_tracking_url="https://trackingdomain.com/path/",
    webhook_url="http://requestb.in/123", include_webhook_url=True)

print(click_tracking_url)
