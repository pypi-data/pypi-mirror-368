import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
import time
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
def main(driver=None):
    if driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://summer.hackclub.com")
    with open("som-cookie.txt", "r") as f:
        cookie_value = f.read().strip()
    driver.add_cookie({"name": "_journey_session",  "value": cookie_value})
    driver.get("https://summer.hackclub.com/votes/new")
    read_stuff = driver.find_elements(By.CSS_SELECTOR, "button.text-nice-blue")
    if read_stuff:
        print(read_stuff)
        for read in read_stuff:
            driver.execute_script("arguments[0].click();", read)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    print(soup.prettify())
    project_name = soup.find_all("h3", {"class": "text-lg md:text-2xl"})
    left_project = project_name[0].text.strip()
    left_project = left_project.replace("?", "")
    right_project = project_name[1].text.strip()
    right_project = right_project.replace("?", "")
    right_project = right_project.replace("Report ", "")
    right_project = right_project.replace("?", "")
    left_project = left_project.replace("Report ", "")
    if left_project == "Fight for Union" or right_project == "Fight for Union":
        main(driver)
    div_descriptions = soup.find_all("div", {"class": "text-base sm:text-lg text-gray-600"})
    left_div_descr = div_descriptions[0]
    left_description = left_div_descr.find("div").text.strip()
    right_div_descr = div_descriptions[1]
    right_description = right_div_descr.find('div').text.strip()
    button_strip = driver.find_element(By.CSS_SELECTOR, ".flex.flex-col.sm\\:flex-row.justify-center.items-center.space-y-4.sm\\:space-y-0.sm\\:space-x-6.mb-6")
    button_strip = button_strip.find_elements(By.TAG_NAME, "label")
    left_button = button_strip[0].find_element(By.TAG_NAME, "input")
    tie_button = button_strip[1].find_element(By.TAG_NAME, "input")
    right_button = button_strip[2].find_element(By.TAG_NAME, "input")
    form_element = driver.find_element(By.ID, "vote_explanation")
    usernames = []
    images = []
    bad_images = soup.find_all("div", {"class":"mt-2 sm:mt-3"})
    print(bad_images)
    for image in bad_images:
        if image.find("img"):
            img = image.find("img")
            images.append([img.get("src"), "image"])
        elif image.find("video"):
            video = image.find("video")
            img = video.get("src")
            if img:
                images.append([img, "video"])


    usernames_og = soup.find_all("img", {"class": "w-8 h-8 sm:w-10 sm:h-10 rounded-full mr-2 sm:mr-3"})
    entire_devlogs = soup.find_all("div", {"class": "px-4 py-8 sm:py-4 bg-[#F6DBBA] sm:rounded-xl"})
    usernames = []
    for username in usernames_og:
        if username not in usernames:
            usernames.append(username)
    ai_tags_left = entire_devlogs[0].find("span", {"class": "inline-flex items-center bg-[#FFE8CD] text-som-dark text-xs font-semibold px-2 py-1 rounded-full border border-[#a8956b] shadow-sm"})
    ai_tags_right = entire_devlogs[1].find("span", {"class": "inline-flex items-center bg-[#FFE8CD] text-som-dark text-xs font-semibold px-2 py-1 rounded-full border border-[#a8956b] shadow-sm"})
    devlogs_and_time = soup.find_all("span", {"class": "text-gray-800"})
    important_buttons = soup.find_all("a", class_="som-button-primary")
    devlog_1 = devlogs_and_time[0].text.strip() + " devlogs"
    time_1 = devlogs_and_time[1].text.strip()
    devlog_2 = devlogs_and_time[2].text.strip() + " devlogs"
    time_2 = devlogs_and_time[3].text.strip()
    devlogs = soup.find_all("div", {"class": "prose max-w-[32em] text-som-dark mb-2 sm:mb-3 text-base sm:text-lg 2xl:text-xl break-words overflow-wrap-anywhere"})
    num_left_devlogs = int(devlog_1.replace(" devlogs", ""))
    num_right_devlogs = int(devlog_2.replace(" devlogs", ""))
    left_devlogs = devlogs[0:num_left_devlogs]
    right_devlogs = devlogs[num_left_devlogs:num_left_devlogs + num_right_devlogs]
    important_stuff = []
    print(left_button, right_button, tie_button)
    wait = WebDriverWait(driver, 10)
    submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.som-button-primary[type='submit'][name='button']")))
    details = soup.find_all("div", {"class": "text-som-detail"})
    for detail in details:
        spans = detail.find_all("span")
        string_construct = ""
        for index in range(0, len(spans), 3):
            cool_string = spans[index:index+3]
            string_construct = " ".join(span.text.strip() for span in cool_string)
            important_stuff.append(string_construct)
    left_stuff = important_stuff[0:num_left_devlogs]
    right_stuff = important_stuff[num_left_devlogs:num_left_devlogs + num_right_devlogs]
    left_images = images[0:num_left_devlogs]
    right_images = images[num_left_devlogs:num_left_devlogs + num_right_devlogs]
    if ai_tags_left:
        if ai_tags_left and ai_tags_right:
            print("Both projects used AI")
            return [left_project, right_project, devlog_1, time_1, devlog_2, time_2, important_buttons, usernames, left_devlogs, left_stuff, right_stuff, right_devlogs, left_description, right_description, driver, left_button, right_button, tie_button, form_element, submit_button, [True, True], left_images, right_images]
        elif ai_tags_left and not ai_tags_right:
            print("Left AI tag found, but not right")
            return [left_project, right_project, devlog_1, time_1, devlog_2, time_2, important_buttons, usernames, left_devlogs, left_stuff, right_stuff, right_devlogs, left_description, right_description, driver, left_button, right_button, tie_button, form_element, submit_button, [True, False], left_images, right_images]
    elif ai_tags_right and not ai_tags_left:
        print("right ai tag")
        return [left_project, right_project, devlog_1, time_1, devlog_2, time_2, important_buttons, usernames, left_devlogs, left_stuff, right_stuff, right_devlogs, left_description, right_description, driver, left_button, right_button, tie_button, form_element, submit_button, [False, True], left_images, right_images]
    else:
        print("No AI tags found")
        return [left_project, right_project, devlog_1, time_1, devlog_2, time_2, important_buttons, usernames, left_devlogs, left_stuff, right_stuff, right_devlogs, left_description, right_description, driver, left_button, right_button, tie_button, form_element, submit_button, [False, False], left_images, right_images]
