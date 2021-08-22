import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from app.service._util import bootstrap_chrome

from app import userdb

logger = logging.getLogger("gunicorn.error")


def _login(student):
    stuid = student["stuid"]
    stupwd = student["password"]

    if stuid == "" and stupwd == "":
        # print("没有设置教务处用户名和密码")
        return False

    driver = bootstrap_chrome(headless=False)  # TODO 上线时改为无头
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
    except:
        logger.warn(f"{stuid},获得打卡记录时登录发生了错误")
        driver.quit()
        return None


def _get_records(driver: WebDriver):
    driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y")
    records = driver.find_elements_by_xpath("/html/body/div[2]/table/tbody[2]/tr")
    rlist = []
    for r in records:
        r: WebElement
        tds = r.find_elements_by_tag_name("td")
        if len(tds) > 2:
            if "疫" in tds[1].text:
                rlist.append((tds[0].text, tds[1].text))
    return rlist


def dkrecords(student):
    logger.info(f"{student['stuid']} 执行了打卡记录刷新")
    try:
        driver = _login(student)
        if not driver:
            return None
        records = _get_records(driver)
        count = 0
        for r in records:
            if r[0] != ' ':
                count += 1
            else:
                break
    finally:
        driver.quit()
    logger.info(f"{student['stuid']},连续打卡 count={count}")
    userdb.db_put_user_daka_combo(student["stuid"], count)
    userdb.db_put_user_daka_records(student["stuid"], records)
