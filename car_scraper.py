import requests
from bs4 import BeautifulSoup
from time import sleep
import csv


def parse_car_data(url):
    next_page = False

    with requests.get(url) as res:
        if res.status_code == 200:
            info = dict()
            info["cars"] = []

            soup = BeautifulSoup(res.content, "html.parser")

            # Check for another page
            if soup.find("a", attrs={"aria-label": "Next page"}) is not None:
                next_page = True

            list_rows = soup.find_all("div", attrs={"phx-hook": "VehicleCard"})
            for row in list_rows:
                car = dict()

                # Check Car Condition
                stock = row.find("p", attrs={"class": "stock-type"})
                car["condition"] = stock.text.strip() if stock else None

                # Check Listing Title
                title = row.find("h2", attrs={"class": "title"})
                car["title"] = title.text.strip() if title else None

                # Get Car Price
                price = row.find("span", attrs={"class": "primary-price"})
                car["price"] = (price.text.strip()).replace(",", "") if price else None

                # Get Car URL
                car_url = row.find("a", attrs={"data-linkname": "vehicle-listing", "data-activity-rule-type": "page-over-page"})
                car["url"] = "www.cars.com" + car_url['href'] if car_url else None

                info["cars"].append(car)

    # Continue to next page if one exists
    return info, next_page


if __name__ == '__main__':
    url = "https://www.cars.com/shopping/results/?page=1&page_size=100&list_price_max=&makes[]=ferrari&maximum_distance=all&stock_type=all&zip="
    print(f"Scraping Page 1\t\t{url}")

    cars = []
    while True:
        parsed = parse_car_data(url)
        for car in parsed[0]['cars']:
            cars.append(car)

        # Break the loop if there isn't another page
        if not parsed[1]:
            break

        # Prevent Rate Limiting by waiting 2 seconds
        sleep(2)

        # Go onto next page
        s = url
        start = s.find("?page=") + len("?page=")
        end = s.find("&page_size")
        url_first_half = s[:start]
        url_second_half = s[end:]
        next_page_number = str(int(s[start:end]) + 1)

        url = url_first_half + next_page_number + url_second_half
        print(f"Scraping Page {next_page_number}\t\t{url}")

    # Once all car data is gathered write out to a csv
    f = open('cars.csv', 'w')

    # create the csv writer
    writer = csv.writer(f)

    # write a header row to the csv file
    header = ['url', 'condition', 'car', 'price']
    writer.writerow(header)

    for car in cars:
        writer.writerow([car['url'], car['condition'], car['title'], car['price']])

    # close the file
    f.close()
