import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException        
import requests
import json

import pandas as pd
import numpy as np

URL = "https://yocket.in/profiles/find/matching-admits-and-rejects"
DRIVER_PATH = r"C:\Users\Cosmos\Documents\Jayen\Pre MS\Big Game\Yocket Analysis\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(DRIVER_PATH)
HOME = r'C:\Users\Cosmos\Documents\Jayen\Pre MS\Big Game\Yocket Analysis'

# raw_data = pd.DataFrame(columns = ['student_name','gre','ielts_toefl','work_exp','papers','ug_college_name_location','ug_degree','ug_pct_cgpa',
									# 'ms_college_name','ms_college_course','ms_college_decision_status'])

def openyocket(URL,credentials):
    driver.get(URL)
    time.sleep(1)
    driver.find_element_by_name('email').send_keys(credentials['username'])
    time.sleep(1)
    driver.find_element_by_name('password').send_keys(credentials['password'])

def search_universities():
    cha = ["University of waterloo"]
    course = ["computer"]
    for i in cha[0]:
        driver.find_element_by_id("users-view-search-universities").send_keys(i)
    time.sleep(2)
    driver.find_element_by_id("users-view-search-universities").send_keys(Keys.ARROW_DOWN,Keys.ENTER)
    time.sleep(2)
    driver.find_element_by_id("users-view-search-courses").send_keys(Keys.CONTROL,'a')
    time.sleep(2)
    driver.find_element_by_id("users-view-search-courses").send_keys("computer")
    time.sleep(2)
    first_option = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "users-view-search-courses")))
    print(first_option.text)
    driver.find_element_by_id("users-view-search-courses").send_keys(Keys.ARROW_DOWN,Keys.ENTER)
    time.sleep(2)
    driver.find_element_by_id("find-admits-rejects-button").click()

def shallow_data():
	#to get the name, college, course and intake 
	name_college_course_intake = driver.find_elements_by_class_name("col-sm-8")
	#this captures info reg admit, reject 
	decision = driver.find_elements_by_class_name("col-sm-3.text-uppercase")
	#profile of candidate like gre, work exp,etc
	profile = driver.find_elements_by_class_name("row.text-center")
	#Name of person
	print(name_college_course_intake[0].find_element_by_tag_name("a").text)
	#Course and intake
	print(name_college_course_intake[0].find_element_by_tag_name("small").text.split("\n"))
	#Decision
	print(decision[0].find_element_by_tag_name('label').text)
	#Profile
	print(profile[0].find_elements_by_class_name("col-sm-3.col-xs-6")[0].text.split("\n"))
	print(profile[0].find_elements_by_class_name("col-sm-3.col-xs-6")[1].text.split("\n"))
	print(profile[0].find_elements_by_class_name("col-sm-3.col-xs-6")[2].text.split("\n"))
	print(profile[0].find_elements_by_class_name("col-sm-3.col-xs-6")[3].text.split("\n"))
	# print(profile[0].find_elements_by_class_name("col-sm-3.col-xs-6")[0].find_element_by_tag_name('strong').text)

def data_parser(raw_data, page_no, student_name, gre_gmat, toefl_ielts, work_exp, papers, ug_info, *args_ms_colleges):

	Page_no = page_no
	permit_missing_undergrad_info = False
	
	if gre_gmat[1]!="None" and len(gre_gmat)!=3:
		gre_scores = gre_gmat[1:]
		# print(gre_scores)
	else:
		gre_scores = np.nan
		# print("not appeared")
	
	if toefl_ielts[0].lower()!="eng test":

		eng_test = toefl_ielts
		# print("yes",toefl_ielts)
	else:
		eng_test = np.nan
		# print("Not Available")
	
	work_exp = work_exp[1].lower()
	papers = papers[1].lower()
	if len(ug_info)==5:
		permit_missing_undergrad_info = True
	assert len(ug_info)==6 or permit_missing_undergrad_info,"Failed to handle ug college info, wrong assumption on generic pattern:"+str(ug_info)

	ug_college_name_location = ug_info[4].lower()
	ug_college_degree = ug_info[3].lower()
	ug_grades = ug_info[1:3]

	for ms_colleges in args_ms_colleges:

		ms_college_name = ms_colleges[0].lower()
		ms_college_course = ms_colleges[1].lower()
		ms_colleges_decision = ms_colleges[-1].lower() 
		if len(ms_colleges)==3 or (len(ms_colleges)==6 and ms_colleges_decision=="interested"):
			ms_colleges_app_date = np.nan
			ms_colleges_des_date = np.nan
		elif len(ms_colleges)==4 or (len(ms_colleges) == 7 and (ms_colleges_decision=="applied" or ms_colleges_decision=="reject")):
			ms_colleges_app_date = ms_colleges[2][9:]
			ms_colleges_des_date = np.nan
		elif len(ms_colleges) == 5 or len(ms_colleges) == 8:
			ms_colleges_app_date = ms_colleges[2][9:]
			ms_colleges_des_date = ms_colleges[3][10:]
		else:
			print("~~~~~~~~~~",ms_colleges,"~~~~~~~~~~~~")
			raise Exception("Did not acoount for this particular case of ms college format")

		row = [Page_no, student_name, gre_gmat, toefl_ielts, work_exp,papers, ug_college_name_location, ug_college_degree, ug_grades, ms_college_name,
				ms_college_course, ms_colleges_decision, ms_colleges_app_date, ms_colleges_des_date]
		
		entry = dict(zip(raw_data.columns,row))
		raw_data = raw_data.append(entry,ignore_index=True)
	return raw_data
	

