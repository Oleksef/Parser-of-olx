# Libraries
import psycopg2
import requests
from bs4 import BeautifulSoup as bs
import time
from datetime import date

# Settings
main_url = 'https://www.olx.ua'
category = ''
months = {1: 'січня', 2: 'лютого', 3: 'березня', 4: 'квітня', 5: 'травня', 6: 'червня', 7: 'липня', 8: 'серпня',
     9: 'вересня', 10: 'жовтня', 11: 'листопада', 12: 'грудня'}

# Receiving url, adding to list
category_url = 'https://www.olx.ua/d/uk/zhivotnye/sobaki/'  # input('Залишіть посилання на категорію: ')
list_page_url = list()  # List of urls, which will be parsed
list_page_url.append(category_url)


########################################################################################################################
#                                                      Functions                                                       #
########################################################################################################################

# Function of parsing url of pages
def get_url_page(url: str):
    """
    The function gets url, from which will be parsed last page number from olx.ua. It will take it and
    make new urls, changing parameter "?page=". At the end of the function, it will make an array with urls.
    :param url:
    :return:
    """

    req = requests.get(url)
    soup = bs(req.text, 'lxml')

    # Takes category name
    global category

    category = soup.find('div', class_='css-1l6p2f7').find_all('li', class_='css-7dfllt')[-1].text
    time.sleep(1)
    parse_page = soup.find_all('a', class_='css-1mi714g')[1]
    time.sleep(1)
    page_url = main_url + parse_page.get('href')
    page_number = int(soup.find_all('a', class_='css-1mi714g')[-1].text)

    for page in range(2, page_number + 1):
        t = page_url
        t = t.replace(t[t.find('2')], str(page))
        list_page_url.append(t)


# Function of parsing advertisement from one page of array
def gather_info(urls: list):
    """
    This function gets LIST of urls, gathers information from advertisement and adds it to database. Return message with
    finished work.
    :param urls:
    :return:
    """

    def gathering(url):
        """
        It receives url, parses information from advertisement and adds it to database.
        :param url:
        :return:
        """

        req = requests.get(url)
        soup = bs(req.text, 'lxml')
        name = soup.find('h1', class_='css-1soizd2 er34gjf0').text
        print(name, end='   | ')

        ctgr = category  # Here is the name of category, which can be added directly to the DB in the future
        print(ctgr, end='   | ')

        price = soup.find('h3', class_='css-ddweki er34gjf0').text
        print(price, end='   | ')

        view = soup.find('span', class_='css-42xwsi')  # .text
        print(view, end='   | ')

        advertisement_date = soup.find('span', class_='css-19yf5ek').text  # Need to be changed due to word "today" in the advertisement
        if ("Сьогодні" or "Сегодня") in d:
            advertisement_date = date.today().strftime(f"%d {months[date.today().month]} %Y") + (f" ({d.split(' ')[-1]})")
        print(advertisement_date, end='   | ')

        district = soup.find('p',
                             class_='css-1cju8pu er34gjf0')  # .text + soup.find('p', class_='css-b5m1rv er34gjf0').text
        print(district, end='   | ')

        print()

        pass

    # Loop for parsing advertisements in list of URLS (list_page_url), which contains function "gathering"
    for page in list_page_url:
        req_page = requests.get(page)
        soup_page = bs(req_page.text, 'lxml')
        advertisements = soup_page.find_all('div', class_='css-1sw7q4x')
        for adv in advertisements:
            adv_url = main_url + adv.find('a', class_='css-rc5s2u').get('href')
            gathering(adv_url)
            time.sleep(3.5)

    pass


# Function for testing
def test(url):
    req = requests.get(url)
    soup = bs(req.text, 'lxml')
    name = soup.find('h1', class_='css-1soizd2 er34gjf0').text
    print(name, end='   ')

    ctgr = category  # Here is the name of category, which can be added directly to the DB in the future
    print(ctgr, end='   ')

    price = soup.find('h3', class_='css-ddweki er34gjf0').text
    print(price, end='   ')

    view = soup.find('span', class_='css-42xwsi')  # .text         # Here is the problems with dynamic(?) objects
    print(view, end='   ')

    d = soup.find('span', class_='css-19yf5ek').text  # Need to be changed due to word "today" in the advertisement
    if ("Сьогодні" or "Сегодня") in d:
        d = date.today().strftime(f"%d {m[date.today().month]} %Y") + (f" ({d.split(' ')[-1]})")
    print(d, end='   ')

    district = soup.find('p',
                         class_='css-1cju8pu er34gjf0')  # .text + soup.find('p', class_='css-b5m1rv er34gjf0').text
    # Here is the problem with dynamic(?) objects
    print(district, end='   ')

    print()
    pass


########################################################################################################################
#                                                          Main                                                        #
########################################################################################################################

get_url_page(category_url)
# test('https://www.olx.ua/d/uk/obyavlenie/mrya-llak-hlopchik-frantsuzkiy-buldog-golubiy-frantsuz-torg-IDRpe7Z.html')
gather_info(list_page_url)
