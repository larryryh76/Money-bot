class BaseParser:
    def find_offers(self, driver):
        raise NotImplementedError

    def do_task(self, driver, offer):
        raise NotImplementedError
