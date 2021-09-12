from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
import logging

logger = logging.getLogger("gunicorn.error")


def bootstrap_chrome(headless=True, max_window=True):
    mobileEmulation = {"deviceName": "iPhone X"}
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")  # 谷歌文档提到需要加上这个属性来规避bug
    if headless:
        options.add_argument("headless")
    options.add_argument("--no-sandbox")  # do not remove it !
    options.add_argument("blink-settings=imagesEnabled=false")  # 不加载图片, 提升速度
    options.add_experimental_option("mobileEmulation", mobileEmulation)
    # start chrome and maximize window
    driver = webdriver.Chrome(chrome_options=options)
    if max_window:
        driver.maximize_window()
    return driver


def login(student, driver=None):
    stuid = student["stuid"]
    stupwd = student["password"]
    if stuid == "" and stupwd == "":
        # print("没有设置教务处用户名和密码")
        return False
    if not driver:
        driver = bootstrap_chrome()  # TODO 上线时改为无头
    driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/sj.asp")
    try:
        username_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "txtId"))
        )
        username_input.send_keys(stuid)

        password_input = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, "txtMM"))
        )

        password_input.send_keys(stupwd)
        password_input.send_keys(Keys.ENTER)
        return driver
    except Exception as e:
        logger.warn(f"{stuid},登录发生了错误")
        logger.warn(e)
        driver.quit()
        return None
