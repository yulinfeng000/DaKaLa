import logging
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.service._util import login

logger = logging.getLogger("gunicorn.error")
PIC_LOCATION = os.path.abspath("./data/pic")


def get_photo(student):
    try:
        driver = login(student)
        driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y")
        newset_a = driver.find_element_by_xpath(
            "/html/body/div[2]/table/tbody[2]/tr[2]/td[2]/a"
        )
        newset_a.click()
        vc_image_path = os.path.abspath(f"{PIC_LOCATION}/{student['stuid']}_img.png")
        form_body = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "wjTA"))
        )
        form_body.screenshot(vc_image_path)
        return vc_image_path
    except Exception as e:
        logger.warn(e)
        logger.warn("刷新打卡截图发生了错误")
    finally:
        driver.quit()
