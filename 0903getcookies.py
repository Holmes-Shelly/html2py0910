import time
import requests
from selenium import webdriver
import sys
from bs4 import BeautifulSoup
import json

url = 'https://www.ingress.com/intel'
driver = webdriver.Chrome()
driver.get(url)

time.sleep(50)
cookies = driver.get_cookies()

new_cookies = []
for cookie in cookies:
	if ((cookie['name'] == "SACSID") or (cookie['name'] == "csrftoken")):
		new_cookies.append(cookie)
print new_cookies
	
with open('cookies.txt', 'w') as fp:
    json.dump(new_cookies, fp)
print 'cookies documented'

req = requests.Session()
with open('cookies.txt', 'r') as fp:
	cookies = json.load(fp)
	for cookie in cookies:
		req.cookies.set(cookie['name'],cookie['value'])

content_test = req.get(url).content
bs1 = BeautifulSoup(content_test, 'html.parser')
csrf = bs1.find(type = 'hidden').get('value').encode('ascii')
print csrf
