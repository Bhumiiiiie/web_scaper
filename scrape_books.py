# scrape_books.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = "http://books.toscrape.com/"

def get_soup(url):
    resp = requests.get(url)
    resp.raise_for_status()  # stop if page not reachable
    return BeautifulSoup(resp.text, "lxml")

def parse_book(book_tag):
    # book_tag is a <article class="product_pod"> element
    title = book_tag.h3.a['title'].strip()
    price = book_tag.find('p', class_='price_color').text.strip()  # like '£51.77'
    availability = book_tag.find('p', class_='instock availability').text.strip()
    # rating is encoded in class, e.g. <p class="star-rating Three">
    rating_p = book_tag.find('p', class_='star-rating')
    rating = [c for c in rating_p['class'] if c != 'star-rating'][0]  # 'One','Two','Three',...
    return {
        "title": title,
        "price": price,
        "availability": availability,
        "rating": rating
    }

def scrape_all_books():
    page_url = BASE_URL + "catalogue/page-1.html"
    books = []
    while True:
        print("Fetching:", page_url)
        soup = get_soup(page_url)
        product_list = soup.select("article.product_pod")
        for p in product_list:
            books.append(parse_book(p))
        # find "next" button
        next_btn = soup.select_one("li.next > a")
        if next_btn:
            next_href = next_btn['href']  # e.g. 'page-2.html' or '../page-2.html'
            # build absolute URL: the site uses relative paths from /catalogue/
            if "catalogue/" in page_url:
                # keep same directory
                base = page_url.rsplit('/', 1)[0] + '/'
                page_url = base + next_href
            else:
                page_url = BASE_URL + "catalogue/" + next_href
            time.sleep(1)  # polite delay
        else:
            break
    return books


if __name__ == "__main__":
    books = scrape_all_books()
    df = pd.DataFrame(books)

    # quick cleanup: price -> float, rating -> numeric
    df['price'] = (
        df['price']
        .astype(str)
        .str.replace('Â', '', regex=False)
        .str.replace('£', '', regex=False)
        .str.strip()
        .astype(float)
    )

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    df['rating_num'] = df['rating'].map(rating_map)

    df.to_csv("books.csv", index=False)
    print("Saved", len(df), "books to books.csv")
    print(df.head())
