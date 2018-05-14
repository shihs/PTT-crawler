# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup



def get_pages(board, pages):
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


def get_posts(res):
	'''獲取該頁文章標題、推文數、作者id
	Args:
		res:get_pages function的requests
	'''
	soup = BeautifulSoup(res.text, "lxml")

	# 獲取文章標題、推文數、作者
	for post in soup.select(".r-ent"):
		push = post.select(".nrec")[0].text.encode("utf-8").strip()
		title = post.select(".title")[0].text.encode("utf-8").strip()
		author = post.select(".author")[0].text.encode("utf-8").strip()
		print push, title, author


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
		url = "https://www.ptt.cc/bbs/" + board + "/index" + str(previous - page + 1) + ".html"
		print url
		res = s.get(url)
		get_posts(res)





get_pages("movie", 1)
# get_pages("Gossiping", 5)





