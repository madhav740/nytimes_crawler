import re
import uuid
from datetime import datetime, timedelta
import time

import requests
from dateutil.relativedelta import relativedelta
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By

from utils import write_to_excel
from work_item_getter import WorkItemGetter

browser_lib = Selenium()


class Crawler:
    SECTION_CHECKBOX_BASE_SELECTOR = "css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div:nth-child(2) > div > div > div > ul > li:nth-child({list_number}) > label > input[type=checkbox]"
    DATE_RANGE_BASE_SELECTOR = "css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div.css-wsup08 > div > div > div > ul > li:nth-child({list_number}) > button"
    ACCEPT_COOKIE_SELECTOR = "css:#site-content > div.gdpr.shown.expanded.expanded-dock.css-jgcl4n.efw9frv0 > div.css-f63blv.e2qmvq0 > div > div.css-1cndoy8 > button:nth-child(1)"
    SECTION_MAPPING = [
        "Any",
        "Arts",
        "Blogs",
        "Briefing",
        "Business",
        "Corrections",
        "Magazine",
        "Opinion",
        "Sports",
        "World",
    ]

    def open_url(self):
        browser_lib.open_available_browser("https://nytimes.com")

    def accept_conditions(self):
        css_selector = "css:.css-1fzhd9j"
        # Condition button
        time.sleep(10)
        if browser_lib.is_element_visible(css_selector):
            browser_lib.click_button(css_selector)
        else:
            browser_lib.click_button(self.ACCEPT_COOKIE_SELECTOR)

    def click_search_button(self, search_term: str = "messi"):
        # type: ignore
        search_button_selector = "css:#app > div:nth-child(4) > div.NYTAppHideMasthead.css-1r6wvpq.e1m0pzr40 > header > section.css-9kr9i3.e1m0pzr42 > div.css-qo6pn.ea180rp0 > div.css-10488qs > button"
        browser_lib.click_button(search_button_selector)
        text_box_selector = "css:#search-input > form > div > input"
        browser_lib.input_text(text_box_selector, search_term)
        # Search
        go_button_selector = "css:#search-input > form > button"
        browser_lib.click_button(go_button_selector)

    def set_sorting_order(self):
        css_selector = "css:#site-content > div > div.css-1npexfx > div.css-nhmgdh > form > div.css-hrdzfd > div > select"
        browser_lib.select_from_list_by_label(css_selector, "Sort by Newest")

    def set_section(self, selected_section: str = "Any"):
        selector = "css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div:nth-child(2) > div > div > button"
        browser_lib.click_button(selector)
        for idx, section_name in enumerate(self.SECTION_MAPPING):
            if section_name == selected_section:
                browser_lib.click_button(
                    self.SECTION_CHECKBOX_BASE_SELECTOR.format(list_number=idx + 1)
                )
                break

    def calculate_date_range(self, month: int = 0):
        prev_month = month - 1 if month > 2 else 0
        end_date = datetime.now()
        start_date = (
            end_date
            - timedelta(days=end_date.day - 1)
            - relativedelta(months=prev_month)
        )
        self.start_date = start_date
        self.end_date = end_date

    def set_date_range(self, month: int = 0):
        date_button_selector = "css:#site-content > div > div.css-1npexfx > div.css-1az02az > div > div > div.css-wsup08 > div > div > button"
        browser_lib.click_button(date_button_selector)
        # Select custom date range
        browser_lib.click_button(self.DATE_RANGE_BASE_SELECTOR.format(list_number=6))
        # Set start_date to be current_date - month, where month is the number of months. Format the value to be in MM/DD/YYYY. Similarly, create end_date
        self.calculate_date_range(month)
        browser_lib.set_element_attribute(
            "css:#startDate", "value", self.start_date.strftime("%m/%d/%Y")
        )
        browser_lib.set_element_attribute(
            "css:#endDate", "value", self.end_date.strftime("%m/%d/%Y")
        )

    def load_all_articles(self):
        show_more_button_selector = "css:#site-content > div > div:nth-child(2) > div.css-1t62hi8 > div > button"
        if not browser_lib.is_element_visible(show_more_button_selector):
            return
        while True:
            ordered_list_element = browser_lib.find_element(
                "css:#site-content > div > div:nth-child(2) > div.css-46b038 > ol"
            )
            articles = ordered_list_element.find_elements(By.TAG_NAME, "li")
            last_article = articles[-1]
            article_date = last_article.find_element(By.TAG_NAME, "span").text
            if "," not in article_date:
                article_date = f"{article_date}, 2023"
            sanitized_article_date = datetime.strptime(article_date, "%B %d, %Y")
            if sanitized_article_date < self.start_date:
                break
            browser_lib.wait_and_click_button(show_more_button_selector)

    def fetch_articles(self, search_term):
        result = []
        ordered_list_element = browser_lib.find_element(
            "css:#site-content > div > div:nth-child(2) > div.css-46b038 > ol"
        )
        for article_element in ordered_list_element.find_elements(By.TAG_NAME, "li"):
            if article_element.get_attribute("class") == "css-1yvwzdo":
                # Ad Banner. Skip this element
                continue
            title = article_element.find_element(By.TAG_NAME, "h4").text
            description = article_element.find_element(
                By.CLASS_NAME, "css-16nhkrn"
            ).text
            article_date = article_element.find_element(By.TAG_NAME, "span").text
            if "," not in article_date:
                article_date = f"{article_date}, 2023"
            img_element = article_element.find_element(By.TAG_NAME, "img")
            url = img_element.get_attribute("src")
            file_name = self.download_and_save_image(url)
            (tile_count, description_count) = self.get_count(
                title, description, search_term
            )
            contains_monetary_value = self.contains_monetary_values(
                title
            ) or self.contains_monetary_values(description)
            record = {
                "title": title,
                "description": description,
                "article_date": article_date,
                "image_url": url,
                "image_path": file_name,
                "title_count": tile_count,
                "description_count": description_count,
                "contains_monetary_value": contains_monetary_value,
            }
            result.append(record)
        return result

    def download_and_save_image(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            file_name = f"{uuid.uuid4()}.jpg"
            with open(f"output/{file_name}", "wb") as f:
                f.write(response.content)
            return file_name
        else:
            print(f"Failed to fetch url: {url}")
            return None

    def contains_monetary_values(self, text):
        pattern = r"\$[\d,.]+|\b\d+(\.\d{1,2})?\s?(billion|million|thousand)?\s?(dollars|USD)?\b"
        return bool(re.search(pattern, text))

    def get_count(self, title: str, description: str, search_term: str):
        title_count = title.lower().count(search_term.lower())
        description_count = description.lower().count(search_term.lower())
        return (title_count, description_count)

    def run(self, search_phrase, news_categories, months):
        try:
            self.open_url()
            self.accept_conditions()
            self.click_search_button(search_phrase)
            self.set_sorting_order()
            self.set_section()
            self.set_date_range(months)
            self.load_all_articles()
            return self.fetch_articles(search_phrase)
        except Exception as e:
            print("ERROR OCCURRED")
            raise e
        finally:
            browser_lib.close_all_browsers()
            return records