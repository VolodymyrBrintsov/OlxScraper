from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup as sp
from parse.models import JobAdds
import os
import datetime
GOOGLE_CHROME_PATH = '/app/.apt/usr/bin/google_chrome'
CHROMEDRIVER_PATH = '/app/.chromedriver/bin/chromedriver'

def scraper():
    # Link
    link = "https://www.olx.ua/poltava"
    options = Options()

    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')

    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(executable_path=os.path.abspath('webdriver'), chrome_options=options)
    driver.get(link)

    jobs_list = []
    #Number of ads that user want ro parse
    jobs_num = int(50)
    #Counter of jobs that have been alreade parced
    jobs_counter = 0
    #Page counter (we start from page 1)
    page_counter = 1
    price_range = [500, 999999999]
    from_price, to_price = price_range
    # Iterationg through pages
    while link != None:
        # Get the number of work
        page_tree = sp(driver.page_source, 'html.parser')
        jobs = page_tree.find_all('tr', {'class': 'wrap'})

        # Iterating through work
        for job in jobs:
            if jobs_counter == jobs_num:
                break

            # Title
            title = job.find('h3').text.strip()

            #Price parsing
            try:
                price = job.find('p', {'class': 'price'}).text.strip()
                price_int = float(''.join(x for x in price if x.isdigit() or x=='.'))
            except:
                price = 'Не указана.'

            if ((from_price or to_price) != 0):
                if price == 'Не указана.' or from_price > price_int or price_int> to_price:
                    continue

            # Link to the details
            job_link = job.find('a')["href"]
            driver.get(job_link)

            # Finding a button to click in order to unblock telephone number
            try:
                phone_btn = driver.find_element_by_class_name('spoiler')
            except:
                continue
            # Wait until telephone number gets clear
            driver.execute_script("arguments[0].click();", phone_btn)
            wait = WebDriverWait(driver, 10)
            try:
                wait.until_not(ec.text_to_be_present_in_element((By.CLASS_NAME, 'contactitem'), 'x'))
            except:
                continue
            # Parse job link page
            job_page = sp(driver.page_source, 'html.parser')
            user_since = job_page.find('div', {'class': 'quickcontact__user-since'}).text
            #Parse heading
            try:
                heading = job_page.select('td.middle > ul > li')[1].text
            except:
                heading = 'Недобавленная рубрика.'
            #Parse phone number
            try:
                phones = job_page.select('div.contactitem')[0].text
                print(phones)
            except:
                # If no phone than ignore this job
                continue
            #Parse username
            try:
                name = driver.find_element_by_class_name('quickcontact__user-name').text
            except NoSuchElementException:
                name = 'Имя не указано.'

            jobs_list.append({'title': title.strip(),
                              'phone': phones.strip(),
                              'name': name.strip(),
                              'heading': heading.strip(),
                              'user_since': user_since.strip(),
                              'price': price,
                              'link': job_link.strip(),
                              })
            #Try to find unique Add if no then add it to database
            try:
                JobAdds.objects.get(phone=phones.strip())

            except (JobAdds.MultipleObjectsReturned, JobAdds.DoesNotExist):
                JobAdds.objects.create(
                    title =  title.strip(),
                    link =  job_link.strip(),
                    phone = phones.strip(),
                    name = name.strip(),
                    heading = heading.strip(),
                    price = price,
                    user_since = user_since.strip()
                    )

            jobs_counter += 1
        # Link to another page
        try:
            if jobs_counter == jobs_num:
                break
            page_counter += 1
            link = page_tree.find('a', {'class': '{page:'+str(page_counter)+'}'})['href']
            driver.get(link)
            driver.implicitly_wait(0.3)
        except (NoSuchElementException, IndexError, InvalidArgumentException, TypeError):
            link = None

    driver.close()