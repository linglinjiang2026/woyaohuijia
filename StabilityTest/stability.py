import os
import time
import json
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

import config


os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
os.makedirs(config.LOG_DIR, exist_ok=True)
os.makedirs(config.RESULT_DIR, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_file = os.path.join(
    config.LOG_DIR,
    f"stability_{timestamp}.log"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(
            log_file,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)

def create_driver():

    if config.BROWSER.lower() == "chrome":

        options = Options()

        if config.HEADLESS:
            options.add_argument("--headless=new")

        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")

        driver = webdriver.Chrome(
            options=options
        )

    else:
        raise ValueError(
            f"暂不支持的浏览器: {config.BROWSER}"
        )

    driver.set_page_load_timeout(
        config.PAGE_LOAD_TIMEOUT
    )

    return driver

def run_test_case(driver):

    """
    这里是单次测试流程。

    后续由其他人的功能测试步骤替换或填入。
    现在先使用简单测试：
    打开网址 → 检查页面是否正常加载
    """

    driver.get(config.TEST_URL)

    # 判断页面是否成功加载
    assert driver.title != "", "页面标题为空"

    return True

def save_screenshot(driver, test_number):

    filename = (
        f"fail_{test_number}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    )

    path = os.path.join(
        config.SCREENSHOT_DIR,
        filename
    )

    try:
        driver.save_screenshot(path)

        logging.info(
            f"失败截图已保存: {path}"
        )

        return path

    except Exception as e:

        logging.error(
            f"截图保存失败: {e}"
        )

        return None

def should_continue(
    test_count,
    start_time
):

    if config.TEST_MODE == "count":

        return test_count < config.TEST_COUNT

    elif config.TEST_MODE == "duration":

        elapsed = time.time() - start_time

        return elapsed < config.TEST_DURATION

    else:

        raise ValueError(
            f"未知测试模式: {config.TEST_MODE}"
        )

def run_stability_test():

    start_time = time.time()

    total = 0
    success = 0
    failed = 0

    consecutive_failures = 0

    execution_times = []

    errors = []

    logging.info("=" * 50)
    logging.info("稳定性测试开始")
    logging.info(f"测试模式: {config.TEST_MODE}")
    logging.info(f"目标地址: {config.TEST_URL}")

    if config.TEST_MODE == "count":

        logging.info(
            f"计划执行次数: {config.TEST_COUNT}"
        )

    elif config.TEST_MODE == "duration":

        logging.info(
            f"计划运行时间: "
            f"{config.TEST_DURATION} 秒"
        )

    logging.info("=" * 50)

    while should_continue(
        total,
        start_time
    ):

        total += 1

        driver = None

        test_start = time.time()

        logging.info(
            f"开始第 {total} 次测试"
        )

        try:

            # 启动浏览器
            driver = create_driver()

            # 执行单次测试
            run_test_case(driver)

            cost = time.time() - test_start

            execution_times.append(cost)

            success += 1

            consecutive_failures = 0

            logging.info(
                f"第 {total} 次成功 | "
                f"耗时: {cost:.2f} 秒"
            )


        except Exception as e:

            cost = time.time() - test_start

            failed += 1

            consecutive_failures += 1

            error_message = (
                f"{type(e).__name__}: {str(e)}"
            )

            logging.error(
                f"第 {total} 次失败 | "
                f"耗时: {cost:.2f} 秒 | "
                f"错误: {error_message}"
            )

            screenshot = None

            if driver:

                screenshot = save_screenshot(
                    driver,
                    total
                )

            errors.append({
                "test_number": total,
                "error_type": type(e).__name__,
                "error": str(e),
                "duration": round(cost, 2),
                "screenshot": screenshot
            })

            if (
                consecutive_failures
                >= config.MAX_CONSECUTIVE_FAILURES
            ):

                logging.error(
                    f"连续失败 "
                    f"{consecutive_failures} 次，"
                    f"测试停止"
                )

                break

            if not config.CONTINUE_ON_FAILURE:

                logging.error(
                    "测试失败，配置要求停止"
                )

                break

        finally:

            # 无论成功还是失败
            # 都关闭浏览器
            if driver:

                try:
                    driver.quit()

                except WebDriverException as e:

                    logging.error(
                        f"关闭浏览器失败: {e}"
                    )

        if (
            config.LOOP_INTERVAL > 0
            and should_continue(
                total,
                start_time
            )
        ):

            time.sleep(
                config.LOOP_INTERVAL
            )

    total_duration = (
        time.time() - start_time
    )

    success_rate = (
        success / total * 100
        if total > 0
        else 0
    )


    result = {
        "test_start": datetime.fromtimestamp(
            start_time
        ).strftime("%Y-%m-%d %H:%M:%S"),

        "test_mode": config.TEST_MODE,

        "total_tests": total,

        "success": success,

        "failed": failed,

        "success_rate": round(
            success_rate,
            2
        ),

        "total_duration_seconds": round(
            total_duration,
            2
        ),

        "average_execution_time": round(
            sum(execution_times)
            / len(execution_times),
            2
        )
        if execution_times
        else 0,

        "max_execution_time": round(
            max(execution_times),
            2
        )
        if execution_times
        else 0,

        "min_execution_time": round(
            min(execution_times),
            2
        )
        if execution_times
        else 0,

        "errors": errors
    }

    result_file = os.path.join(
        config.RESULT_DIR,
        f"result_{timestamp}.json"
    )

    with open(
        result_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    logging.info("=" * 50)
    logging.info("稳定性测试结束")
    logging.info(f"总测试次数: {total}")
    logging.info(f"成功次数: {success}")
    logging.info(f"失败次数: {failed}")
    logging.info(
        f"成功率: {success_rate:.2f}%"
    )
    logging.info(
        f"总运行时间: "
        f"{total_duration:.2f} 秒"
    )

    if execution_times:

        logging.info(
            f"平均成功耗时: "
            f"{result['average_execution_time']:.2f} 秒"
        )

        logging.info(
            f"最长成功耗时: "
            f"{result['max_execution_time']:.2f} 秒"
        )

        logging.info(
            f"最短成功耗时: "
            f"{result['min_execution_time']:.2f} 秒"
        )

    logging.info(
        f"结果文件: {result_file}"
    )

    logging.info("=" * 50)

if __name__ == "__main__":

    run_stability_test()