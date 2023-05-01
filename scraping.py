from selenium.webdriver.common.by import By
import change_price
from settings import *


def create_list_url(category_list):
    """
    Takes the url of next page, makes the url for the other pages and appends it to list "list_page_url"
    :return:
    """
    parse_page = driver.find_element(By.XPATH,
                                              "//*[@id='mainContent']/div[2]/form/div[5]/div/section[1]/div/ul/li[2]/a")
    page_url = parse_page.get_attribute('href')
    page_numbers = int(driver.find_elements(By.XPATH,
                                                    '//*[@id="mainContent"]/div[2]/form/div[5]/div/section[1]/div/ul/li[@data-testid="pagination-list-item"]/a')[-1].text)
    # Loop which create urls for pages of the current category
    list_page_url = [category_list] + [page_url.replace(page_url[page_url.find('2')], str(number)) for number
                                      in range(2, page_numbers + 1)]
    print(list_page_url)

    # the first version of list with urls of pages
    # for number in range(2, page_numbers + 1):
    #     t = page_url
    #     t = t.replace(t[t.find('2')], str(number))
    #     list_page_url.append(t)

    return list_page_url


def gather_info(url_category: str, print_parsed=True):
    """
    Then this function gets LIST of urls, gathers information from advertisement and adds it to database. Return
    message with finished work.
    :param print_parsed: "False" if you don't want to see in console the all information from an advertisement.
    :param url_category: url of the category, which will be parsed.
    :return:
    """

    driver.get(url_category)

    # At once take from the page the category and save it to variable "category"
    category = driver.find_elements(By.XPATH,
                                             '//*[@id="mainContent"]/div[2]/form/div[3]/div[3]/div/div[2]/ol/li')[
        -1].text

    url_pages = create_list_url(url_category)

    # The main loop, which walks through pages and advertisements, adding information to DB. Prints parsed information.
    for page in url_pages:
        if print_parsed:
            print("#" * 200)
            print(f'CURRENT PAGE: {url_pages.index(page) + 1}')
            print("#" * 200, end='\n')

        advertisement_links = []
        driver.get(page)
        advertisements = driver.find_elements(By.XPATH,
                                                       '//*[@id="mainContent"]/div[2]/form/div[5]/div/div[2]/div['
                                                       '@data-cy]/a')

        # Adds urls of the all advertisements to list "advertisement_links".
        for i in range(len(advertisements)):
            advertisement_links.append(advertisements[i].get_attribute('href'))
        if print_parsed:
            print(len(advertisement_links), 'advertisements.', end='\n')

        # Gathering information from advertisement, add it to data base.
        for advert in advertisement_links:
            try:
                with conn.cursor() as cur:
                    conn.autocommit = True
                    driver.get(advert)
                    name = driver.find_element(By.XPATH,
                                               '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[2]/h1').text
                    price = driver.find_element(By.XPATH,
                                                '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[3]/h3').text
                    currency = change_price.currency_sign(price)
                    price = change_price.to_int(price)
                    view = int(driver.find_element(By.XPATH,
                                                   '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[9]/div/'
                                                   'span[2]').text.strip()[-1])
                    advertisement_date = driver.find_element(By.XPATH,
                                                             '//*[@id="mainContent"]/div[3]/div[3]/div[1]/div[2]/div[1]'
                                                             '/span/span').text

                    if "сьогодні" in advertisement_date or "сегодня" in advertisement_date:
                        advertisement_date = date.today().strftime(
                            f"%d {months[date.today().month]} %Y") + f" ({advertisement_date.split(' ')[-1]})"

                    district = driver.find_element(By.XPATH,
                                                   '//*[@id="mainContent"]/div[3]/div[3]/div[2]/div[@class='
                                                   '"css-1dp6pbg"]/div/section/div[1]/div/p[1]').text.split(',')[0]
                    link_of_advert = advert

                    if print_parsed:
                        print(name, end='  |  ')
                        print(category, end='  |  ')
                        print(currency, end='  |  ')
                        print(price, end='  |  ')
                        print(view, end='  |  ')
                        print(advertisement_date, end='  |  ')
                        print(district, end='  |  ')
                        print(link_of_advert, end='  |\n')

                    cur.execute(sql.SQL("""
                        CREATE TABLE IF NOT EXISTS olx.{} (name varchar(300), category varchar(60), price integer,
                                                           currency varchar(5), view integer, date varchar(30),
                                                           district varchar(30), url varchar(500));
                                        """).format(sql.Identifier(category)))

                    cur.execute(sql.SQL("""
                        INSERT INTO olx.{} (name, category, price, currency, view, date, district, url)
                        SELECT %s, %s, %s, %s, %s, %s, %s, %s
                        WHERE NOT EXISTS (
                            SELECT 1 FROM olx.{}
                            WHERE name = %s AND category = %s AND price = %s AND currency = %s AND view = %s 
                            AND date = %s AND district = %s AND url = %s
                        );
                        """).format(sql.Identifier(category), sql.Identifier(category)),
                                (
                                    name, category, price, currency, view, advertisement_date, district, link_of_advert,
                                    name, category, price, currency, view, advertisement_date, district, link_of_advert)
                                )

            except Exception as e:
                if print_parsed:
                    print('!' * 200)
                    print(f"Помилка: {e}")
                    print('!' * 200)
