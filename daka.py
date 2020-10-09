from datetime import datetime
import time
import userdb
from selenium import webdriver
from selenium.common.exceptions import \
    NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException, InvalidSelectorException, \
    InvalidElementStateException
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

DAKA_URL = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/editSj.asp?UTp=Xs&Tx=33_1&ObjId="
logger = logging.getLogger(__file__)


def dakala(student, config:dict):
    # print(student, config)
    STU_ID = student['stuid']
    STU_PASSWD = student['password']

    if STU_ID == "" and STU_PASSWD == "":
        # print("没有设置教务处用户名和密码")
        return False

    mobileEmulation = {'deviceName': 'iPhone X'}
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    options.add_argument('headless')
    # options.add_argument('--no-sandbox')
    options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    options.add_experimental_option('mobileEmulation', mobileEmulation)
    # start chrome and maximize window
    driver = webdriver.Chrome(chrome_options=options)

    driver.maximize_window()

    # go to login page
    driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/sj.asp")
    # time.sleep(1)

    try:
        # find input element

        username_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "txtId"))
        )
        username_input.send_keys(STU_ID)

        password_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "txtMM"))
        )

        password_input.send_keys(STU_PASSWD)
        login_submit_btn = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "IbtnEnter"))
        )
        login_submit_btn.click()

        
        driver.get(
            "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y")
        # time.sleep(1)
        # n = driver.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
        # print('当前句柄: ', n)  # 会打印所有的句柄
        # driver.switch_to.window(n[-1])
        # time.sleep(12)
        linkList = driver.find_elements_by_tag_name("a")
        # gen_log.warning(linkList[1].get_attribute('href'))

        linkList[0].click()

        # new feature
        # auto application in-out school

        if config.get('application_start_day') is not None:
            application_start_day_elem = driver.find_element_by_name(
                'sF21912_3')
            Select(application_start_day_elem).select_by_value(
                config['application_start_day'])

        if config.get('application_start_time') is not None:
            application_start_time_elem = driver.find_element_by_name(
                'sF21912_4')
            Select(application_start_time_elem).select_by_value(
                config['application_start_time'])

        if config.get('application_end_day') is not None:
            application_end_day_elem = driver.find_element_by_name('sF21912_5')
            Select(application_end_day_elem).select_by_value(
                config['application_end_day'])

        if config.get('application_end_time') is not None:
            application_end_time_elem = driver.find_element_by_name(
                'sF21912_6')
            Select(application_end_time_elem).select_by_value(
                config['application_end_time'])

        if config.get('application_location') is not None:
            application_location_elem = driver.find_element_by_name(
                'sF21912_1')
            application_location_elem.clear()
            application_location_elem.send_keys(config['application_location'])

        if config.get('application_reason') is not None:
            application_reason_elem = driver.find_element_by_name('sF21912_2')
            application_reason_elem.clear()
            application_reason_elem.send_keys(config['application_reason'])

        # fill data into form
        city_status = driver.find_element_by_name("sF21650_5")
        working_place = driver.find_element_by_name("sF21650_6")
        health_status = driver.find_element_by_name("sF21650_7")
        living_status = driver.find_element_by_name("sF21650_8")
        home_status = driver.find_element_by_name("sF21650_9")

        Select(city_status).select_by_value(config['cityStatus'])
        Select(working_place).select_by_value(config['workingPlace'])
        Select(health_status).select_by_value(config['healthStatus'])
        Select(living_status).select_by_value(config['livingStatus'])
        Select(home_status).select_by_value(config['homeStatus'])

        questionnaire_submit = driver.find_element_by_name("B2")
        questionnaire_submit.click()

        # time.sleep(1)
        try:
            alert_window = driver.switch_to.alert
            alert_window.accept()
        except NoAlertPresentException:
            logger.warning(
                f'学号: {STU_ID},确认窗口未弹出，当前时间为: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            form_body = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

            # form_body = driver.find_element_by_tag_name("form")
            vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
            form_body.screenshot(vc_image_path)
            logger.info(
                f"{STU_ID} 打卡： 确认窗口未弹出但打卡成功并已经截图,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
            userdb.db_put_dk_callback_info(STU_ID, "打卡成功")

        # get screenshot

        # time.sleep(1)

        form_body = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )

        # form_body = driver.find_element_by_tag_name("form")
        vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
        form_body.screenshot(vc_image_path)
        userdb.db_put_dk_callback_info(STU_ID, "打卡成功")
        logger.info(
            f"{STU_ID}: 打卡成功,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
        # print(os.path.dirname(os.path.abspath(vc_image_path)))
        # close browser window
    except NoSuchElementException or NoAlertPresentException or UnexpectedAlertPresentException or InvalidSelectorException or InvalidElementStateException:
        logger.warning(
            f'学号 {STU_ID} , 打卡错误,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        # userdb.db_delete_user_info(STU_ID)
        userdb.db_put_dk_callback_info(
            STU_ID, f'打卡失败,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    finally:
        driver.close()
        driver.quit()
        # gen_log.info("打卡退出")
