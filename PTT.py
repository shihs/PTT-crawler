# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import json


def get_requests(board):
	'''送出requests Sesstion 通過十八歲確認
	Args:
		borad:看板英文名稱
	Return:
		s:requests Session
		res:get 結果
	'''
	s = requests.Session()
	# 看板
	url = "https://www.ptt.cc/bbs/" + board + "/index.html"
	res = s.get(url)
	soup = BeautifulSoup(res.text, "lxml")

	# 檢查是否需要滿十八歲確認
	if len(soup.select(".over18-notice")) != 0:
		over18_url = "https://www.ptt.cc/ask/over18"
		payload = {
			"from": "/bbs/" + board + "/index.html",
			"yes": "yes"
		}

		s.post(over18_url, data = payload, verify = False)
		res = s.get(url, verify = False)

	# 回傳 requests Session 和 s.get 結果
	return (s, res)


def get_posts_info(s, page_url):
	'''獲取該頁文章標題、推文數、po文id、文章網址
	Args:
		s:get_pages function的Session
		page_url:每頁的網址
	Return:
		posts_info:List，文章標題、推文數、po文id、文章網址
	'''
	res = s.get(page_url)
	if  res.status_code == 500:
		print ("oops! 500")
		return("stop!")
	soup = BeautifulSoup(res.text, "lxml")
	
	# return list
	posts_info = []

	# 獲取文章標題、推文數、po文id、文章網址
	for post in soup.select(".r-ent"):
		
		push = post.select(".nrec")[0].text.strip() # 推文數

		try:
			title = post.select(".title")[0]
			# 文章網址
			post_url = title.select("a")[0]["href"] 
			post_url = "https://www.ptt.cc" + post_url
			
			title = title.text.strip() # 文章標題
			# 略過公告文章
			if "[公告]" in title:
				continue

			author = post.select(".author")[0].text.strip() # po文id

			# 將每篇文章簡單資訊儲存到 posts_info_all
			posts_info.append([push, title, author, post_url, page_url])

		except:
			continue

	return (posts_info)




# def get_page(s, res, board, pages):
def get_page(s, res, board, index):
	'''獲取每頁的url並抓每頁文章標題、推文數、po文id、文章網址
	Args:
		s:get_pages function的Session
		res:get_pages function的requests
		borad:看板英文名稱
		pages:要爬取的頁數，包含最新頁總共的頁數
	Return:
		posts_info_all:List, 多頁的文章標題、推文數、po文id、文章網址
	'''

	soup = BeautifulSoup(res.text, "lxml")
	previous = soup.select(".wide")[1]["href"]
	previous = int(previous[(previous.find("index")+5):previous.find(".html")])

	posts_info_all = []

	# 爬取看板每頁文章簡單資訊
	# for page in range(pages):
	while True:
		# 該頁網址
		# page_url = "https://www.ptt.cc/bbs/" + board + "/index" + str(previous - page + 1) + ".html"
		page_url = "https://www.ptt.cc/bbs/" + board + "/index" + str(index) + ".html"
		print (page_url)
		# 獲取該頁各文章 推文數、標題、作者、網址
		posts_info = get_posts_info(s, page_url)

		if posts_info == "stop!":
			print ("im stoping here")
			return(posts_info_all)

		# 將每篇文章簡單資訊儲存到 posts_info_all
		posts_info_all.extend(posts_info)
		index = index + 1

	# return (posts_info_all)


def get_post_content(s, post_url):
	'''獲取每篇文章詳細資訊，包含po文時間、作者ip、文章內容、推文內容
	Args:
		s:get_pages function的Session
		post_url:the url of a post
	'''
	print (post_url)
	res = s.get(post_url)
	soup = BeautifulSoup(res.text, "lxml")
	main_content = soup.select("#main-content")[0]
	# print (main_content)
	str_main_content = str(main_content)

	# 發文時間
	article_time = main_content.select(".article-metaline")[2].select(".article-meta-value")[0].text
	# print (article_time)
	
	# 發文ip
	ips = main_content.select(".f2")[:3]
	ip = ""
	for i in ips:
		if "發信站" in str(i):
			ip = i.text.replace("※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ", "").strip()

			if ip == "※ 發信站: 批踢踢實業坊(ptt.cc)":
				start = str_main_content.find("◆ From: ") + 8
				end = str_main_content.find('\n', start)
				ip = str_main_content[start:end]
			break

	# 發文內容
	start = str_main_content.find(str(article_time)) + len(article_time) + 13
	end = str_main_content.find('--', start)
	# end = str_main_content.rfind('--') # 找到最後的 "--"，文章內文結束處
	content = str_main_content[start:end].strip()
	content = BeautifulSoup(content, "lxml").text#.replace("\n", "  ")
	# print (content)

	# 推/噓
	# push = main_content.select(".push")
	end = str_main_content.rfind('--') # 找到最後的 "--"，文章內文結束處
	push = str_main_content[end:]
	push = BeautifulSoup(push, "lxml").select(".push")
	# print (push)

	push_info = list()
	for p in push:
		# print (p.text)
		try:
			push_tag = p.select(".push-tag")[0].text[:-1]
		except:
			continue
		push_userid = p.select(".push-userid")[0].text
		push_content = p.select(".push-content")[0].text[1:].strip()
		push_ipdatetime = p.select(".push-ipdatetime")[0].text.strip().split()
		
		try:
			push_ip = push_ipdatetime[0]
			push_date = push_ipdatetime[1]
			push_time = push_ipdatetime[2]
		except:
			push_ip = ""
			push_date = ""
			push_time = ""
			for j in push_ipdatetime:
				if "." in j:
					push_ip = j
				if "/" in j:
					push_date = j
				if ":" in j:
					push_time = j

		push_info.append([push_tag, push_userid, push_content, push_ip, push_date, push_time])
	
	return(article_time, ip, content, push_info)


# def run(board, pages):
def run(board, index):
	# 獲取各版po文詳細資訊（包含po文者id、po文內容與時間等等）
	'''Args:
		board:看板名稱
		pages:要爬取的頁數
	'''

	# 網站session
	s, res = get_requests(board)

	# 文章簡單資訊
	# posts_info_all = get_page(s, res, board, pages)
	posts_info_all = get_page(s, res, board, index)
	n = len(posts_info_all)

	all_info = {}

	for i in range(n):
		post = posts_info_all[i]
		push = post[0]
		title = post[1]
		author = post[2]
		post_url = post[3]
		page_url = post[4]

		# 文章詳細資訊
		article_time, ip, content, push_info = get_post_content(s, post_url)

		# 整理成 dictionary 格式
		all_info[post_url] = {
			"id":i+1,
			"title":title,
			"author":author,
			"ip":ip,
			"article_time":article_time,
			"content":content,
			"push_info":{
				"push_number":push,
				"push":push_info
			},
			# "post_url":post_url,
			"page_url":page_url

		}

		if (i+1)%1000 == 0:
			with open(board +  + ".json", "w") as f:
				json.dump(all_info, f)
			all_info = {}

	if all_info != {}:
		with open("test.json", "w") as f:
			json.dump(all_info, f)

	print ("done!")
	# return (all_info)







all_info = run("Gossiping", 39440)
# print (all_info)



