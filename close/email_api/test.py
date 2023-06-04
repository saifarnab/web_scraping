import pytracking

full_url = "http://0.0.0.0:8055/email-tracker/api/eyJtZXRhZGF0YSI6IHsiY3VzdG9tZXJfaWQiOiAxfX0="
tracking_result = pytracking.get_open_tracking_result(
    full_url, base_open_tracking_url="http://0.0.0.0:8055/email-tracker/api/1*1pixel-img")

print(tracking_result)