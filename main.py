import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import facebook_login, facebook_password
from connect import get_data, record_data
from typing import List


ua_chrome = " ".join(["Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                      "AppleWebKit/537.36 (KHTML, like Gecko)",
                      "Chrome/108.0.0.0 Safari/537.36"])
headers = {"user-agent": ua_chrome}
domain = "https://www.facebook.com"


def get_price(bs_object: BeautifulSoup) -> str:
    price = bs_object.find(name="div", class_="x1anpbxc")
    if price is not None:
        price = price.text.strip()
    else:
        price = bs_object.find(name="div", class_="x1xmf6yo")
        if price is not None:
            price = price.text.strip()
        else:
            price = "Not Found"
    return price


def get_rating(bs_object: BeautifulSoup) -> int:
    all_aria_label_divs = bs_object.find_all(name="div", attrs={"aria-label": True})
    for div in all_aria_label_divs:
        if "rating" in div["aria-label"]:
            result = div["aria-label"].split(" ")[0]
            return result
    return 0


def get_date_of_registration(bs_object: BeautifulSoup) -> str:
    str_bs_object = str(bs_object)
    start_index = str_bs_object.find("Joined Facebook in")
    str_bs_object = str_bs_object[start_index:]
    end_index = str_bs_object.find("</span>")
    result = str_bs_object[:end_index]
    if "Joined Facebook in" in result:
        return result.replace("<!-- -->", "")
    return "No information"


def get_animal_friendly(bs_object: BeautifulSoup) -> bool:
    if "Dog and cat friendly" in bs_object.text or "Cat friendly" in bs_object.text or "Dog friendly" in bs_object.text:
        return True
    return False


def get_address(bs_object: BeautifulSoup) -> str:
    i_tag = bs_object.find(name='i', attrs={"style": "background-image:url('https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/ZpIxH1CXAcn.png');background-position:0 -923px;background-size:25px 1490px;width:20px;height:20px;background-repeat:no-repeat;display:inline-block"})
    return i_tag.parent.parent.text.strip()


def get_date_of_publication(bs_object: BeautifulSoup) -> str:
    i_tag = bs_object.find(name="i", attrs={"style": "background-image:url('https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/ZpIxH1CXAcn.png');background-position:0 -419px;background-size:25px 1490px;width:20px;height:20px;background-repeat:no-repeat;display:inline-block"})
    return i_tag.parent.parent.text.strip()


def authorization(browser: webdriver.Chrome) -> None:
    print("[INFO] Авторизуемся в системе...")
    browser.get(url="https://www.facebook.com/")
    login_input = browser.find_element(By.ID, "email")
    login_input.send_keys(facebook_login)
    password_input = browser.find_element(By.ID, "pass")
    password_input.send_keys(facebook_password)
    login_button = browser.find_element(By.TAG_NAME, "button")
    login_button.click()
    time.sleep(5)


def get_object_links(browser: webdriver.Chrome, url: str) -> List[str]:
    print("[INFO] Собираем ссылки на объекты...")
    browser.get(url=url)
    old_bs_object = BeautifulSoup(browser.page_source, "lxml")
    index = 0
    while True:
        index += 1
        print(f"[INFO - Facebook] Ссылки со страницы {index} страницы успешно собраны")
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        current_bs_object = BeautifulSoup(browser.page_source, "lxml")
        if current_bs_object == old_bs_object:
            break
        if index == 2:
            break
        old_bs_object = current_bs_object
    bs_object = BeautifulSoup(browser.page_source, "lxml")
    product_link_objects = bs_object.find_all(name="div", class_="x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e xnpuxes x291uyu x1uepa24 x1iorvi4 xjkvuk6")
    product_links = list()
    for product_link_object in product_link_objects:
        if product_link_object.a is not None:
            product_link = domain + product_link_object.a["href"].split("?")[0]
            product_links.append(product_link)
    return product_links


def get_object_info(browser: webdriver.Chrome, object_url: str) -> dict:
    print(f"[INFO] Обрабатываем объект {object_url}")
    browser.get(object_url)
    try:
        show_all_description = browser.find_elements(By.TAG_NAME, "span")
        for el in show_all_description:
            if el.text == "See more":
                browser.execute_script("arguments[0].click();", el)
                time.sleep(2)
                break
    except Exception as ex:
        pass
    bs_object = BeautifulSoup(browser.page_source, "lxml")
    title = bs_object.find(name="title").text
    description = bs_object.find(name="div", class_="xz9dl7a x4uap5 xsag5q8 xkhd6sd x126k92a").text
    description = description.replace("See less", "").replace("See translation", "").strip()
    price = get_price(bs_object=bs_object)

    animal_friendly = get_animal_friendly(bs_object=bs_object)
    address = get_address(bs_object=bs_object)
    date_of_publication = get_date_of_publication(bs_object=bs_object)
    rating = get_rating(bs_object=bs_object)
    date_of_registration = get_date_of_registration(bs_object=bs_object)

    return {"title": title, "price": price, "object_url": object_url, "description": description,
            "animal_friendly": animal_friendly, "address": address, "date_of_publication": date_of_publication,
            "rating": rating, "date_of_registration": date_of_registration}


def get_new_object_links(object_links: List[str], exist_object_links: List[str]) -> List[str]:
    result = list()
    for object_link in object_links:
        if object_link not in exist_object_links:
            result.append(object_link)
    return result


def main() -> None:
    exist_object_links = get_data()
    result = list()
    url = "https://www.facebook.com/marketplace/category/propertyrentals?sortBy=creation_time_descend&exact=false"
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua_chrome}")
    options.add_argument("--disable-notifications")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument('--disable-dev-shm-usage')
    browser = webdriver.Chrome(options=options)
    try:
        authorization(browser=browser)
        print("[INFO] Авторизация успешно завершена")
        object_links = get_object_links(browser=browser, url=url)
        new_object_links = get_new_object_links(object_links=object_links, exist_object_links=exist_object_links)
        all_objects = list()
        exceptions = 0
        print(len(new_object_links))
        for object_link in new_object_links:
            try:
                sub_result = get_object_info(browser=browser, object_url=object_link)
                all_objects.append(sub_result)
            except Exception as ex:
                exceptions += 1
                print(f"[ERROR] {ex} ({object_link})")
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument(f"user-agent={ua_chrome}")
                    options.add_argument("--disable-notifications")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument('--disable-dev-shm-usage')
                    browser = webdriver.Chrome(options=options)
                    authorization(browser=browser)
                    sub_result = get_object_info(browser=browser, object_url=object_link)
                    all_objects.append(sub_result)
                except Exception as ex:
                    print(f"[ERROR] {ex} ({object_link})")
                    exceptions += 1
                    continue

        for current_object in all_objects:
            if ("sublease" in current_object["description"].lower() or
                    "sublet" in current_object["description"].lower() or
                    "subletting" in current_object["description"].lower()):
                result.append(current_object)
        print(result)
        record_data(result=result)
    finally:
        browser.close()
        browser.quit()


def test():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua_chrome}")
    options.add_argument("--disable-notifications")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    authorization(browser=browser)
    object_link = "https://www.facebook.com/marketplace/item/226473383166620/"
    try:
        result = get_object_info(browser=browser, object_url=object_link)
        print(result)
    finally:
        browser.close()
        browser.quit()


if __name__ == "__main__":
    main()
