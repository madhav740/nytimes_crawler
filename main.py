from nytimes_crawler import NytimesCrawler
from rpa_work_item_getter import RpaWorkItemGetter
import utils


if __name__ == '__main__':
    try:
        output_dir = 'output'
        file_name = "nytimes"
        # rpa_work_item_getter = RpaWorkItemGetter()
        # search_phrase = rpa_work_item_getter.search_phrase()
        # news_categories = rpa_work_item_getter.news_categories()
        # months = rpa_work_item_getter.months()
        # nytimes_crawler = NytimesCrawler(search_phrase, news_categories, months, output_dir)
        #     crawler.run(search_phrase, news_categories, months)
        nytimes_crawler = NytimesCrawler("Messi", ["Sports","World"], 2, output_dir)
        article_infos = nytimes_crawler.run()
        if len(article_infos) > 0 :
            print(f"#{len(article_infos)} Search Records put into Excel file #{file_name}. Images are downloaded in directory #{output_dir} ")
            utils.write_to_excel(article_infos, output_dir, file_name, "result")
        else:
            print("No Records found. Skipping writing to Excel")
    except Exception as e:
        raise e
    finally:
        print("Crawler Run Complete")