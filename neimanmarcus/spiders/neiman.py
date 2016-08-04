# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse
from neimanmarcus.items import NeimanmarcusItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from scrapy.http import Request

import ipdb

CHOICES = (
	('SHOES','SHOES'),
	('HANDBAGS', 'HANDBAGS'),
	('BEAUTY', 'BEAUTY')
)

itemcategory = itemsubcategory = None

class NeimanSpider(scrapy.Spider):
	name = "neiman"
	allowed_domains = ["www.neimanmarcus.com"]
	start_urls = (
		# 'http://www.neimanmarcus.com/',		
	# 	'http://www.neimanmarcus.com/en-de/All-Shoes/cat47190746_cat13030734_cat000141/c.cat',
	# 	# 'http://www.neimanmarcus.com/en-de/All-Shoes/cat47190746_cat13030734_cat000141/c.cat#userConstrainedResults=true&refinements=&page=4&pageSize=120&sort=PCS_SORT&definitionPath=/nm/commerce/pagedef_rwd/template/EndecaDrivenHome&onlineOnly=&allStoresInput=false&rwd=true&catalogId=cat47190746&selectedRecentSize=&activeFavoriteSizesCount=0&activeInteraction=true',
	# 	# 'http://www.neimanmarcus.com/en-fr/Saint-Laurent-Chain-Wrapped-Tumbled-Leather-Boot-Black-All-Shoes/prod180470029_cat47190746__/p.prod',
		'http://www.neimanmarcus.com/service/sitemap.jsp',		
	)

	# rules = (
	# 	Rule(LinkExtractor(allow=(r'/All-Apparel/.*',)), callback='parse_item',follow=True),		
	# 	# Rule(LinkExtractor(allow=(r'/Handbags/All-Handbags/.*',)), callback='parse_item',follow=True),		

	# )

	# def parse_start_url(self, response):
	# 	list(self.item_detail(response))

	def parse(self, response):
		print response.url
		hxs = Selector(response)
		# categories = hxs.xpath('//*[@id="contentbody"]/table[3]/tr[2]//a[contains(@href,"c.cat")]')
		categories = hxs.xpath('//*[@id="contentbody"]/table[3]/tr[2]/td[2]/table/tr/td[2]/table/tr[2]/td')
		# categories = [urlparse.urljoin(response.url,category_url) for category_url in categories]
		for category_url in categories:
			# tds = category_url.xpath('./td')
			# for td in 
			category = category_url.xpath('./font/text()').extract()
			subcategory_urls = category_url.xpath('.//a[contains(@href,"c.cat")]')
			for subcategory_url in subcategory_urls:
				url = subcategory_url.xpath('./@href').extract()
				if url:			
					url = urlparse.urljoin(response.url,url[0])

					request = Request(url, self.item_list, dont_filter=True)
					# request.meta['category_name'] = category
					global itemcategory
					itemcategory = category

					subcategory_name = subcategory_url.xpath('./text()[normalize-space()]').extract()
					if subcategory_name:
						# request.meta['subcategory_name'] = ' '.join(subcategory_name[0].split())
						global itemsubcategory
						itemsubcategory = ' '.join(subcategory_name[0].split())						
					
					# ipdb.set_trace()
					yield request

	def item_list(self, response):
		hxs = Selector(response)
		item_links = hxs.xpath('//ul[@class="category-items"]/li[@class="category-item"]/figure/div/a/@href').extract()
		item_links = [urlparse.urljoin(response.url,item_link) for item_link in item_links]
		item_links = filter(lambda item_link: urlparse.urlparse(item_link).netloc != '',item_links)
		
		gender = hxs.xpath('normalize-space(//a[@id="bchome"]/text())').extract()
		igender = None
		if gender and 'women' in gender[0].lower():
			igender = 'Women'
			
		# ipdb.set_trace() 
		for item_link in item_links:			
			request = Request(item_link,self.item_detail)
			request.meta['gender'] = igender
			# if request.meta['category']:
			global itemcategory
			global itemsubcategory
			request.meta['category'] = ' '.join(itemcategory[0].split())			
			request.meta['subcategory'] = itemsubcategory

			
			yield request

		#pagination
		total_pages = hxs.xpath('normalize-space(//ul[@id="epagingTop"]/li[@class="pageOffset"][last()]/a/text())').extract()
		total_items = hxs.xpath('//span[@id="numItems"]/text()').extract()
		if total_items:
			pages = int(total_items[0]) / 120
		# ipdb.set_trace()
			catid = response.url.rsplit('/',2)[-2].split('_')[0]
			for page_num in range(2, pages+1):			
				link = urlparse.urljoin(response.url,'#userConstrainedResults=true&refinements=&page={0}&pageSize=120&sort=PCS_SORT&definitionPath=/nm/commerce/pagedef_rwd/template/EndecaDrivenHome&onlineOnly=&allStoresInput=false&rwd=true&catalogId={1}&selectedRecentSize=&activeFavoriteSizesCount=0&activeInteraction=true'.format(page_num,catid))
				yield Request(link,self.item_list)		


	def item_detail(self, response):
		# print response.url
		hxs = Selector(response)
		
		item = NeimanmarcusItem()
		
		import uuid
		item['product_id'] = str(uuid.uuid1()).split('-')[0]
		# image_urls = hxs.xpath('//div[@class="images"]//div[contains(@class,"img-wrap")]/img/@src').extract()
		#All image urls ending with z.jpg (Large images)
		image_urls = hxs.xpath('//img[@data-zoom-url]/@data-zoom-url').extract()
		image_urls = list(set(image_urls))		

		if image_urls:
			for image_url in image_urls:
				if str(image_url).endswith('z.jpg'):
					# item['image_urls'] = image_url
					item['im_name'] = image_url.rsplit('/',1)[-1].replace('.jpg','')
					
					item['im_url'] = image_url

					
					item['product_url'] = response.url


					brand_name = hxs.xpath('(//a[@itemprop="brand"])[1]/text()').extract()
					if brand_name:
						item['brand_name'] = brand_name
					else:
						brand_name = hxs.xpath('(//h1[@class="product-name elim-suites"])[1]/span[@class="prodDesignerName"]/text()').extract()
						if brand_name:
							item['brand_name'] = brand_name


					product_name = hxs.xpath('(//a[@itemprop="brand"])[1]/following-sibling::span[1]/text()[normalize-space()]').extract()
					if product_name:
						item['product_name'] = ' '.join(product_name[0].split())
					else:
						product_name = hxs.xpath('(//h1[@class="product-name elim-suites"])[1]/span[@class="prodDesignerName"]/following-sibling::span[1]/text()').extract()
						if product_name:
							item['product_name'] = 	product_name


					now_price = hxs.xpath('//span[text()="NOW:"]/following-sibling::span[1]/text()[normalize-space()]').extract()
					if now_price:						
						price = ' '.join(now_price[0].split()) #removing \t\n\r from string
					else:
						price = hxs.xpath('//p[@itemprop="price"]/text()[normalize-space()]').extract()
						if price:
							price = ' '.join(price[0].split()) #removing \t\n\r from string

					price = price.split()
					if len(price) >= 2:						
						item['currency'] = price[0]
						item['price'] = price[1]
					else:
						item['currency'] = 'USD'
						item['price'] = price[0].strip('$')

					item['category'] = response.meta['category']

					item['subcategory'] = response.meta['subcategory']

					item['gender'] = response.meta['gender']

					item['store'] = 'Neiman Marcus' #Manually naming the store

					description = hxs.xpath('//div[@class="productCutline"]/h2/ul/li/text()').extract()
					if description:
						item['description'] = ' '.join(description)

					item['im_url_small'] = str(image_url).replace('z.jpg','n.jpg')

					item['im_url_md'] = str(image_url).replace('z.jpg','k.jpg')
					
					item['im_url_display'] = str(image_urls[0]).replace('z.jpg','n.jpg')

					# ipdb.set_trace()

					# image_urls = hxs.xpath('//div[@id="prod-img"]/div/div[@class="slick-track"]/div/img/@src').extract()
					# image_urls = hxs.xpath('//div[@class="images"]//div[contains(@class,"img-wrap")]/img/@src').extract()
					# image_urls = hxs.xpath('//div[@class="images"]//div[contains(contains(@class,"img-wrap slick-slide")]/img/@src').extract()
					# image_urls = hxs.xpath('//div[@class="images"]//div[@class="slick-track"]/div/img/@src').extract()
					# print image_urls
					# if image_urls:
					# 	item['image_urls'] = image_urls

					# print item
					# print  item['price']
					yield item


# userConstrainedResults=true&refinements=&page=2&pageSize=120&sort=PCS_SORT&definitionPath=/nm/commerce/pagedef_rwd/template/EndecaDrivenHome&onlineOnly=&allStoresInput=false&rwd=true&catalogId=cat48490746&selectedRecentSize=&activeFavoriteSizesCount=0&activeInteraction=true