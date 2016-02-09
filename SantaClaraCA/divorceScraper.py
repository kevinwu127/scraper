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

#Superior Court of California, County of Santa Clara
url = 'https://cmportal.scscourt.org/Portal'
status = "Active"
date_start = date(2010, 3, 18)
date_end = date(2010, 6, 1)
file_name = "SantaClaraCounty" + status + date_start.strftime("%Y_%m_%d") + "-" + date_end.strftime("%Y_%m_%d")

with open(file_name + '.csv', 'w') as csvfile:
	fieldnames = ['case_number', 'case_type', 'case_status', 'court', 'file_date', 'case_filer_name', 'case_filer_info', 'petitioner_info', 'respondent_info']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	writer.writeheader()

# try:
# 	driver = webdriver.Firefox()
# 	driver.get(url)


# 	#Setting for driver to wait at least 60 seconds when looking at DOM
# 	driver.implicitly_wait(20)
# except:
# 	driver.close();
	# print 'Error found during the process.'

for single_date in daterange(date_start, date_end):
	current_date = single_date.strftime("%m/%d/%Y")

	try:
		driver = webdriver.Firefox()
		driver.get(url)


		#Setting for driver to wait at least 60 seconds when looking at DOM
		driver.implicitly_wait(10)

		#Input * into SearchCriteria
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[3]/p/input').clear()
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[3]/p/input').send_keys('*')

		driver.implicitly_wait(1)
		try:
			#Click arrow on advanced search options
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/p[2]/a').click()
		except:
			print ''
		

		#Click plus on search cases
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/header/a').click()
		try:
			#Click arrow and then All Case Types for Case Type
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[1]/div[2]/span/span/input').clear()
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[1]/div[2]/span/span/input').send_keys('All Case Type')
		except:
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/header/a').click()
			#Click arrow and then All Case Types for Case Type
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[1]/div[2]/span/span/input').clear()
			driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[1]/div[2]/span/span/input').send_keys('All Case Type')


		driver.implicitly_wait(10)

		#Click arrow and then Closed for Case Status
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[2]/div[2]/span/span/input').clear()
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[2]/div[2]/span/span/input').send_keys(status)

		#Click FROM and clear field
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[3]/div[2]/input').clear()


		#fill out From
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[3]/div[2]/input').send_keys(current_date)

		#Click TO and clear field
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[3]/div[3]/input').clear()

		#fill out To
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[6]/div[3]/section[2]/div/div[3]/div[3]/input').send_keys(current_date)

		#Click SUBMIT
		driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[1]/div/div/div[2]/form/div[7]/input').click()

		count = 0;

		k = 0;

		driver.implicitly_wait(3)

		if status == "Active":
			try:
				#if there is a warning
				num_ppl = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/span[2]')
			except:
				num_ppl = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/span[2]')

		else:
			#extract number from bottom of page
			num_ppl = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/span[2]')

		driver.implicitly_wait(10)
			

		num_ppl = [int(s) for s in num_ppl.text.split() if s.isdigit()]
		num_ppl = max(num_ppl)

		while True:
			for i in range(1, 11):

					#Click back to search results
					driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/nav/ul/li[2]/a').click()

					if status == "Active":
						driver.implicitly_wait(0.3)
						try:
							#if theres a red row
							driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
						except:
							driver.implicitly_wait(10)
							driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
						driver.implicitly_wait(10)
					else:
						#Click each name
						driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
					
					try:
						#extract number from bottom of page
						num_cases = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div[3]/section/div/div/div/div/span[2]')
					except NoSuchElementException:
						print "*******TOOK TOO LONG TO LOAD**********"
						#Click back to search results
						driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/nav/ul/li[2]/a').click()
						k = k + 1
						continue

					num = [int(s) for s in num_cases.text.split() if s.isdigit()]
					max_num = max(num)
					if max_num > 10:
						max_num = 10

					#extract case filer name (MAY BE LAWYER IF DIFFERENT FROM PETITIONER NAME)
					case_filer_name = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/h3')
					case_filer_name = case_filer_name.text

					#extract case filer personal information
					case_filer_info = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div[1]/section/div/div/div[1]')
					case_filer_info = case_filer_info.text.replace('Address', 'Address:').replace('\n', ' ').replace('\r', '').replace('   ', ' ').rstrip()

					for j in range(1, max_num + 1):
						#Find the case type
						case_type = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div[3]/section/div/div/div/table/tbody/tr[' + str(j) + ']/td[3]')

						count = count + 1

						#Compare case type
						if str(case_type.text) == "Dissolution w/ Minor" or str(case_type.text) == "Dissolution w/o Minor Children" or str(case_type.text) == "Legal Separation w/o Minor Children" or str(case_type.text) == "Legal Separation w/ Minor" or str(case_type.text) == "Dissolution w/ Minor Children" or str(case_type.text) == "Legal Separation w/ Minor Children":
							case_type = case_type.text
							#print case_type
							#Click case number
						 	driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/div[1]/div[3]/section/div/div/div/table/tbody/tr[' + str(j) + ']/td[1]/a').click()
							
						 	driver.implicitly_wait(60)

							#Save case number
						 	case_num = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[1]/div/div/p[1]')
						 	case_num = case_num.text.split()
						 	case_num.remove('Case')
						 	case_num.remove('Number:')
						 	case_num = " ".join(case_num)
						 	#print case_num

						 	driver.implicitly_wait(10)

						 	#Save case status
						 	case_status = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[1]/div/div/p[5]')
						 	case_status = case_status.text.split()
						 	case_status.remove('Case')
						 	case_status.remove('Status:')
						 	case_status = " ".join(case_status)
						 	#print case_status

						 	#Save court
						 	court = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[1]/div/div/p[2]')
						 	court = court.text.split()
						 	court.remove('Court:')
						 	court = " ".join(court)
						 	#print court

						 	#Save file date
						 	file_date = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[1]/div/div/p[3]')
						 	file_date = file_date.text.split()
						 	file_date.remove('File')
						 	file_date.remove('Date:')
						 	file_date = " ".join(file_date)
						 	#print file_date

						 	#Save petitioner information
						 	pet_info = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[2]/div/div[2]/div[2]')
						 	pet_info = pet_info.text.replace('\n', ' ').replace('\r', '').rstrip()
						 	#print pet_info

							#Get respondent information
							resp_info = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[3]/div/form/section[2]/div/div[1]/div[1]')
							resp_info = resp_info.text.replace('\n', ' ').replace('\r', '').rstrip()
							#print resp_info

							with open(file_name + '.csv', 'a') as csvfile:
								fieldnames = ['case_number', 'case_type', 'case_status', 'court', 'file_date', 'case_filer_name', 'case_filer_info', 'petitioner_info', 'respondent_info']
								writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
								writer.writerow({'case_number' : case_num, 
												 'case_type' : case_type,
												 'case_status' : case_status,
												 'court' : court,
												 'file_date' : file_date,
												 'case_filer_name' : case_filer_name,
												 'case_filer_info' : case_filer_info,
												 'petitioner_info' : pet_info,
												 'respondent_info' : resp_info})
							
							#Click back to person info
							driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/nav/ul/li[2]/a').click()
							if status == "Active":
								driver.implicitly_wait(0.3)
								try:
									#if theres a red row
									driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
								except:
									driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
							else:
								#Click each name
								driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/table/tbody/tr[' + str(i) + ']/td[2]/a').click()
							driver.implicitly_wait(10)

						else:
							print case_type.text
					#Click back to search results
					driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/nav/ul/li[2]/a').click()

					#increment person counter
					k = k + 1

					#check against max_ppl
					if k == num_ppl:
						break

			if k == num_ppl:
				break
				
			if status == "Active":
				driver.implicitly_wait(1)
				try:
					driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[2]/div/div/a[3]/span').click()
				except:
					driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/a[3]/span').click()
				driver.implicitly_wait(10)
			else:
				#Click forward arrow
				driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/div/div/div[1]/div/div/a[3]/span').click()

		#write to file

		driver.close()

	except NoSuchElementException:
		print 'No elements found for: ' + current_date
		driver.close()
		# driver.close();
		# print 'Error found during the process.'





	