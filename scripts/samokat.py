"""Данный модуль парсит данные о мясе из самоката.
Чтобы получить данные о макаронах и сыре, нужно изменить константы  CATEGORY_LINK и FILE_NAME"""


import csv
from dataclasses import asdict

from bs4 import BeautifulSoup
from selenium import webdriver

from model import ProductData

BASE_URL = "https://samokat.ru"
CATEGORY_LINK = "/category/myaso-i-ptitsa" # для сыра:"/category/syr" ; для макарон: "/category/makarony-i-lapsha"
FILE_NAME = "../samokat_myaso.csv"  #samokat_syry.csv для сыра и "samokat_makarony.csv" для макарон

driver = webdriver.Chrome()


def save_data(data: list[ProductData]):
    with open(FILE_NAME, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["name", "price", "weight", "brand", "link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([asdict(d) for d in data])


def main():
    data: list[ProductData] = []

    driver.get(BASE_URL + CATEGORY_LINK)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    containers = soup.find_all("div", attrs={"class": "ProductsList_productList__jjQpU"})
    for container in containers:
        product_links = container.find_all("a")
        for product in product_links:
            name = product.find("div", {"class": "ProductCard_name__2VDcL"}).find("span").get_text(strip=True)
            weight = product.find("div", {"class": "ProductCard_specification__Y0xA6"}).find("span").get_text(
                strip=True)

            old_price_span = product.find("span", {"class": "ProductCardActions_oldPrice__d7vDY"})
            if old_price_span:
                price = old_price_span.get_text(strip=True)
            else:
                price = product.find("div", {"class": "ProductCardActions_text__3Uohy"}).find("span").get_text(
                    strip=True)
            data.append(ProductData(
                name=name,
                price=price,
                weight=weight,
                brand="",
                link=BASE_URL + product.get("href"),
            ))
    save_data(data)

if __name__ == '__main__':
    main()
