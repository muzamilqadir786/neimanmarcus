# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from neimanmarcus.items import NeimanmarcusItem
from scrapy.http import Request
import urlparse

import ipdb


class BergdorfSpider(scrapy.Spider):
	name = "bergdorf"
	allowed_domains = ["bergdorfgoodman.com"]
	start_urls = (
		'http://www.bergdorfgoodman.com/service/sitemap.jsp?icid=foot_site_map',
	)

	def parse(self, response):		
		hxs = Selector(response)		
		categories = hxs.xpath('//*[@id="contentbody"]/table[3]/tr[2]/td[2]/table/tr/td[2]/table/tr[2]/td')		
		for category_url in categories:
			category = category_url.xpath('./font/text()').extract()
			subcategory_urls = category_url.xpath('.//a[contains(@href,"c.cat")]')
			for subcategory_url in subcategory_urls:
				url = subcategory_url.xpath('./@href').extract()
				if url:								
					url = urlparse.urljoin(response.url,url[0])
					request = Request(url, self.pagination)					
					request.meta['category'] = category

					yield request

	def pagination(self, response):
		hxs = Selector(response)
		#pagination
		total_pages = hxs.xpath('normalize-space(//ul[@id="epagingTop"]/li[@class="pageOffset"][last()]/a/text())').extract()
		total_items = hxs.xpath('//span[@id="numItems"]/text()').extract()
		if total_items:
			pages = int(total_items[0]) / 120			
			catid = response.url.rsplit('/',2)[-2].split('_')[0]
			# ipdb.set_trace()
			for page_num in range(2, pages+1):			
				link = urlparse.urljoin(response.url,'#userConstrainedResults=true&refinements=&page={0}&pageSize=120&sort=PCS_SORT&definitionPath=/nm/commerce/pagedef_rwd/template/EndecaDrivenHome&onlineOnly=&allStoresInput=false&rwd=true&catalogId={1}&selectedRecentSize=&activeFavoriteSizesCount=0&activeInteraction=true'.format(page_num,catid))				
				request = Request(link,self.item_list,dont_filter=True)		
				request.meta['category'] = response.meta['category']
				yield request

	def item_list(self, response):		
		hxs = Selector(response)
		item_links = hxs.xpath('//ul[@class="category-items"]/li[@class="category-item"]/figure/div/a/@href').extract()
		item_links = [urlparse.urljoin(response.url,item_link) for item_link in item_links]
		item_links = filter(lambda item_link: urlparse.urlparse(item_link).netloc != '',item_links)
		
		gender = hxs.xpath('normalize-space(//a[@id="bchome"]/text())').extract()
		igender = 'Women'
		if gender and 'women' in gender[0].lower():
			igender = 'Women'

		
		subcategory = hxs.xpath('normalize-space(//a[@class="catalognavOpenItem active "]/text())').extract()
		# ipdb.set_trace()		
		for item_link in item_links:			
			request = Request(item_link,self.item_detail,dont_filter=True)
			request.meta['gender'] = igender
			request.meta['category'] = response.meta['category']
			# if category:
			# 	request.meta['category'] = category
			if subcategory:
				request.meta['subcategory'] = subcategory

			# ipdb.set_trace()
			
			yield request


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
					
					item['im_name'] = image_url.rsplit('/',1)[-1].replace('.jpg','')
					
					item['im_url'] = image_url

					
					item['product_url'] = response.url


					brand_name = hxs.xpath('(//a[@itemprop="brand"])[1]/text()').extract()
					if brand_name:
						item['brand_name'] = brand_name
					else:
						brand_name = hxs.xpath('normalize-space((//h1[@class="product-name elim-suites"])[1]/text())').extract()
						if brand_name:
							item['brand_name'] = brand_name


					product_name = hxs.xpath('(//a[@itemprop="brand"])[1]/following-sibling::span[1]/text()[normalize-space()]').extract()
					if product_name:
						item['product_name'] = ' '.join(product_name[0].split())
					else:
						product_name = hxs.xpath('normalize-space((//h1[@class="product-name elim-suites"])[1]/span/text())').extract()
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

					item['store'] = 'Bergdorf GoodMan' #Manually naming the store

					description = hxs.xpath('//div[@class="productCutline"]/h2/ul/li/text()').extract()
					if description:
						item['description'] = ' '.join(description)

					item['im_url_small'] = str(image_url).replace('z.jpg','n.jpg')

					item['im_url_md'] = str(image_url).replace('z.jpg','k.jpg')
					
					item['im_url_display'] = item['im_url_small'].rsplit('_',1)[0] + '_mn.jpg'
					
					# ipdb.set_trace()

					yield item
