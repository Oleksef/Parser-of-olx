import change_price
from connection import add_to_database
from settings import *


def create_list_url(category_list):
    """
    Takes the url of next page, makes the url for the other pages and appends it to list "list_page_url"
    :return:
    """
    parse_page = driver.find_element(By.XPATH,
                                     "//*[@id='mainContent']/div[2]/form/div[5]/div/section[1]/div/ul/li[2]/a")
    page_url = parse_page.get_attribute('href')
    page_numbers = int(driver.find_elements(By.XPATH, '//*[@id="mainContent"]/div[2]/form/div[5]/div/section[1]/'
                                                      'div/ul/li[@data-testid="pagination-list-item"]/a')[-1].text)
    # Loop which create urls for pages of the current category
    list_page_url = [category_list] + [page_url.replace(page_url[page_url.find('2')], str(number)) for number
                                       in range(2, page_numbers + 1)]
    return list_page_url


def gather_data(url_category: str):
    """
    Then this function gets LIST of urls, gathers information from advertisement and adds it to database. Return
    message with finished work.
    :param url_category: url of the category, which will be parsed.
    :return:
    """

    def parse_data(link_advert: str):
        """
        Function for parsing data from an ad.
        :param link_advert: a link of an advertisement.
        :return: list of data from an ad.
        """
        try:
            driver.get(link_advert)
            name = driver.find_element(By.XPATH,
                                       '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[2]/h1').text
            price = driver.find_element(By.XPATH,
                                        '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[3]/h3').text
            currency = change_price.currency_sign(price)
            price = change_price.to_int(price)
            view = int(driver.find_element(By.XPATH,
                                           '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[9]/div/span[2]').
                       text.strip()[-1])
            advertisement_date = driver.find_element(By.XPATH,
                                                     '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[1]/'
                                                     'span/span').text

            if "сьогодні" in advertisement_date or "сегодня" in advertisement_date:
                advertisement_date = date.today().strftime(
                    f"%d {months[date.today().month]} %Y") + f" ({advertisement_date.split(' ')[-1]})"

            district = driver.find_element(By.XPATH,
                                           '//*[@id="mainContent"]/div[3]/div[3]/div[2]/div[@class='
                                           '"css-1dp6pbg"]/div/section/div[1]/div/p[1]').text.split(',')[0]

            data_from_ad = [name, category, price, currency, view, advertisement_date, district, link_advert]
            add_to_database(data_from_ad)
            data_from_ad.clear()

        except Exception as e:
            print('!' * 200)
            print(f"Помилка: {e}")
            print('!' * 200)

    driver.get(url_category)
    # At once take from the page the category and save it to variable "category"
    category = driver.find_elements(By.XPATH,
                                    '//*[@id="mainContent"]/div[2]/form/div[3]/div[3]/div/div[2]/ol/li')[-1].text
    url_pages = create_list_url(url_category)

    # The main loop, which walks through pages and advertisements, adding information to DB. Prints parsed information.
    for page in url_pages:
        print(f'CURRENT PAGE: {url_pages.index(page) + 1}')

        advertisements_links = []
        driver.get(page)
        advertisements = driver.find_elements(By.XPATH,
                                              '//*[@id="mainContent"]/div[2]/form/div[5]/div/div[2]/div[@data-cy]/a')

        # Adds urls of the all advertisements to list "advertisement_links".
        for i in range(len(advertisements)):
            advertisements_links.append(advertisements[i].get_attribute('href'))

        # Gathering information from advertisement, add it to data base.
        for ad_link in advertisements_links:
            print(advertisements_links.index(ad_link) + 1, end=' ')
            print(ad_link)
            parse_data(ad_link)

        #add_to_database(data_from_ad)
        #data_from_ad.clear()
