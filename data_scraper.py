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

import json

import pandas as pd
import numpy as np

URL = "https://yocket.in/profiles/find/matching-admits-and-rejects"
DRIVER_PATH = r"C:\Users\Cosmos\Documents\Jayen\Pre MS\Big Game\Yocket Analysis\chromedriver_win32\chromedriver.exe"
driver = webdriver.Chrome(DRIVER_PATH)


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

def data_parser(raw_data, student_name, gre_gmat, toefl_ielts, work_exp, papers, ug_info, *args_ms_colleges):
# 	primary_id = student_name
# 	if len(gre_gma)
#   interested has three values
#	applied has 4 values
#   admit/reject has 5 values (ignore coments and blank)
	# if (student_name in raw_data['Student_name'].tolist()):
	# 	print('visited_node')
	# 	return raw_data
	# else:
	if len(gre_gmat)!=2 and len(gre_gmat)!=3:
		gre_scores = gre_gmat[1:].lower()
	else:
		gre_scores = np.nan
		# print("not appeared")
	
	if toefl_ielts[0].lower()!="eng test":
		eng_test = toefl_ielts.lower()
	else:
		eng_test = np.nan
		# print("Not Available")
	
	work_exp = work_exp[1].lower()
	papers = papers[1].lower()

	assert len(ug_info)==6,"Failed to handle ug college info, wrong assumption on generic pattern"

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
		elif len(ms_colleges)==4:
			ms_colleges_app_date = ms_colleges[2][9:]
			ms_colleges_des_date = np.nan
		elif len(ms_colleges) == 5 or len(ms_colleges) == 8:
			ms_colleges_app_date = ms_colleges[2][9:]
			ms_colleges_des_date = ms_colleges[3][10:]
		else:
			print("~~~~~~~~~~",ms_colleges,"~~~~~~~~~~~~")
			raise Exception("Did not acoount for this particular case of ms college format")

		row = [student_name, gre_scores, eng_test, work_exp,papers, ug_college_name_location, ug_college_degree, ug_grades, ms_college_name,
				ms_college_course, ms_colleges_decision, ms_colleges_app_date, ms_colleges_des_date]
		# print(gre_scores,eng_test,work_exp,papers,ug_college_name_location,ug_college_degree,ug_grades,ms_college_name,\
				# ms_college_course,ms_colleges_decision,ms_colleges_app_date,ms_colleges_des_date)	
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

def deep_scrape():
	name_college_course_intake = driver.find_elements_by_class_name("col-sm-8")
	gre_engtest_wrkexp_papers = []
	raw_data = pd.DataFrame(columns = ['Student_name','gre','ielts_toefl','work_exp','papers','ug_college_name_location','ug_degree','ug_pct_cgpa',
									'ms_college_name','ms_college_course','ms_college_decision_status'])
	ms_colleges = []
	while check_exists_by_xpath("//button[@class='btn btn-default']"):
		for idx,_ in enumerate(name_college_course_intake):
			student_name = driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").text
			# print("Student Name:",driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").text)
			if (student_name in raw_data['Student_name'].tolist()):
				print('visited_node')
				continue
			university_name = driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("small").text.split('\n')
			driver.find_elements_by_class_name("col-sm-8")[idx].find_element_by_tag_name("a").send_keys("\n")
			candidate_profile = driver.find_elements_by_class_name("row.text-center")
			for i in range(4):
				# print(":::",candidate_profile[0].find_elements_by_tag_name("div")[i].text.split("\n"))
				gre_engtest_wrkexp_papers.append(candidate_profile[0].find_elements_by_tag_name("div")[i].text.split("\n"))

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
			raw_data = data_parser(raw_data,student_name,gre_engtest_wrkexp_papers[0],gre_engtest_wrkexp_papers[1],gre_engtest_wrkexp_papers[2],gre_engtest_wrkexp_papers[3],ug_info,*ms_colleges)

			time.sleep(1)
			driver.back()	
		print(raw_data)
		driver.find_elements_by_class_name("btn.btn-default")[-1].send_keys("\n")
		
if __name__=='__main__':
    
    HOME = r'C:\Users\Cosmos\Documents\Jayen\Pre MS\Big Game\Yocket Analysis'
    with open(os.path.join(HOME,'config.json'),'r') as f:
    	meta_data = json.load(f)
    f.close()
    if meta_data['csv']=="None":
    	raw_data = pd.DataFrame(columns = ['Student_name','gre','ielts_toefl','work_exp','papers','ug_college_name_location','ug_degree','ug_pct_cgpa',
									'ms_college_name','ms_college_course','ms_college_decision_status',';la'])
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
    deep_scrape()
    