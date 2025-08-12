from bs4 import BeautifulSoup
import re

def star_check(url, driver):
    driver.get(url)
    response = driver.page_source
    current_content = response
    soup = BeautifulSoup(current_content, "html.parser")
    like_button_divs = soup.find_all('div', id=re.compile('^like-button.*'))
    img = soup.find('img', attrs={"controls": False}, alt=lambda x: x and x.strip(), src=lambda x: x and 'blobs' in x.lower())
    if img:
        alt_text = img.get("alt", "no alt text")
    else:
        alt_text = "no image found"
    results = []
    for something, like_button_div in enumerate(like_button_divs):
        like_button = like_button_div.find('button')
        if like_button:
            star_count = like_button.text.strip()
            results.append((something, star_count, alt_text))
        else:
            print(f"Like button not found in div with id: {like_button_div['id']}")
    return results