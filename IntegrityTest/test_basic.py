import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestBaiduSearch:
    """百度搜索完整性测试 - 15个测试用例（普通 Chrome + 防自动化配置）"""

    def setup_method(self):
        """每个测试方法执行前的准备工作 - 防自动化配置 + 防崩溃参数"""
        chrome_options = Options()

        # ---------- 防自动化检测参数 ----------
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36")

        # ---------- 解决 tab crashed 的关键参数 ----------
        chrome_options.add_argument('--no-sandbox')                     # 禁用沙盒模式
        chrome_options.add_argument('--disable-dev-shm-usage')         # 解决共享内存不足
        chrome_options.add_argument('--disable-gpu')                   # 禁用 GPU 硬件加速
        chrome_options.add_argument('--disable-software-rasterizer')   # 禁用软件光栅化
        chrome_options.add_argument('--disable-extensions')            # 禁用扩展
        chrome_options.add_argument('--disable-plugins')              # 禁用插件

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 20)

        # ---------- 执行 CDP 命令（隐藏 webdriver 特征） ----------
        try:
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
        except Exception as e:
            print(f"⚠️ CDP 命令执行失败（不影响核心功能）: {e}")

    def teardown_method(self):
        """每个测试方法执行后的清理工作"""
        try:
            self.driver.quit()
        except Exception:
            pass

    def _search(self, keyword):
        """执行搜索操作"""
        self.driver.get("https://www.baidu.com")
        time.sleep(2)

        # 尝试关闭可能出现的浮层
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

        # 定位搜索框并输入关键词
        search_box = self.wait.until(
            EC.element_to_be_clickable((By.ID, "kw"))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        time.sleep(0.5)
        search_box.send_keys(Keys.ENTER)

        # 等待搜索结果加载
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#content_left h3 a, h3 a"))
            )
        except Exception as e:
            with open(f"debug_{keyword}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"❌ 关键词 '{keyword}' 搜索超时，已保存 debug_{keyword}.html")
            raise e

        time.sleep(1)
        return self.driver.title

    # ==================== 15个测试用例 ====================

    def test_search_selenium(self):
        """1. 英文关键词：Selenium"""
        print("\n🧪 测试1: 搜索 'Selenium'")
        title = self._search("Selenium")
        assert "Selenium" in title
        print("✅ 测试通过")

    def test_search_python(self):
        """2. 英文关键词：Python"""
        print("\n🧪 测试2: 搜索 'Python'")
        title = self._search("Python")
        assert "Python" in title
        print("✅ 测试通过")

    def test_search_chinese(self):
        """3. 中文关键词：自动化测试"""
        print("\n🧪 测试3: 搜索 '自动化测试'")
        title = self._search("自动化测试")
        assert "自动化测试" in title
        print("✅ 测试通过")

    def test_search_mixed(self):
        """4. 中英混合：Selenium自动化测试"""
        print("\n🧪 测试4: 搜索 'Selenium自动化测试'")
        title = self._search("Selenium自动化测试")
        assert "Selenium" in title or "自动化" in title
        print("✅ 测试通过")

    def test_search_special_char(self):
        """5. 特殊字符：Selenium@2024"""
        print("\n🧪 测试5: 搜索 'Selenium@2024'")
        title = self._search("Selenium@2024")
        assert "Selenium" in title or "2024" in title
        print("✅ 测试通过")

    def test_search_long_keyword(self):
        """6. 长关键词（30个字符）"""
        print("\n🧪 测试6: 搜索长关键词")
        long_keyword = "这是一个非常长的搜索关键词测试百度搜索的稳定性"
        title = self._search(long_keyword)
        assert "百度" in title or "搜索" in title
        print("✅ 测试通过")

    def test_search_short_keyword(self):
        """7. 短关键词：AI"""
        print("\n🧪 测试7: 搜索 'AI'")
        title = self._search("AI")
        assert "AI" in title or "人工智能" in title
        print("✅ 测试通过")

    def test_search_number(self):
        """8. 纯数字：2024"""
        print("\n🧪 测试8: 搜索 '2024'")
        title = self._search("2024")
        assert "2024" in title
        print("✅ 测试通过")

    def test_search_url(self):
        """9. URL格式：github.com"""
        print("\n🧪 测试9: 搜索 'github.com'")
        title = self._search("github.com")
        assert "github" in title.lower() or "GitHub" in title
        print("✅ 测试通过")

    def test_search_empty(self):
        """10. 空搜索（直接点击搜索）"""
        print("\n🧪 测试10: 空搜索")
        self.driver.get("https://www.baidu.com")
        time.sleep(2)
        search_button = self.wait.until(EC.element_to_be_clickable((By.ID, "su")))
        search_button.click()
        time.sleep(2)
        assert "百度" in self.driver.title
        print("✅ 测试通过")

    def test_search_reset(self):
        """11. 输入后清除再输入新词"""
        print("\n🧪 测试11: 清除后重新搜索")
        self.driver.get("https://www.baidu.com")
        time.sleep(2)
        search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "kw")))
        search_box.send_keys("清空测试")
        search_box.clear()
        search_box.send_keys("Selenium")
        search_box.send_keys(Keys.ENTER)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content_left h3 a, h3 a")))
        assert "Selenium" in self.driver.title
        print("✅ 测试通过")

    def test_search_twice(self):
        """12. 连续搜索两次"""
        print("\n🧪 测试12: 连续搜索两次")
        title1 = self._search("Python")
        assert "Python" in title1

        search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "kw")))
        search_box.clear()
        search_box.send_keys("Java")
        search_box.send_keys(Keys.ENTER)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content_left h3 a, h3 a")))
        assert "Java" in self.driver.title or "Java" in self.driver.page_source
        print("✅ 测试通过")

    def test_search_enter_key(self):
        """13. 只用回车键（不点按钮）"""
        print("\n🧪 测试13: 回车键搜索")
        self.driver.get("https://www.baidu.com")
        time.sleep(2)
        search_box = self.wait.until(EC.element_to_be_clickable((By.ID, "kw")))
        search_box.send_keys("GitHub")
        search_box.send_keys(Keys.ENTER)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content_left h3 a, h3 a")))
        assert "GitHub" in self.driver.title
        print("✅ 测试通过")

    def test_search_case_sensitive(self):
        """14. 大小写不敏感测试：selenium"""
        print("\n🧪 测试14: 小写 'selenium'")
        title = self._search("selenium")
        assert "Selenium" in title or "selenium" in title.lower()
        print("✅ 测试通过")

    def test_search_special_character_only(self):
        """15. 纯特殊符号：@#"""
        print("\n🧪 测试15: 纯特殊符号 '@#'")
        title = self._search("@#")
        assert "百度" in title
        print("✅ 测试通过")