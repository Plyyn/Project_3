import csv
from dataclasses import asdict

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from model import ProductData

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 YaBrowser/25.4.0.0 Safari/537.36"
}
BASE_URL = "https://vkusvill.ru/"

# Категории для парсинга
CATEGORIES = {
    "сыры": {
        "category_link": BASE_URL + "/goods/supermarket/syry/",
        "file_name": "vkusvill_syry.csv"
    },
    "мясо": {
        "category_link": BASE_URL + "goods/supermarket/myaso-ptitsa-p-f/",
        "file_name": "vkusvill_myaso.csv"
    },
    "макароны": {
        "category_link": BASE_URL + "/goods/supermarket/bakaleya/makarony-pasta/",
        "file_name": "vkusvill_makarony.csv"
    }
}

def get_links(page: int, category_link: str) -> list[str]:
    r = requests.get(
        url=category_link + f"/?PAGEN_1={page}",
        headers=HEADERS
    )
    soup = BeautifulSoup(r.content, 'html.parser')
    links = [
        tag['href']
        for tag in soup.select(".ProductCard > .ProductCard__content > a")
    ]
    return links

def get_pages(category_link: str) -> int:
    r = requests.get(
        url=category_link,
        headers=HEADERS
    )
    soup = BeautifulSoup(r.content, 'html.parser')
    max_page = int(soup.select(".VV_Pager__Item")[-2].text)

    return max_page

def get_product(link: str) -> ProductData:
    r = requests.get(
        url=BASE_URL + link,
        headers=HEADERS
    )
    soup = BeautifulSoup(r.content, 'html.parser')
    name_tag = soup.find("h1", class_="Product__title")
    price_tag = soup.find("span", class_="Price--label")
    weight_tag = soup.find("div", class_="ProductCard__weight")
    brand_tag = next(
        (div for div in soup.find_all('div', class_='VV23_DetailProdPageInfoDescItem')
         if div.find('h4', class_="VV23_DetailProdPageInfoDescItem__Title").get_text(strip=True) == 'Бренд')
    ).find("div", class_="VV23_DetailProdPageInfoDescItem__Desc")

    return ProductData(
        link=BASE_URL + link,
        name=name_tag.get_text(strip=True),
        price=price_tag.get_text(strip=True),
        weight=weight_tag.get_text(strip=True) if weight_tag else "",
        brand=brand_tag.get_text(strip=True),
    )

def save_data(data: list[ProductData], file_name: str):
    with open(file_name, "w", encoding="utf-8", newline="") as csvfile:
        fieldnames = ["name", "price", "weight", "brand", "link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([asdict(d) for d in data])

def process_category(category_link: str, file_name: str):
    pages = get_pages(category_link)
    links: list[str] = []
    data: list[ProductData] = []

    for page in range(1, pages + 1):
        links.extend(get_links(page, category_link))

    for link in tqdm(links, desc=f"Обработка {file_name}"):
        data.append(get_product(link))

    save_data(data, file_name)

def main():
    for category_name, category_data in CATEGORIES.items():
        print(f"Парсинг категории: {category_name}")
        process_category(category_data["category_link"], category_data["file_name"])

if __name__ == '__main__':
    main()
