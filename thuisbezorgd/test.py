import requests

url = 'https://www.thuisbezorgd.nl/bestellen/eten/amsterdam-1016'
headers = {
    'authority': 'www.thuisbezorgd.nl',
    'method': 'GET',
    'path': '/bestellen/eten/amsterdam-1016',
    'scheme': 'https',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,bn;q=0.8',
    'cache-control': 'max-age=0',
    'if-modified-since': 'Thu, 11 May 2023 08:00:00 GMT',
    'referer': 'https://www.thuisbezorgd.nl/',
    'sec-ch-ua': 'Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Linux',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'cookie': 'je-auser=3a2dac00-e156-4c96-bb73-90df1bee9aec; localFavorites=[]; _ga_raw=0187c1d1978e0016f6c6badc063a03069003906100bd0; _ga=GA1.1.0187c1d1978e0016f6c6badc063a03069003906100bd0; cookieConsent=full; customerCookieConsent=%5B%7B%22consentTypeId%22%3A100%2C%22consentTypeName%22%3A%22full%22%2C%22isAccepted%22%3Atrue%2C%22decisionAt%22%3A%222023-04-27T08%3A26%3A03.0000000%2B00%3A00%22%7D%5D; _gcl_au=1.1.1165181458.1682583964; _scid=f790a766-1ce0-40dc-a495-0dea1c1ade2e; _pin_unauth=dWlkPVpqUmpPVEptTVRjdE5tSmlZeTAwTkdKaUxUZ3dOREF0T1dFeVpqUmpZV1V5T0dSag; _tt_enable_cookie=1; _ttp=CYdz_Kkl1OCceIUNzPxb4xYPwo0; _hjSessionUser_1264618=eyJpZCI6ImViZWFhOGM5LTM0YmEtNTg5Ni04YjhhLThhZWZhMmI1ZDBlMSIsImNyZWF0ZWQiOjE2ODI1ODM5NjU0OTAsImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample_1264618=1; _hjSession_1264618=eyJpZCI6IjBhYjRlMWEwLTZkNGYtNDIzMC05MTY2LWZmMTliNjkyMTE3ZiIsImNyZWF0ZWQiOjE2ODM3OTAwOTcxOTksImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=1; _sctr=1%7C1683741600000; cf_clearance=suozkZ7lHpnN6xOHaCDsPBSJcfuwsTqVTXXrCqIxAlQ-1683791874-0-160; __cf_bm=tlijIBn5SbS6EYXfl495JtEKoFTVjG4K7GpZ9ImSNkw-1683791960-0-AbExHSMMV+0ZMAe5i3XRNRLiKzQLPsKjK9h3TeFLvl7eKnmNQV3ehTaligN9InVtNh9fnJ2V3aQpR31Vq+9eADnfnMwZaPd+qyCXET39W0cCcl6YampUwkMQTGCNvlLDNzKJCkdOjjRp48BRhPgZFY2Zpnb1u0EcpfyRdZsXFFlM; cwSession=%7B%22id%22%3A%227e5291ad-baad-4c4a-b83a-de7f6376feed%22%7D; userExperiments=%7B%22id%22%3A%22ae13c987-729c-4eb3-913c-f448b0290724%22%2C%22attributes%22%3A%7B%22viewportType%22%3A%22desktop%22%2C%22countryCode%22%3A%22nl%22%2C%22isBot%22%3Afalse%2C%22isNativeAppWebView%22%3Afalse%2C%22isE2E%22%3Afalse%2C%22pageName%22%3A%22%2Frestaurant-list%22%7D%2C%22flags%22%3A%5B%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22skipLegacyCookiesCompatibility%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22cashAmountSelectionDropdown%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22featureFlagExample%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22showGroceries%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22googleSignIn%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22globalFeedback%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22redirectToTestLocation%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22personalInfoPage%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22topRankCpc%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22sendSessionTokenForAutosuggestion%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22serviceChargeAdditionalInfo%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22newOrderIdentifier%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22giftCardShop%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22languageSelector%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22reorder%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22becomeACourier%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22isDynamicDeliveryFeeEnabled%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22ageVerification%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22cachingRestaurantListPage%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22menuAndCheckoutLocationPanelHidden%22%7D%2C%7B%22type%22%3A%22feature%22%2C%22key%22%3A%22uefaCampaign%22%7D%5D%2C%22version%22%3A%223190%22%7D; _uetsid=65381680efcd11ed9725b7fb153be0dc; _uetvid=26be4d30e4d511ed87a5694e38f1158e; _ga_4PH28YDTSD=GS1.1.1683790095.3.1.1683792149.0.0.0; _scid_r=f790a766-1ce0-40dc-a495-0dea1c1ade2e; activeAddress=%7B%22address%22%3A%7B%22location%22%3A%7B%22city%22%3A%22Amsterdam%22%2C%22country%22%3A%22%22%2C%22deliveryAreaId%22%3A%22935435%22%2C%22district%22%3A%22%22%2C%22lat%22%3A52.37074720248934%2C%22lng%22%3A4.881877308666887%2C%22locationSlug%22%3A%22amsterdam-1016%22%2C%22placeId%22%3A%22%22%2C%22postalCode%22%3A%221016%22%2C%22state%22%3A%22Noord-Holland%22%2C%22street%22%3A%22%22%2C%22streetNumber%22%3A%22%22%2C%22streetAddress%22%3A%22%22%2C%22takeawayPostalCode%22%3A%221016%22%2C%22formattedAddress%22%3A%221016%20Amsterdam%22%2C%22id%22%3A%22%22%2C%22timeZone%22%3A%22%22%7D%2C%22shippingDetails%22%3A%7B%7D%2C%22savedAddressId%22%3A%22%22%7D%2C%22searchString%22%3A%221016%20Amsterdam%22%7D; utag_main=v_id:0187c1d1978e0016f6c6badc063a03069003906100bd0$_sn:2$_se:111$_ss:0$_st:1683794026434$dc_visit:2$ses_id:1683790089611%3Bexp-session$_pn:9%3Bexp-session$dc_event:30%3Bexp-session$dc_region:eu-west-1%3Bexp-session; PHPSESSID=oeh4mkl43u8209kl283o4k3ucq; _dd_s=rum=1&id=1d68ad1c-7a4d-4646-9124-19475914b875&created=1683790089066&expire=1683793131135',
}
# res = requests.get(url, headers=headers)
# print(res.status_code)
# print(res.content)

from requests_html import HTMLSession
s = HTMLSession()
s.headers['user-agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
r = s.get(url)
r.html.render(timeout=8000)
print(r.status_code)
# print(r.content)
