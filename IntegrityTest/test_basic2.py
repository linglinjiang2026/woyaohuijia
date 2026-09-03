import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class TestBaiduSearch:
    """百度搜索核心流程测试 - 模拟真实用户"""

    def setup_method(self):
        """每个测试方法执行前的准备工作 - 带防自动化配置"""
        # 🆕 关键：添加 Chrome Options 防自动化检测
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
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

    def _search(self, keyword):
        """
        执行搜索操作 - 使用 send_keys + Keys.ENTER 触发真实事件
        """
        # 访问百度
        self.driver.get("https://www.baidu.com")
        time.sleep(2)

        # 关闭浮层
        self._close_popup_if_exists()

        # 定位搜索框并输入关键词（触发真实输入事件）
        search_box = self.wait.until(
            EC.element_to_be_clickable((By.ID, "kw"))
        )
        search_box.clear()
        search_box.send_keys(keyword)
        print(f"✅ 输入关键词: {keyword}")
        time.sleep(0.5)

        # 使用回车键提交搜索（模拟真实用户行为）
        search_box.send_keys(Keys.ENTER)
        print("✅ 按回车键提交搜索")

        # 备用：如果回车无效，再尝试点击搜索按钮
        try:
            search_button = self.driver.find_element(By.ID, "su")
            if search_button.is_displayed() and search_button.is_enabled():
                search_button.click()
                print("✅ 补充点击搜索按钮")
        except Exception:
            pass

        # 等待搜索结果 - 使用更宽泛的选择器
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#content_left h3 a, h3 a"))
            )
        except Exception as e:
            # 如果等待超时，保存页面源码用于调试
            with open("debug.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"❌ 搜索结果加载超时，已保存页面源码到 debug.html")
            print(f"📄 当前页面标题: {self.driver.title}")
            raise e

        time.sleep(1)
        return self.driver.title

    def test_baidu_search(self):
        """核心测试：搜索 'Selenium'"""
        print("\n🌐 正在访问百度首页...")
        title = self._search("Selenium")

        # 检查是否进入安全验证页面
        if "验证" in title or "安全" in title:
            raise AssertionError(f"❌ 触发百度安全验证，页面标题: {title}")

        assert "Selenium" in title, f"标题中未找到 'Selenium'，实际标题：{title}"
        print("🎉 测试通过！百度搜索功能完整可用")

    def test_baidu_search_alternative(self):
        """备用测试：搜索 'Python'"""
        print("\n🌐 正在访问百度首页（备用测试）...")
        title = self._search("Python")

        if "验证" in title or "安全" in title:
            raise AssertionError(f"❌ 触发百度安全验证，页面标题: {title}")

        assert "Python" in title, f"标题中未找到 'Python'，实际标题：{title}"
        print("🎉 备用测试通过！")