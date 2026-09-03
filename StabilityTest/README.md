# 稳定性测试

## 前置条件

* 测试浏览器：Google Chrome
* 测试框架：Selenium

## 大致框架结构

```
selenium_tests/
│
├── test_basic.py          # 基础功能测试
├── test_login.py          # 登录功能测试
├── test_stability.py      # 稳定性测试
├── test_stress.py         # 并发/压力测试
│
├── screenshots/           # 测试失败截图
│
├── logs/                  # 测试运行日志
│
└── requirements.txt       # Python依赖列表
```

## 依赖列表

* selenium
* pytest
* pytest-xdist

## 安排规划

#### 2026.8.26-2026.8.27

* 完成依赖列表、简述结构、用例
