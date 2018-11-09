#-*- coding:utf-8 -*-
import requests
import sys
import json
import re
import time

url = 'https://www.ingress.com/intel'
req = requests.Session()

# 从本地文件中获取cookies并加入session和header中去
header_cookie = ''
with open('cookies.txt', 'r') as fp:
	intel_cookies = json.load(fp)
	for cookie in intel_cookies:
		req.cookies.set(cookie['name'],cookie['value'])
		header_cookie = header_cookie + cookie['name'] + '=' + cookie['value'] + ';'
# print header_cookie

# 从网页中获取version
content_test = req.get(url).content
version = re.findall(r'gen_dashboard_(\w*)\.js', content_test)[0]

# header和data
headers = {
	'accept':'*/*',
	'accept-encoding':'gzip, deflate, br',
	'accept-language':'en,zh;q=0.9,zh-CN;q=0.8,lb;q=0.7',
	'content-length':'93',
	'content-type':'application/json; charset=UTF-8',
	'origin':'www.ingress.com',
	'referer':'https://www.ingress.com/intel',
	'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
	}
headers['x-csrftoken'] = intel_cookies[1]['value']
headers['cookie'] = header_cookie

data = {'guid': "47297cb5f5db4a12a0b91284d8f13352.16"}
data['v'] = version

portal_guid_list = [
"b7fb26b8fb7f4dce9636fdaf270c41f1.16","ca09681350fb46509c59a8b7268a5ab3.16","782d999c7a0a40b0b9b26c96f008fc63.16","e0edda8657324463af887c61d08dac97.16","499dee356bab4b9dba1dfa6ae2fc6979.16","b61f808294844cf1b70d39989b263b32.16","3372f163343e4cfe99dbcad160033160.16","d69a9ae6733e4c9487808cde64564be9.16","a0a1a02678c44d26bac39bd7c97b1a10.16","ac6f5912651948038996f3e488dea71a.16","a4d46c8a78134dab90555d9ce9f9ee09.16","79f6625e971e4f848bd8bc4017c1f2f2.16","5b355df9569d42bda75a24bb53faae64.16","c6ac5bd1f7344d9fb02ae0ea180dcb4e.16","47297cb5f5db4a12a0b91284d8f13352.16"
]

res_power = (0, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 6000)
query_history = ()

# portal名字输出函数
def portal_name_output():
	f = open('post0910.txt', 'a')
	for portal_index in range(len(portal_guid_list)):
		# 获取portal信息
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://www.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		# 规定输出格式
		f.write('[')
		f.write('{:0>2d}'.format(portal_index + 1))
		f.write(']')
		f.write(portal_detail[8].encode('utf-8'))
		f.write(' ')
		f.write(portal_link(portal_detail[2], portal_detail[3]))
		f.write('\n')
	f.close
	return

# 电量查询函数
def portal_power_query():
	portal_power_list = []
	# 对列表里的portal进行循环
	for portal_index in range(len(portal_guid_list)):
		# 获取一个的portal信息
		data['guid'] = portal_guid_list[portal_index]
		post_content = req.post('https://www.ingress.com/r/getPortalDetails', data = json.dumps(data), headers = headers)
		portal_detail = post_content.json()['result']
		# 计算这个portal的电量总和
		portal_full_power = 0
		portal_decay_power = 0
		for res in portal_detail[15]:
			portal_decay_power += res[2]
			portal_full_power += res_power[res[1]]
		# 根据portal阵营输出power_percentage
		if(portal_detail[1] == "R"):
			power_percentage = round(float(portal_decay_power)/float(portal_full_power), 4)
		elif(portal_detail[1] == "N"):
			power_percentage = 0
		else:
			power_percentage = -round(float(portal_decay_power)/float(portal_full_power), 4)
		# 将每个portal的power_percentage列入电量列表
		portal_power_list.append(power_percentage)
		# 歇一歇再查询下一个portal
		time.sleep(2)
	# 信息储存
	global query_history
	query_history += (tuple(portal_power_list),)
	query_output()
	# 查询变化
	any_change()
	return 

# 无限循环查询电量	
def query_cycle():
	while(1):
		try:
			portal_power_query()
		except:
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print "Something went wrong, maybe network."
		time.sleep(1200)
	return

# 输出到txt
def query_output():
	f = open('post0910.txt', 'a')
	f.write(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
	f.write('\n')
	for portal_index in range(len(query_history[-1])):
		f.write('[')
		f.write('{:0>2d}'.format(portal_index + 1))
		f.write(']')
		if(query_history[-1][portal_index] > 0):
			f.write('R')
		elif(query_history[-1][portal_index] == 0):
			f.write('N')
		else:
			f.write('E')
		f.write('-')
		f.write('{:.2f}'.format(abs(query_history[-1][portal_index]) * 100))
		f.write('%')
		f.write(' ')
	f.write('\n')
	return
	
# 每次查询结束后，根据上次查询结果进行比对
def any_change():
	charged_list = []
	if(len(query_history) > 1):
		for portal_index in range(len(portal_guid_list)):
			if(abs(query_history[-1][portal_index]) > abs(query_history[-2][portal_index])):
				charged_list.append(str(portal_index + 1))	
		if(len(charged_list)):
			print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			print ', '.join(charged_list), "has been charged"
		# 这个地方应该写一个变化列表，把每次循环变化的情况归类（以后量大了再加进去，自动分析判断？）
	return	

# 根据经纬度生成portal的链接
def portal_link(lat, lon):
	latitude = '{:.6f}'.format(lat / 1000000.0)
	longitude = '{:.6f}'.format(lon / 1000000.0)
	return 'https://www.ingress.com/intel?ll=' + latitude + ',' + longitude + '&z=17&pll=' + latitude + ',' + longitude

# 根据guid列表输出portal名字和链接 	
portal_name_output()

# 开始查询	
query_cycle()