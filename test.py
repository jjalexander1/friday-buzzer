import time


class Tst(object):
    def __init__(self):
        self.itemlist = []

    def add_item_to_list(self, item):
        self.itemlist.append(item)
        self.process()

    def process(self):
        time.sleep(2)
        self.itemlist = sorted(self.itemlist)
        print(self.itemlist)


if __name__ == '__main__':
    t = Tst()

    t.add_item_to_list(25)
    t.add_item_to_list(13)
    t.add_item_to_list(14345253)