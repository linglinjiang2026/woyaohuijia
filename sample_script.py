from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://cn.bing.com/")

wait = WebDriverWait(driver,15)
search = wait.until(EC.element_to_be_clickable((By.NAME,"q")))
search.send_keys("Dress")
search.send_keys(Keys.ENTER)

wait.until(lambda d:"dress" in d.current_url.lower())
print("Test Passed")

sleep(10)   # 停留10秒，你可以观察搜索结果页面

driver.quit()
