import json
from seleniumwire import webdriver
from seleniumwire.utils import decode
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# {
#     "poiID": "IT.1RB9NY5SLZGAB",
#     "location": {
#         "latitude": 14.489963,
#         "longitude": 121.020762
#     },
#     "country": "Philippines",
#     "city": "Metro Manila",
#     "postcode": "1711",
#     "state": "NCR",
#     "name": "Chateau Elysee",
#     "address": "Doña Soledad Ave. Ext., Bicutan, Parañaque City, Metro Manila, NCR, 1711, Philippines",
#     "businessType": "residential",
#     "cityID": "4",
#     "countryID": "2",
#     "openingHours": "{}",
#     "score": 695.71564,
#     "debug": {
#         "d1": "details",
#         "rankings": {
#             "es_rank": 0,
#             "generic_rank": 0
#         },
#         "scores": {
#             "d": 0.9820137900379085,
#             "d2": 0,
#             "d2_raw": 0,
#             "d_raw": 0.9820137900379085,
#             "es_raw": 695.71564,
#             "es_score": 0,
#             "generic_score": 1.8045646103088009,
#             "h": 0.8373,
#             "h2": 0.009357486937559261,
#             "h2_raw": 0.6931471805599453,
#             "h_raw": 1,
#             "r": 0,
#             "r_raw": 0,
#             "s": -0.024106666666666665,
#             "s_raw": 0.5333333333333333
#         }
#     },
#     "Popularity": {
#         "pickupCount": 1573,
#         "dropoffCount": 1624
#     }
# }

countryCodes = ["id", "ph", "th", "vn", "sg", "my", "mm"]
countryNames = ["1--Indonesia","2--Philippines","3--Thailand","4--Vietnam","5--Singapore","6--Malaysia","7--Myanmar"]
wireOptions = {
    'proxy': {
        'http': 'http://172.17.0.2:8118',
        'https': 'http://172.17.0.2:8118',
        'no_proxy': 'localhost,127.0.0.1'
    }
}
selectedInformations = ['location', 'name', 'address']
query = 'nothing'
searchFilter = 'autocomplete'
resultNumber = 5

def interceptor_search(request, myFilter=searchFilter):
    if myFilter in request.url:
        print(f'{myFilter}-filter intercepted success: you are searching for the keyword {query}')
        params = request.params
        params['keyword'] = query
        params['limit'] = 100
        request.params = params

def printArray(arr):
	for i in arr:
		print(i, end = " \n")

def seleniumWireConfig():
	option = Options()
	prefs = {"profile.managed_default_content_settings.images": 2}
	option.add_experimental_option("prefs", prefs)
	# option.add_argument("--headless") # Runs Chrome in headless mode.
	# option.add_argument('--no-sandbox') # # Bypass OS security model
	# option.add_argument('start-maximized')
	# option.add_argument('disable-infobars')
	# option.add_argument("--disable-extensions")
	chrome = webdriver.Chrome(seleniumwire_options=wireOptions, options=option)
	chrome.request_interceptor = interceptor_search
	return chrome

def printOption(options, keys, lineNum):
	i = int(1)
	for place in options:
		if i > lineNum: break
		else: i = i + 1
		for key in keys:
			print(f"{key}: {place[key]}")

def seleniumStart(chrome, c, q):
	chrome.get(f'https://food.grab.com/{c}/en/')
	global query
	query = q
	# delay = 10 # seconds
	# try:
	# 	myElem = WebDriverWait(chrome, delay).until(EC.presence_of_element_located((By.ID, 'location-input')))
	# 	print("Page is ready!")
	# except TimeoutException:
	# 	print("Loading took too much time!")
	# chrome.wait_for_request('https://food.grab.com/favicon.ico').response
	queryRes = getData(chrome)
	chrome.close()
	global selectedInformations
	printOption(queryRes, selectedInformations, resultNumber)

def ScriptOptions():
	printArray(countryNames)
	c = -1
	q = 'Problemmm!'
	while (c == -1 or c <= 0):
		try:
			c = int(input('Please Select a country :'))
			if (c > 0):
				print(f'You selected {countryNames[c - 1]}')
				q = input("Please enter search keyword: ")
		except:
			print('Select a Number between 1 & 7 Please :')
			c = -1
	return [countryCodes[c - 1], q]

def getData(driver):
	search = driver.find_element(By.ID, 'location-input')
	search.send_keys('n')
	driver.wait_for_request('https://food.grab.com/v1/autocomplete').response
	for request in driver.requests:
		if 'autocomplete' in request.url:
			print(f'autocomplete listening starts to = {request.url}')
			body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
			body = body.decode('utf-8')
			body = json.loads(body)
			searchResult = body['places']
	return searchResult

if __name__ == '__main__':
	c = ScriptOptions()
	chrome = seleniumWireConfig()
	seleniumStart(chrome, c[0], c[1])