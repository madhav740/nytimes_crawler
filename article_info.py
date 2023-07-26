import constant
from selenium.webdriver.common.by import By
from datetime import datetime
class ArticleInfo:

    def __init__(self, article_element):
        self.article_element = article_element

    def title(self):
        return self.article_element.find_element(By.TAG_NAME, "h4").text

    def description(self):
        return self.article_element.find_element(
            By.CLASS_NAME, constant.ARTICLE_DESCRIPTION_CLASS_NAME
        ).text

    def date(self):
        article_date = self.article_element.find_element(By.TAG_NAME, "span").text
        article_date =  f"{article_date}, 2023" if "," not in article_date else article_date
        return datetime.strptime(article_date, "%B %d, %Y")

    def image_url(self):
        img_element = self.article_element.find_element(By.TAG_NAME, "img")
        return img_element.get_attribute("src")

    def is_ad_banner(self):
        return self.article_element.get_attribute("class") == constant.AD_BANNER_CSS_CLASS