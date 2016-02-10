import requests 
from bs4 import BeautifulSoup
import re
import time
import cookielib
import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import timedelta, date

def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def cleanse(string):
	return string.replace('\n', ' ').replace('\r', '').rstrip()

class Scraper:
	def __init__(self, url, status, date_start, date_end, county):
		self.url = url
		self.status = status
		self.file_name = county + status + date_start.strftime("%Y_%m_%d") + "-" + date_end.strftime("%Y_%m_%d")

	def create_csv(self, fieldnames):
		with open(self.file_name + '.csv', 'w') as csvfile:
			self.fieldnames = fieldnames
			self.writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			self.writer.writeheader()

	def init_firefox(self, wait_time):
		self.wait_time = wait_time
		self.driver = webdriver.Firefox()
		self.driver.implicitly_wait(wait_time)
		self.driver.get(self.url)

	def init_phantom(self, wait_time):
		self.wait_time = wait_time
		self.driver = webdriver.PhantomJS()
		self.driver.set_window_size(1024, 768)
		self.driver.implicitly_wait(wait_time)
		self.driver.get(self.url)

	def set_timer(self, wait_time):
		self.driver.implicitly_wait(wait_time)

	def screenshot(self):
		self.driver.save_screenshot('screen.png')

	def navigate(self, xpaths):
		for xpath in xpaths:
			self.driver.find_element_by_xpath(xpath).click()

	def formatted_date(self, date, format):
		if format == 'slash':
			return date.strftime('%m/%d/%Y')

	def set_date_interval(self, start, end):
		self.date_start = start
		self.date_end = end

	def search(self, xpaths):
		#start date
		self.driver.find_element_by_xpath(xpaths[0]).clear()
		self.driver.find_element_by_xpath(xpaths[0]).send_keys(self.formatted_date(self.date_start, 'slash'))

		#end date
		self.driver.find_element_by_xpath(xpaths[1]).clear()
		self.driver.find_element_by_xpath(xpaths[1]).send_keys(self.formatted_date(self.date_end, 'slash'))

		#submit
		self.driver.find_element_by_xpath(xpaths[2]).click()

	def acquire_field_text(self, xpath):
		return self.driver.find_element_by_xpath(xpath).text

	def write_row(self, case_number, case_type, case_status, court, file_date, judicial_officer, petitioner, petitioner_address, petitioner_attorney, respondent, respondent_address, respondent_attorney):
		with open(self.file_name + '.csv', 'a') as csvfile:
			self.writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
			self.writer.writerow({'case_number' : case_number, 
							      'case_type' : case_type,
							      'case_status' : case_status,
							 	  'court' : court,
							 	  'file_date' : file_date,
							 	  'judicial_officer' : judicial_officer,
							 	  'petitioner' : petitioner,
							 	  'petitioner_address' : petitioner_address,
							 	  'petitioner_attorney' : petitioner_attorney,
							 	  'respondent' : respondent,
							 	  'respondent_address' : respondent_address,
							 	  'respondent_attorney': respondent_attorney})