def check_exists_by_xpath(xpath):
    try:
        if driver.find_elements_by_xpath(xpath)[-1].find_element_by_tag_name('i').get_attribute("class") == "fa fa-chevron-right":
        	# print(driver.find_elements_by_xpath(xpath)[-1].find_element_by_tag_name('i').get_attribute("class"))
        	return True
        else: 
        	return False
    except NoSuchElementException:
        return False
    return True


def deep_scrape(raw_data):

	if raw_data.empty:
		# If csv is empty then start from page 1
		page_no=1	
	else:
		# Fetch url of last visited page (acts as a checkpoint) 
		page_no=raw_data['Page_no'].iloc[-1]
		driver.get("https://yocket.in/profiles/find/matching-admits-and-rejects?page="+str(page_no+1))
		page_no+=1

	name_college_course_intake = driver.find_elements_by_class_name("col-sm-8")
	buffer_df = pd.DataFrame(columns = ['Page_no','Student_name','gre','ielts_toefl','work_exp','papers','ug_college_name_location','ug_degree','ug_pct_cgpa',
									    'ms_college_name','ms_college_course','ms_college_decision_status'])
	
	while True:	
		print(page_no)
		for idx,_ in enumerate(name_college_course_intake):
			gre_engtest_wrkexp_papers = []
			ms_colleges = []
			if driver.find_element_by_class_name("col-sm-8").text == "Oops!! Page Not Found!!":
				print("Profile not found or captcha prompted!")
				driver.back()
				continue
			student_name = driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").text
			# print("Student Name:",driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").text)
			if (student_name in raw_data['Student_name'].tolist()) or student_name == "alert(1);d":
				print('Visited_node')
				continue
			university_name = driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("small").text.split('\n')
			driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").send_keys("\n")
			try: 
				if "Oops!! Page Not Found!!" in driver.find_element_by_class_name("col-sm-8").find_element_by_tag_name('h2').text:
					driver.back()
					continue 
			except:
				pass
			
			candidate_profile = driver.find_elements_by_class_name("row.text-center")
			for i in range(4):
				# print(":::",candidate_profile[0].find_elements_by_tag_name("div")[i].text.split("\n"))
				gre_engtest_wrkexp_papers.append(candidate_profile[0].find_elements_by_tag_name("div")[i].text.split("\n"))
			# print(gre_engtest_wrkexp_papers)
			candidate_education_back = driver.find_element_by_class_name("col-sm-12.card").find_elements_by_tag_name("div")
			# print("Education:",candidate_education_back[0].text.split("\n"))
			ug_info = candidate_education_back[0].text.split("\n")
			try:
				driver.find_element_by_class_name("btn-link").send_keys("\n")
			except:
				pass
			college_name = driver.find_element_by_class_name("table")
			for applied_id,_ in enumerate(college_name.find_elements_by_tag_name("tr")):
				# print("Colleges:--",college_name.find_elements_by_tag_name("tr")[applied_id].text.split("\n"))
				ms_colleges.append(college_name.find_elements_by_tag_name("tr")[applied_id].text.split("\n"))
				# raw_data = data_parser(raw_data,student_name,gre_engtest_wrkexp_papers[0],gre_engtest_wrkexp_papers[1],gre_engtest_wrkexp_papers[2],gre_engtest_wrkexp_papers[3],ug_info,*ms_colleges)
			# print(raw_data)
			buffer_df = data_parser(buffer_df,page_no,student_name,gre_engtest_wrkexp_papers[0],gre_engtest_wrkexp_papers[1],gre_engtest_wrkexp_papers[2],gre_engtest_wrkexp_papers[3],ug_info,*ms_colleges)
			time.sleep(2)
			driver.back()	
		buffer_df.to_csv(os.path.join(HOME,"Raw_Data.csv"),mode='a',header=False,index=False)
		buffer_df = buffer_df.iloc[0:0]
		driver.find_elements_by_class_name("btn.btn-default")[-1].send_keys("\n")
		time.sleep(1)
		page_no += 1
		if not check_exists_by_xpath("//button[@class='btn btn-default']"):
			break

if __name__=='__main__':
    
   
    with open(os.path.join(HOME,'config.json'),'r') as f:
    	meta_data = json.load(f)
    f.close()
    if not os.path.exists(os.path.join(HOME,"Raw_Data.csv")):
    	meta_data['csv']="None"
    	with open(os.path.join(HOME,'config.json'),'w') as f:
    		f.write(json.dumps(meta_data))
    	f.close()
    if meta_data['csv']=="None":
    	raw_data = pd.DataFrame(columns = ['Page_no','Student_name','gre','ielts_toefl','work_exp','papers','ug_college_name_location','ug_degree','ug_pct_cgpa',
									'ms_college_name','ms_college_course','ms_college_decision_status'])
    	raw_data.to_csv("Raw_Data.csv",index=False)
    	meta_data['csv']="Raw_Data.csv"
    	with open(os.path.join(HOME,'config.json'),'w') as f:
    		f.write(json.dumps(meta_data))
    	f.close()
    else:
    	raw_data = pd.read_csv(os.path.join(HOME,meta_data['csv']))
    print(raw_data)
    openyocket(URL,meta_data['credentials'])
    
    time.sleep(2)
    # search_universities()
    # scrape_data()
    deep_scrape(raw_data)
    