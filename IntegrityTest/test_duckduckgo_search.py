import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class TestDuckDuckGoSearch:


    @classmethod
    def setup_class(cls):

        options = Options()

        options.add_argument(
            "--disable-dev-shm-usage"
        )

        options.add_argument(
            "--no-sandbox"
        )


        cls.driver = webdriver.Chrome(
            options=options
        )


        cls.driver.maximize_window()


        cls.wait = WebDriverWait(
            cls.driver,
            20
        )



    @classmethod
    def teardown_class(cls):

        cls.driver.quit()



    def open_page(self):

        self.driver.get(
            "https://duckduckgo.com/"
        )


        time.sleep(3)


        print(
            "当前地址:",
            self.driver.current_url
        )

        print(
            "标题:",
            self.driver.title
        )



    def get_search_box(self):

        """
        自动寻找真正搜索框
        """

        selectors = [

            (By.ID, "searchbox_input"),

            (By.NAME, "q"),

            (By.CSS_SELECTOR,
             "input[type='text']"),

            (By.CSS_SELECTOR,
             "textarea")

        ]


        for by,value in selectors:


            try:

                boxes = self.driver.find_elements(
                    by,
                    value
                )


                for box in boxes:


                    if box.is_displayed() and box.is_enabled():

                        print(
                            "找到搜索框:",
                            value
                        )

                        return box


            except Exception:

                pass



        # 保存现场
        self.driver.save_screenshot(
            "search_error.png"
        )


        with open(
                "error.html",
                "w",
                encoding="utf-8"
        ) as f:

            f.write(
                self.driver.page_source
            )


        raise Exception(
            "没有找到可用搜索框"
        )



    def search(self, keyword):


        self.open_page()


        box = self.get_search_box()


        box.click()


        box.clear()


        box.send_keys(
            keyword
        )


        print(
            "输入:",
            keyword
        )


        box.send_keys(
            Keys.ENTER
        )


        time.sleep(5)


        return self.driver.page_source



    def test_search_selenium(self):

        html = self.search(
            "Selenium"
        )


        assert (
                "Selenium"
                in
                html
        )



    def test_search_python(self):

        html = self.search(
            "Python"
        )


        assert (
                "Python"
                in
                html
        )



    def test_search_chinese(self):

        html = self.search(
            "自动化测试"
        )


        assert (
                "自动化"
                in
                html
        )



    def test_search_github(self):

        html = self.search(
            "github.com"
        )


        assert (
                "github"
                in
                html.lower()
        )



    def test_search_number(self):

        html = self.search(
            "2024"
        )


        assert (
                "2024"
                in
                html
        )