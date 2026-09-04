import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class TestBaiduSearch:
    """
    百度搜索完整性测试
    15个测试用例
    """

    @classmethod
    def setup_class(cls):

        options = Options()

        # Chrome稳定参数
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")


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



    def open_baidu(self):

        """
        打开百度首页
        """

        self.driver.get(
            "https://www.baidu.com"
        )

        time.sleep(2)


        print(
            "当前标题:",
            self.driver.title
        )


    def get_search_box(self):

        """
        获取百度搜索框
        """

        box = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "kw"
                )
            )
        )

        return box



    def search(self, keyword):

        """
        执行搜索
        """

        self.open_baidu()


        box = self.get_search_box()


        # 使用JS保证输入
        self.driver.execute_script(
            """
            arguments[0].focus();
            arguments[0].value=arguments[1];

            arguments[0].dispatchEvent(
                new Event(
                    'input',
                    {
                        bubbles:true
                    }
                )
            );
            """,
            box,
            keyword
        )


        box.send_keys(
            Keys.ENTER
        )


        time.sleep(3)


        return self.driver.page_source



    # ===============================
    # 1. 英文搜索
    # ===============================

    def test_search_selenium(self):

        html = self.search(
            "Selenium"
        )

        assert "Selenium" in html



    # ===============================
    # 2. Python搜索
    # ===============================

    def test_search_python(self):

        html = self.search(
            "Python"
        )

        assert "Python" in html



    # ===============================
    # 3. 中文搜索
    # ===============================

    def test_search_chinese(self):

        html = self.search(
            "自动化测试"
        )

        assert "自动化" in html



    # ===============================
    # 4. 中英混合
    # ===============================

    def test_search_mix(self):

        html = self.search(
            "Selenium自动化测试"
        )

        assert (
                "Selenium" in html
                or
                "自动化" in html
        )



    # ===============================
    # 5. 特殊字符
    # ===============================

    def test_search_special(self):

        html = self.search(
            "Selenium@2024"
        )

        assert "Selenium" in html



    # ===============================
    # 6. 长关键词
    # ===============================

    def test_search_long(self):

        html = self.search(
            "这是一个非常长的搜索关键词测试百度搜索稳定性"
        )

        assert "百度" in html



    # ===============================
    # 7. 短关键词
    # ===============================

    def test_search_short(self):

        html = self.search(
            "AI"
        )

        assert (
                "AI" in html
                or
                "人工智能" in html
        )



    # ===============================
    # 8. 数字搜索
    # ===============================

    def test_search_number(self):

        html = self.search(
            "2024"
        )

        assert "2024" in html



    # ===============================
    # 9. URL搜索
    # ===============================

    def test_search_url(self):

        html = self.search(
            "github.com"
        )

        assert "github" in html.lower()



    # ===============================
    # 10. 空搜索
    # ===============================

    def test_empty_search(self):

        self.open_baidu()


        btn = self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "su"
                )
            )
        )


        btn.click()


        time.sleep(2)


        assert "百度" in self.driver.title



    # ===============================
    # 11. 清空重新输入
    # ===============================

    def test_clear_input(self):

        self.open_baidu()


        box = self.get_search_box()


        box.clear()


        box.send_keys(
            "Selenium"
        )


        box.send_keys(
            Keys.ENTER
        )


        time.sleep(3)


        assert "Selenium" in self.driver.page_source



    # ===============================
    # 12. 连续搜索
    # ===============================

    def test_twice_search(self):

        self.search(
            "Python"
        )


        self.search(
            "Java"
        )


        assert "Java" in self.driver.page_source



    # ===============================
    # 13. 回车搜索
    # ===============================

    def test_enter_search(self):

        self.open_baidu()


        box = self.get_search_box()


        box.send_keys(
            "GitHub"
        )


        box.send_keys(
            Keys.ENTER
        )


        time.sleep(3)


        assert "GitHub" in self.driver.page_source



    # ===============================
    # 14. 大小写
    # ===============================

    def test_case(self):

        html = self.search(
            "selenium"
        )


        assert "selenium" in html.lower()



    # ===============================
    # 15. 特殊符号
    # ===============================

    def test_special_symbol(self):

        html = self.search(
            "@#"
        )


        assert "百度" in html