# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup



def get_board(board, pages):
	'''爬取ptt各版文章推文數、標題、作者
	Args:
		borad:看板英文名稱
		pages:要爬取的頁數，包含最新頁總共的頁數

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


	# 每頁內容
	get_page(s, res, board, pages)


def get_posts(s, page_url):
	'''獲取該頁文章標題、推文數、作者id
	Args:
		s:get_pages function的Session
		page_url:每頁的網址
	'''
	res = s.get(page_url)
	soup = BeautifulSoup(res.text, "lxml")

	# 獲取文章標題、推文數、作者
	for post in soup.select(".r-ent")[:1]:
		# python 2
		# push = post.select(".nrec")[0].text.encode("utf-8").strip()
		# title = post.select(".title")[0].text.encode("utf-8").strip()
		# author = post.select(".author")[0].text.encode("utf-8").strip()
		
		# python 3
		push = post.select(".nrec")[0].text.strip() 
		title = post.select(".title")[0]
		post_url = title.select("a")[0]["href"]
		post_url = "https://www.ptt.cc" + post_url
		# print (post_url)
		title = title.text.strip()
		author = post.select(".author")[0].text.strip()
		print (push, title, author, post_url)
		get_post_content(s, post_url)




def get_page(s, res, board, pages):
	'''獲取每頁的url並抓每頁文章標題、推文數、作者
	Args:
		s:get_pages function的Session
		res:get_pages function的requests
		borad:看板英文名稱
		pages:要爬取的頁數，包含最新頁總共的頁數
	'''

	soup = BeautifulSoup(res.text, "lxml")
	previous = soup.select(".wide")[1]["href"]
	previous = int(previous[(previous.find("index")+5):previous.find(".html")])

	for page in range(pages):
		page_url = "https://www.ptt.cc/bbs/" + board + "/index" + str(previous - page + 1) + ".html"
		print (page_url)
		get_posts(s, page_url)




def get_post_content(s, post_url):
	'''獲取每篇文章內容，包含po文時間、作者ip、文章內容、推文內容


	'''
	res = s.get(post_url)
	soup = BeautifulSoup(res.text, "lxml")

	main_content = soup.select("#main-content")[0]
	# print (main_content)
	# 發文時間
	article_time = main_content.select(".article-metaline")[2].select(".article-meta-value")[0].text
	# print (article_time)
	
	# 發文ip
	ip = main_content.select(".f2")[0].text.replace("※ 發信站: 批踢踢實業坊(ptt.cc), 來自: ", "")
	# print (time, ip)

	# 發文內容
	str_main_content = str(main_content)
	start = str_main_content.find(str(article_time)) + len(article_time) + 13
	end = str_main_content.find('--')
	conten = str_main_content[start:end].strip()


	# 推/噓
	# push = main_content.select(".push")
	# push_info = list()
	# for p in push:
	# 	push_tag = p.select(".push-tag")[0].text
	# 	push_userid = p.select(".push-userid")[0].text
	# 	push_content = p.select(".push-content")[0].text
	# 	push_ipdatetime = p.select(".push-ipdatetime")[0].text.strip()
	# 	push_info.append([push_tag, push_userid, push_content, push_ipdatetime])
	# print (push_info)
		

	# print (main_content.select("#text"))


	








# get_board("movie", 1)
get_board("Gossiping", 1)





