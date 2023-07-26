# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from nytimes_crawler import NytimesCrawler
from rpa_work_item_getter import RpaWorkItemGetter
import utils
import pdb

if __name__ == '__main__':
    try:
        ######## uncomment following lines if you want to use RPA WorkItem Getter to get value of variables
        # rpa_work_item_getter = RpaWorkItemGetter()
        # search_phrase = rpa_work_item_getter.search_phrase()
        # news_categories = rpa_work_item_getter.news_categories()
        # months = rpa_work_item_getter.months()

        ###### TESTING IN LOCAL
        search_phrase = "Messi"
        news_categories = ["Sports", "World"]
        months = 2
        output_directory = 'output'
        file_name = 'nytimes.csv'
        nytimes_crawler = NytimesCrawler(search_phrase, news_categories, months, output_directory, file_name)
        nytimes_crawler.run()
        # utils.write_to_csv(article_infos, output_directory, file_name)
        # to use Excel Writer uncommnet following line
        # utils.write_to_csv(article_infos, output_directory, file_name)
        print(f"Search Records put into CSV file #{file_name}. Images are downloaded in directory #{output_directory} ")
    finally:
        print("Crawler Run Complete")