def main():
	#Superior Court of Florida, County of Pinellas
	url = 'https://ccmspa.pinellascounty.org/PublicAccess/default.aspx'
	status = "Open"
	date_start = date(2014, 1, 1)
	date_end = date(2014, 12, 31)
	interval = 7
	county = "PinellasFL"

	#initialize Scraper class
	scraper = Scraper(url, status, date_start, date_end, county)

	#create initial csv with fieldnames
	fieldnames = ['case_number', 'case_type', 'case_status', 'court', 'file_date', 'judicial_officer', 'petitioner','petitioner_address', 'petitioner_attorney', 'respondent','respondent_address', 'respondent_attorney']
	scraper.create_csv(fieldnames)

	#initialize browser window (either firefox or phantomjs)
	wait_time = 30
	#scraper.init_firefox(wait_time)
	scraper.init_phantom(wait_time)

	#navigate to search page
	scraper.driver.find_element_by_xpath('/html/body/table/tbody/tr[2]/td/table/tbody/tr[1]/td[2]/a[3]').click()

	current_date = date_start

	while current_date < date_end:

		if current_date + timedelta(days=interval) >= date_end:
			next_date = date_end
		else:
			next_date = current_date + timedelta(days=interval)

		scraper.set_date_interval(current_date, next_date)


		#navigate to the search page and click on anything needed
		if (status == "Open"):
			xpaths = ['//*[@id="DateFiled"]', '//*[@id="OpenOption"]', '/html/body/form/table[4]/tbody/tr/td/table/tbody/tr[11]/td[2]/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[2]/select/option[7]']
		elif (status == "Closed"):
			xpaths = ['//*[@id="DateFiled"]', '//*[@id="ClosedOption"]', '/html/body/form/table[4]/tbody/tr/td/table/tbody/tr[11]/td[2]/table/tbody/tr/td/div/table/tbody/tr/td/table/tbody/tr/td[2]/select/option[7]']
		scraper.navigate(xpaths)

		#fill out form and search
		xpaths = ['//*[@id="DateFiledOnAfter"]', '//*[@id="DateFiledOnBefore"]', '//*[@id="SearchSubmit"]']
		scraper.search(xpaths)

		print "Date Range: " + scraper.formatted_date(scraper.date_start, 'slash') + ' - ' + scraper.formatted_date(scraper.date_end, 'slash')

		#get total number of records
		record_count = int(scraper.acquire_field_text('/html/body/table[3]/tbody/tr[1]/td[2]/b'))
		print "Total records: " + str(record_count)

		count = 0

		while count < record_count:

			xpath = '/html/body/table[4]/tbody/tr[' + str(count + 3) + ']/td[1]/a'
			case_num = scraper.acquire_field_text(xpath)
			scraper.driver.find_element_by_xpath(xpath).click()

			field_xpath = '/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[1]/td/b'
			case_type = scraper.acquire_field_text(field_xpath)

			field_xpath = '/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[2]/td/b'
			date_filed = scraper.acquire_field_text(field_xpath)

			field_xpath = '/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[3]/td/b'
			location = scraper.acquire_field_text(field_xpath)

			field_xpath = '/html/body/table[3]/tbody/tr/td[3]/table/tbody/tr/td/table/tbody/tr[4]/td/b'
			judicial_officer = scraper.acquire_field_text(field_xpath)

			scraper.set_timer(0.3)
			try:
				try:
					field_xpath = '//*[@id="PIr11"]'
					petitioner = scraper.acquire_field_text(field_xpath)
				except:
					field_xpath = '//*[@id="PIr12"]'
					petitioner = scraper.acquire_field_text(field_xpath)

				try:
					field_xpath = '/html/body/table[4]/tbody/tr[3]/td'
					p_address = cleanse(scraper.acquire_field_text(field_xpath))
				except:
					try:
						field_xpath = '/html/body/table[5]/tbody/tr[3]/td'
						p_address = cleanse(scraper.acquire_field_text(field_xpath))
					except:
						print "CHECK RESPONDENT ADDRESS FOR " + case_num

				try:
					field_xpath = '//*[@id="PIr12"]'
					respondent = scraper.acquire_field_text(field_xpath)
				except:
					field_xpath = '//*[@id="PIr13"]'
					respondent = scraper.acquire_field_text(field_xpath)

				try:
					field_xpath = '/html/body/table[4]/tbody/tr[6]/td'
					r_address = cleanse(scraper.acquire_field_text(field_xpath))
				except:
					try:
						field_xpath = '/html/body/table[5]/tbody/tr[6]/td'
						r_address = cleanse(scraper.acquire_field_text(field_xpath))
					except:
						print "CHECK RESPONDENT ADDRESS FOR " + case_num

				try:
					field_xpath = '/html/body/table[4]/tbody/tr[2]/td[3]'
					petitioner_attorney = cleanse(scraper.acquire_field_text(field_xpath))

					field_xpath = '/html/body/table[4]/tbody/tr[5]/td[3]'
					respondent_attorney = cleanse(scraper.acquire_field_text(field_xpath))
				except:
					field_xpath = '/html/body/table[5]/tbody/tr[2]/td[3]'
					petitioner_attorney = cleanse(scraper.acquire_field_text(field_xpath))

					field_xpath = '/html/body/table[5]/tbody/tr[5]/td[3]'
					respondent_attorney = cleanse(scraper.acquire_field_text(field_xpath))
			except:
				print "Entry " + case_num + " missing critical information. Discarded."

			scraper.set_timer(30)

			print "Writing " + case_num
			scraper.write_row(case_num, case_type, status, location, date_filed, judicial_officer, petitioner, p_address, petitioner_attorney, respondent, r_address, respondent_attorney)

			count += 1
			scraper.driver.back()

		print "Saved " + str(count) + " records"

		#go back to the search form
		scraper.driver.find_element_by_xpath('/html/body/table[2]/tbody/tr/td/table/tbody/tr/td[1]/font/a[5]').click()

		current_date = next_date + timedelta(days=1)

if __name__ == "__main__":
	main()
