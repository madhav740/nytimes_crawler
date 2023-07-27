from RPA.Robocorp.WorkItems import WorkItems

class RpaWorkItemGetter:

    def __init__(self):
        work_item = WorkItems()
        work_item.get_input_work_item()
        self.input_wi = work_item.get_work_item_variables()
        print(self.input_wi)

    def search_phrase(self):
        return self.input_wi["search_phrase"]

    def news_categories(self):
        categories = self.input_wi["news_category"]
        news_categories = [category.strip() for category in categories.split(',')]
        return news_categories

    def months(self):
        return int(self.input_wi["no_of_month"])