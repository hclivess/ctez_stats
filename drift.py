import tornado.ioloop
import tornado.web
import drift_collector
import threading
import time
import json
from datetime import datetime


def reduce(whole, reduce_to=1000):
    """reduce number of entries in list by skipping"""
    reducer = int(len(whole) / reduce_to)
    reduced = whole[::reducer]
    return reduced


def to_ts(date_strings):
    timestamps = []
    for key in date_strings:
        timestamp = datetime.timestamp(datetime.strptime(key, "%Y-%m-%d %H:%M:%S+00:00"))
        timestamps.append(int(timestamp))
    return timestamps


class AllHandler(tornado.web.RequestHandler):
    def get(self, data):
        chart = AllHandler.get_argument(self, "chart")

        input_dict = drift_collector.read_input()["data"]

        values_full = []

        for key in input_dict.keys():
            values_full.append(input_dict[key][chart])

        labels_full = input_dict.keys()

        values = reduce(list(values_full))
        labels = reduce(list(labels_full))

        self.render("chart.html",
                    labels=json.dumps(labels),
                    values=json.dumps(values),
                    title=chart
                    )


class RecentHandler(tornado.web.RequestHandler):
    def get(self, data):
        chart = RecentHandler.get_argument(self, "chart")

        input_dict = drift_collector.read_input()

        block_max = input_dict["stats"]["last_block"]
        block_min = block_max - 1000
        block_range = list(range(block_min, block_max + 1))  # +1 to include in range

        value_list = []
        for key, value in input_dict["data"].items():
            if block_min <= int(key) <= block_max:
                value_list.append(value[chart])

        self.render("chart.html",
                    labels=json.dumps(block_range),
                    values=json.dumps(value_list),
                    title=chart
                    )


class ApiHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(drift_collector.read_input())

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("dashboard.html")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api", ApiHandler),
        (r"/all(.*)", AllHandler),
        (r"/recent(.*)", RecentHandler),
        (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
    ])


class ThreadedClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            drift_collector.collect(block_last=drift_collector.block_last_get(),
                                    block_start=drift_collector.block_start_get())
            print("Sleeping...")
            time.sleep(10)


if __name__ == "__main__":
    background = ThreadedClient()
    background.start()
    print("Background process started")

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
