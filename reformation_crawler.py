import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import re

seed = "https://www.thereformation.com"
toCrawl = [seed]
crawled = []
dataCollected = []

def get_links_from_page(url):
    global toCrawl, seed, actualSeed
    print("Getting links")
    print("Url: ", url, len(url)) 
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    urls = []
    for link in soup.find_all("a"):
        href = str(link.get('href'))
        if len(href) > 1 and href[0] == "/":
            if (seed + href) not in toCrawl:
                urls.append(seed + href)
        elif len(href) > 1 and "facebook" not in href and "#" not in href and "twitter" not in href and "faq" not in href and "about" not in href and "contact" not in href and "careers" not in href:
            if href not in toCrawl and seed in href and "terms" not in href and "login" not in href and "password" not in href and "help" not in href and "stores" not in href:
                urls.append(href)
    driver.quit()
    print("URLS: ", urls)
    return list(set(urls))


def remove_special_characters(data):
    newData = re.sub(r"[^a-zA-Z0-9]+"," ",data)
    newData = newData.lower()
    return newData


def get_product_name(soup):
    print("Getting name")
    for tag in soup.find_all("h1"):
      if tag.get("class") == ['product-details__name']:
        return tag.text        
    return None

"""def get_reference_number(soup):
    print("Getting reference number")
    for tag in soup.find_all("div"):
        if tag.get("class") == ["sizes--block__item"]:
            return (tag.get("data-value").split("-"))[0]
    return None"""

def get_product_description(soup):
    print("Getting description")
    for tag in soup.find_all("div"):
        if tag.get("class") == ["product-details__description", "flex-order--one"]:
          return tag.text
    return None

def get_product_price(soup):
    print("Getting price")
    for tag in soup.find_all("div"):
        if tag.get("class") == ["product-prices", "product-prices--details"]:
            return tag.text
    return None


def get_product_images(soup):
    print("Getting Images")
    imageUrls = []
    for tag in soup.find_all("img"):
        if tag.get("class") == ["product-details__primary-image-link-image", "lazyload"]:
            if "jpg" in tag.get("src"):
                imageUrls.append(tag.get("src"))
        if tag.get("class") == ["product-details__primary-image-link-image", "lazyloaded"]:
            if "jpg" in tag.get("src"):
                imageUrls.append(tag.get("src"))
    return imageUrls



def get_data(url):
    print("In get data")
    productData = {}
    driver = webdriver.Chrome()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'lxml')
    productName = get_product_name(soup)
    print("Product name: ", productName)
    #referenceNumber = get_reference_number(soup)
    #print("Reference Number: ", referenceNumber)
    productDescription = get_product_description(soup)
    print("Product Description: ", productDescription)
    productPrice = get_product_price(soup)
    print("Product Price: ", productPrice)
    productImages = get_product_images(soup)
    print("Product Images: ", productImages)
    driver.quit()
    """referenceNumbers = []
    if len(dataCollected )> 0:
        for data in dataCollected:
            referenceNumbers.append(data["Reference Number"])"""
    if productName != None and productImages != []:
        productData["Product Name"] = productName
        #productData["Reference Number"] = referenceNumber
        productData["Product Description"] = productDescription
        productData["Product Price"] = productPrice
        productData["Product Images"] = productImages
        return productData
    return {}
        


def crawl(url):
    global toCrawl, crawled, dataCollected
    while len(toCrawl) > 0 and len(dataCollected) < 20:
        print(url)
        if url not in crawled:
            print("HERE")
            print("Data collected: ", dataCollected, len(dataCollected))
            print(len(toCrawl))
            print(len(crawled)) 
            toCrawl = toCrawl + get_links_from_page(url)
            crawled.append(url)
            toCrawl = list(set(toCrawl) - set(crawled))
            url_data = get_data(url)
            if url_data == {}:
                print("url_data: ", url_data)
                next_url = toCrawl.pop()
                url = next_url
            else:
                print("url_data: ", url_data)
                dataCollected.append(url_data)
                next_url = toCrawl.pop()
                url = next_url
    if len(dataCollected) == 20:
        productsInfo = []
        for data in dataCollected:
            product = []
            product.append(data["Product Name"])
            #product.append(data["Reference Number"])
            product.append(data["Product Description"])
            product.append(data["Product Price"])
            product.append(data["Product Images"])
            productsInfo.append(product)
        df = pd.DataFrame(productsInfo, columns = ['Name', 'Description', 'Price', 'Images'])
        df.to_csv("frankandoak.csv")

crawl(seed)
