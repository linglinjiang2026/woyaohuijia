import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestBaiduSearch:
    """百度搜索基础功能测试 - 模拟真实用户"""

    def setup_method(self):
        """每个测试方法执行前的准备工作"""
        # 🆕 关键：添加浏览器选项，模拟真实用户
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 隐藏自动化特征
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 去掉"Chrome正在受自动测试软件控制"提示
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 添加用户代理，模拟真实浏览器
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)

        # 🆕 执行 CDP 命令，进一步隐藏自动化特征
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['zh-CN', 'zh']
                });
            """
        })

    def teardown_method(self):
        """每个测试方法执行后的清理工作"""
        self.driver.quit()

    def _close_popup_if_exists(self):
        """尝试关闭百度首页可能出现的浮层广告"""
        close_selectors = [
            "//*[@id='s-top-loginbtn']/following-sibling::a",
            "//*[@class='close-btn']",
            "//*[contains(@class, 'close')]",
            "//*[@id='s-bottom-layer-close']"
        ]
        for selector in close_selectors:
            try:
                close_btn = self.driver.find_element(By.XPATH, selector)
                if close_btn.is_displayed() and close_btn.is_enabled():
                    close_btn.click()
                    time.sleep(0.5)
                    break
            except Exception:
                continue

    def _find_search_box(self):
        """使用多种方式尝试定位百度搜索框"""
        locators = [
            (By.ID, "kw"),
            (By.NAME, "wd"),
            (By.CSS_SELECTOR, "input[name='wd']"),
            (By.XPATH, "//input[@id='kw']"),
            (By.XPATH, "//input[@type='text']"),
            (By.CSS_SELECTOR, "input#kw"),
        ]
        for by, value in locators:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located((by, value))
                )
                if element.is_displayed() and element.is_enabled():
                    return element
            except Exception:
                continue
        # 定位失败，保存页面源码
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        raise Exception("无法定位百度搜索框，已保存页面源码到 debug.html")

    def test_search_selenium(self):
        """测试搜索关键词 'Selenium'"""
        print("\n🌐 正在访问百度首页...")
        self.driver.get("https://www.baidu.com")
        time.sleep(3)

        self._close_popup_if_exists()

        print("🔍 正在定位搜索框...")
        search_box = self._find_search_box()

        print("✍️ 正在输入关键词...")
        search_box.clear()
        search_box.send_keys("Selenium")

        print("🖱️ 正在点击搜索按钮...")
        search_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "su"))
        )
        search_button.click()

        print("⏳ 等待搜索结果...")
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(@class, 't')]/a"))
        )

        assert "Selenium" in self.driver.title
        print("✅ 测试通过！")

    def test_search_python(self):
        """测试搜索关键词 'Python'"""
        print("\n🌐 正在访问百度首页...")
        self.driver.get("https://www.baidu.com")
        time.sleep(3)

        self._close_popup_if_exists()

        print("🔍 正在定位搜索框...")
        search_box = self._find_search_box()

        print("✍️ 正在输入关键词...")
        search_box.clear()
        search_box.send_keys("Python")

        print("🖱️ 正在点击搜索按钮...")
        search_button = self.wait.until(
            EC.element_to_be_clickable((By.ID, "su"))
        )
        search_button.click()

        print("⏳ 等待搜索结果...")
        self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//h3[contains(@class, 't')]/a"))
        )

        assert "Python" in self.driver.title
        print("✅ 测试通过！")