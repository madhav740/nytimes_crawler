from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By
from article_info import ArticleInfo
import constant
import utils
import time

class NytimesCrawler:

    def __init__(self, search_term, news_categories, months, output_directory="output"):
        self.__browser_lib = Selenium()
        self.search_term = search_term
        self.news_categories = [category.lower().capitalize() for category in news_categories]
        self.months = months
        self.start_date = None
        self.end_date = None
        self.image_download_directory = output_directory
        if len(news_categories) == 0:
            self.news_categories = ['Any']
        if not all(category in constant.NEWS_CATEGORIES for category in self.news_categories):
            raise ValueError("Valid news categories are: ", constant.NEWS_CATEGORIES)

    def run(self):
        result = []
        self.load_home_page()
        self.input_search_term_and_search()
        self.set_section()
        self.__calculate_date_range()
        self.set_date_filter()
        self.set_sorting_order()
        self.load_all_articles()
        result = self.fetch_articles()
        return result

        # try:
        #     self.load_home_page()
        #     self.input_search_term_and_search()
        #     self.set_section()
        #     self.__calculate_date_range()
        #     self.set_date_filter()
        #     self.set_sorting_order()
        #     self.load_all_articles()
        #     result = self.fetch_articles()
        # except Exception as e:
        #     raise e
        # finally:
        #     self.__browser_lib.close_all_browsers()
        #     return result

    def load_home_page(self):
        self.__browser_lib.open_available_browser(constant.NY_TIMES_HOME_PAGE_URL)
        time.sleep(10)
        if self.__browser_lib.is_element_visible(constant.CONTINUE_TERMS_AND_CONDITIONS_POP_UP_CSS_SELECTOR):
            self.__browser_lib.click_button(constant.CONTINUE_TERMS_AND_CONDITIONS_POP_UP_CSS_SELECTOR)
        elif self.__browser_lib.is_element_visible(constant.ACCEPT_COOKIES_TRACKER_POPUP):
            self.__browser_lib.click_button(constant.ACCEPT_COOKIES_TRACKER_POPUP)
        else:
            pass

    def input_search_term_and_search(self):
        self.__browser_lib.click_button(constant.SEARCH_BUTTON_CSS_SELECTOR)
        self.__browser_lib.input_text(constant.SEARCH_TEXT_BOX_CSS_SELECTOR, self.search_term)
        self.__browser_lib.click_button(constant.GO_BUTTON_CSS_SELECTOR)

    def set_section(self):
        self.__browser_lib.wait_until_element_is_visible(constant.SECTION_DROPDOWN_CSS_SELECTOR)
        self.__browser_lib.click_button(constant.SECTION_DROPDOWN_CSS_SELECTOR)
        for category in self.news_categories:
            idx = constant.NEWS_CATEGORIES.index(category)
            self.__browser_lib.click_button(
                constant.SECTION_CHECKBOX_BASE_SELECTOR.format(list_number=idx + 1)
            )

    """
    number of months for which you need to receive news
    Example of how this should work:
    0 or 1 - only the current month,
    2 - current and previous month,
    3 - current and two previous months, and so on
    """

    def set_date_filter(self):
        self.__browser_lib.click_button(constant.DATE_RANGE_DROPDOWN_CSS_SELECTOR)
        # select custom date option from drop down
        self.__browser_lib.click_button(constant.DATE_RANGE_OPTIONS_BASE_SELECTOR.format(
            list_number=constant.CUSTOM_DATE_OPTION_INDEX
        ))
        # set start date
        self.__browser_lib.set_element_attribute(
            constant.START_DATE_CSS_SELECTOR, "value", self.start_date.strftime("%m/%d/%Y")
        )
        # set end date
        self.__browser_lib.set_element_attribute(
            constant.END_DATE_CSS_SELECTOR, "value", self.end_date.strftime("%m/%d/%Y")
        )

    def set_sorting_order(self):
        self.__browser_lib.select_from_list_by_label(
            constant.SORTING_ORDER_CSS_SELECTOR, "Sort by Newest"
        )

    def load_all_articles(self):
        if not self.__browser_lib.is_element_visible(constant.SHOW_MORE_BUTTON_CSS_SELECTOR):
            return
        while True:
            ordered_list_element = self.__browser_lib.find_element(
                constant.ALL_ARTICLES_ORDERED_LIST_CSS_SELECTOR
            )
            articles = ordered_list_element.find_elements(By.TAG_NAME, "li")
            last_article = ArticleInfo(articles[-1])
            if last_article.date() < self.start_date:
                break
            self.__browser_lib.click_button(constant.SHOW_MORE_BUTTON_CSS_SELECTOR)

    def fetch_articles(self):
        result = []
        ordered_list_element = self.__browser_lib.find_element(
            constant.ALL_ARTICLES_ORDERED_LIST_CSS_SELECTOR
        )
        for article_element in ordered_list_element.find_elements(By.TAG_NAME, "li"):
            article_info = ArticleInfo(article_element)
            if article_info.is_ad_banner():
                continue
            title = article_info.title()
            description = article_info.description()
            image_url = article_info.image_url()
            article_date = article_info.date()
            search_term_occurence_count = self.__count_occurence(title) + self.__count_occurence(description)
            contains_monetary_value = utils.contains_monetary_values(title) or utils.contains_monetary_values(title)

            record = {
                "title": title,
                "description": description,
                "article_date": article_date.strftime("%B %d, %Y"),
                "image_url": image_url,
                "image_path": utils.download_image(image_url,self.image_download_directory),
                "search_term_occurence_count": search_term_occurence_count,
                "contains_monetary_value": contains_monetary_value,
            }
            result.append(record)
        return result

    def __count_occurence(self, text: str):
        if text is None:
            return 0
        else:
            return text.lower().count(self.search_term.lower())

    def __calculate_date_range(self):
        self.end_date = datetime.now()
        prev_month = self.months - 1 if self.months > 2 else 0
        beginning_of_current_month = self.end_date - timedelta(days=(self.end_date.day) - 1)
        self.start_date = beginning_of_current_month - relativedelta(months=prev_month)