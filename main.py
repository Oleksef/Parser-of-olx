# Libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import psycopg2
from datetime import date


# Settings
main_url = 'https://www.olx.ua'
months = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня', 7: 'липня', 8: 'серпня',
     9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}

# Receiving url, adding to list
category_url = 'https://www.olx.ua/d/uk/zhivotnye/sobaki/'  # input('Залишіть посилання на категорію: ')
list_page_url = list()  # List of urls, which will be parsed
list_page_url.append(category_url)

# Selenium settings
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-popup-blocking')
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.implicitly_wait(10)


# DataBase settins
conn = psycopg2.connect(dbname='olxpostdb', user='olxpars', password='olxpass', host='localhost')


########################################################################################################################
#                                                      Functions                                                       #
########################################################################################################################



# Main
def gather_info(url: str, urls: list):
    """
    The function gets url, from which will be parsed last page number from olx.ua. It will take it and
    make new urls, changing parameter "?page=". At the end of the function, it will make an array with urls.

    Then this function gets LIST of urls, gathers information from advertisement and adds it to database. Return message with
    finished work.
    :param url:
    :return:
    """

    driver.get(url)
    #time.sleep(1)

    # Takes category name
    category = driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[3]/div[3]/div/div[2]/ol/li[3]/span").text
    parse_page = driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[5]/div/section[1]/div/ul/li[2]/a")
    page_url = parse_page.get_attribute('href')
    page_numbers = int(driver.find_element(By.XPATH, "//*[@id='root']/div[1]/div[2]/form/div[5]/div/section[1]/div/ul/li[5]/a").text)


    # Loop which create urls for pages of the current category
    for number in range(2, page_numbers + 1):
        t = page_url
        t = t.replace(t[t.find('2')], str(number))
        list_page_url.append(t)


    # The main loop, which walks through pages and advertisements, adding information to DB. (WIP, it only shows in console info)
    for page in urls:
        print("#" * 200)
        print(f'CURRENT PAGE: {urls.index(page) + 1}')
        print("#" * 200, end='\n')
        advertisement_links = []
        driver.get(page)
        #time.sleep(2.5) # I need it for the page, which have to download the all advertisements
        advertisements = driver.find_elements(By.XPATH,
                                              '//*[@id="root"]/div[1]/div[2]/form/div[5]/div/div[2]/div[@data-cy]/a')
        # Adds urls of the all advertisements to list "advertisement_links".
        for i in range(len(advertisements)):
            advertisement_links.append(advertisements[i].get_attribute('href'))

        print(len(advertisement_links), 'advertisements.', end='\n')
        # Gathering information from advertisement, add it to data base.
        try:
            for advert in advertisement_links:
                with conn.cursor() as cur:
                    conn.autocommit = True
                    driver.get(advert)
                    #time.sleep(0.7)
                    name = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[3]/div[1]/div[2]/div[2]/h1').text
                    print(name, end='  |  ')

                    ctgr = category  # Here is the name of category, which can be added directly to the DB in the future
                    print(ctgr, end='  |  ')

                    price = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/div[3]/div[3]/div[1]/div[2]/div[3]/h3').text
                    print(price, end='  |  ')

                    view = int(driver.find_element(By.XPATH,
                                               '//*[@id="root"]/div[1]/div[3]/div[3]/div[1]/div[2]/div[9]/div/span[2]').text.strip()[-1])
                    print(view, end='  |  ')

                    advertisement_date = driver.find_element(By.XPATH,
                                                             '//*[@id="root"]/div[1]/div[3]/div[3]/div[1]/div[2]/div[1]/span/span').text
                    if "сьогодні" in advertisement_date or "сегодня" in advertisement_date:
                        advertisement_date = date.today().strftime(f"%d {months[date.today().month]} %Y") + f" ({advertisement_date.split(' ')[-1]})"
                    print(advertisement_date, end='  |  ')

                    district = driver.find_element(By.XPATH,
                                                   '//*[@id="root"]/div[1]/div[3]/div[3]/div[2]/div[2]/div/section/div[1]/div/p[1]').text.split(
                        ',')[0]
                    print(district, end='  |  ')

                    link_of_advert = advert
                    print(link_of_advert, end='  |  \n')
                    #time.sleep(0.5)
                    cur.execute("""
                        INSERT INTO olx.advert (name, category, price, view, date, district, url)
                        SELECT %s, %s, %s, %s, %s, %s, %s
                        WHERE NOT EXISTS (
                            SELECT 1 FROM olx.advert
                            WHERE name = %s AND category = %s AND price = %s AND view = %s 
                            AND date = %s AND district = %s AND url = %s
                        );
                        """,
                                (name, category, price, view, advertisement_date, district, link_of_advert,
                                 name, category, price, view, advertisement_date, district, link_of_advert)
                                )


        except Exception as e:
            print(f"Помилка: {e}")
            print('#' * 200)


def test():
    """
    Function for testing
    :return:
    """

    pass

########################################################################################################################
#                                                          Main                                                        #
########################################################################################################################

gather_info(category_url, list_page_url)


