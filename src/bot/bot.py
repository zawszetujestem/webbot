import time
from queue import Queue
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pprint import pprint as pp

from threading import Thread, Lock


class Bot:
    def __init__(self):
        self.res_queue = Queue()
        self.size = 0

    def get_data(self, link_queue, size_lock):
        while not link_queue.empty():
            url = link_queue.get(block=False)
            with urlopen(url) as r:
                bs = BeautifulSoup(r.read(), 'html.parser')
                res = bs.select('a[href*="tvn24"]:not([href^="mailto"])')
                res = {re.get('href') for re in res if not re.get('href').endswith('/')}

            link_queue.task_done()
            self.res_queue.put(res)

            with size_lock:
                self.size += 1

    def manage_threads(self, url, levels=1):
        start_queue = Queue()
        size_lock = Lock()
        start_queue.put(url)
        self.get_data(start_queue, size_lock)

        start = time.perf_counter()
        # TODO create method for multiply run this code
        # TODO add comments(docstring), DRY, KISS, pylint
        for _ in range(levels):
            pp(f'g_data {self.size}')
            link_queue = Queue()

            for urls in self.res_queue.get():
                link_queue.put(urls)

            num_thread = 10
            for _ in range(num_thread):
                t = Thread(target=self.get_data, args=(link_queue, size_lock))
                t.start()

            link_queue.join()

        l_result = []
        for _ in range(self.res_queue.qsize()):
            l_result.append(len(self.res_queue.get()))

        print(sum(l_result))

        end = time.perf_counter()

        print(f'Time {end - start}')
        pp(f'd_data {self.size}')

    def manage_without_threads(self, url):
        start_queue = Queue()
        start_queue.put(url)
        self.get_data(start_queue)

        start = time.perf_counter()
        link_queue = Queue()

        for urls in self.res_queue.get():
            link_queue.put(urls)

        l_result = []
        for _ in range(self.res_queue.qsize()):
            l_result.append(len(self.res_queue.get()))

        print(sum(l_result))

        end = time.perf_counter()

        print(f'Time {end - start}')


if __name__ == '__main__':
    g = Bot()
    g.manage_threads('https://www.tvn24.pl')

