from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup as sp
from .forms import ExtraSearch, QuerySort
from .models import JobAdds
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
import os
import time
from django.template import loader

#Help function to dump adds in excel file
def dump_excel(data_set):
    df = pd.DataFrame.from_records(data_set).drop('time', axis=1).set_index('title').rename(
        columns={
            'phone': 'Телефон', 'heading': "Название рубрики", 'name': "Имя", 'user_since': "Дата регистрации",
            'price': "Цена", 'link': "Ссылка", }).rename_axis("Название")
    try:
        df.drop('id', axis=1, inplace=True)
    except:
        pass
    writer = pd.ExcelWriter('public/JobAdds.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name="Summary")
    worksheet = writer.sheets["Summary"]
    # set the column width as per your requirement
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:D', 30)
    worksheet.set_column('E:E', 30)
    worksheet.set_column('F:F', 30)
    writer.save()

#Home page
def home(request):
    return render(request, 'base.html')
#Extract popular adds on Olx
@login_required(login_url='login')
def extract(request):
    if request.method == 'POST':
        form = ExtraSearch(request.POST)
        if form.is_valid():
            # Link
            link = "https://www.olx.ua/poltava"
            chrome_options = webdriver.ChromeOptions()
            chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),
                                      chrome_options=chrome_options)
            driver.get(link)

            jobs_list = []
            #Number of ads that user want ro parse
            jobs_num = int(form.cleaned_data['jobs_num'])
            #Counter of jobs that have been alreade parced
            jobs_counter = 0
            #Page counter (we start from page 1)
            page_counter = 1
            price_range = [int(num) for num in form.cleaned_data['price'].split('-')]
            from_price, to_price = price_range
            heading = form.cleaned_data['heading']
            driver.find_element(By.XPATH, "//a[contains(@class, 'select')]").click()
            driver.find_element(By.XPATH, f"//a[text()='{heading}']").click()
            time.sleep(3)
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
            dump_excel(jobs_list)
            return render(request, 'parse/job_ads.html', {'jobs': jobs_list})
        return render(request, 'parse/extract.html', {'form': ExtraSearch(request.POST)})
    return render(request, 'parse/extract.html', {'form': ExtraSearch()})

#View to see all adds in database
@login_required(login_url='login')
def all_adds(request):
    if request.method == 'POST':
        form = QuerySort(request.POST)
        if form.is_valid():
            time = form.cleaned_data['datetime']
            if time != 'all':
                dump_excel(JobAdds.objects.filter(time=time).values())
                return render(request, 'parse/job_ads.html', {'jobs': JobAdds.objects.filter(time=time)})
            dump_excel(JobAdds.objects.all().values())
            return render(request, 'parse/job_ads.html', {'jobs': JobAdds.objects.all()})
    dump_excel(JobAdds.objects.all().values())
    return render(request, 'parse/job_ads.html', {'form': QuerySort()})

#View to download current excel file with adds
@login_required(login_url='login')
def download(request):
    with open('public/JobAdds.xlsx', 'rb') as file:
        response = HttpResponse(file, content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="JobAdds.xlsx"'
        return response

def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = AuthenticationForm()
        if request.method == 'POST':
            form = AuthenticationForm(data=request.POST)
            if form.is_valid():
                login(request, form.user_cache)
                return redirect('home')
            return render(request, 'login.html', {'form': form})
        return render(request, 'login.html', {'form': form})

@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')