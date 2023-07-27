from RPA.Robocorp.WorkItems import WorkItems

class RpaWorkItemGetter:

    def __init__(self):
        self.__work_item = WorkItems()

    def search_phrase(self):
        return self.__get_rpa_variable("search_phrase")

    def news_categories(self):
        categories = self.__get_rpa_variable("news_category")
        news_categories = [category.strip() for category in categories.split(',')]
        return news_categories

    def months(self):
        return int(self.__get_rpa_variable("no_of_month"))

    def __get_rpa_variable(self, var_name):
        # self.__work_item.get_input_work_item()
        return self.__work_item.get_work_item_variable(var_name)
