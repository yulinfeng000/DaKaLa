from datetime import datetime
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


def dakala(student, config):
    # print(student, config)
    STU_ID = student['stuid']
    STU_PASSWD = student['password']

    if STU_ID == "" and STU_PASSWD == "":
        # print("没有设置教务处用户名和密码")
        return False

    mobileEmulation = {'deviceName': 'iPhone X'}
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    # options.add_argument('headless')
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

        # username_input = driver.find_element_by_id("txtId")
        # password_input = driver.find_element_by_id("txtMM")
        # login_submit_btn = driver.find_element_by_id("IbtnEnter")

        """
        vc_input       = driver.find_element_by_id("txtVC")
        vc_img         = driver.find_element_by_id("verifypic")
        """

        # clean and input value
        # username_input.clear()
        # username_input.value = STU_ID
        # username_input.send_keys(STU_ID)
        # password_input.clear()
        # password_input.send_keys(STU_PASSWD)
        # password_input.value = STU_PASSWD
        # time.sleep(1)
        # submit
        # login_submit_btn.click()
        """
       
        a_tag_list = driver.find_elements_by_tag_name("a")
        for link in a_tag_list:
            if link.get_attribute("href").count('jkdk=Y') > 0:
                link.click()
                break

        """

        # stu_daka_url = f'{DAKA_URL}{STU_ID}&Id={}'
        driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/sj.asp?UTp=Xs&jkdk=Y")
        # time.sleep(1)
        # n = driver.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
        # print('当前句柄: ', n)  # 会打印所有的句柄
        # driver.switch_to.window(n[-1])
        # time.sleep(12)
        linkList = driver.find_elements_by_tag_name("a")
        # gen_log.warning(linkList[1].get_attribute('href'))

        linkList[0].click()

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
            logger.warning(f'学号: {STU_ID},确认窗口未弹出，当前时间为: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            form_body = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )

            # form_body = driver.find_element_by_tag_name("form")
            vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
            form_body.screenshot(vc_image_path)
            logger.info(f"{STU_ID} 打卡： 确认窗口未弹出但打卡成功并已经截图,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
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
        logger.info(f"{STU_ID}: 打卡成功,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
        # print(os.path.dirname(os.path.abspath(vc_image_path)))
        # close browser window
    except NoSuchElementException or NoAlertPresentException or UnexpectedAlertPresentException or InvalidSelectorException or InvalidElementStateException:
        logger.warning(f'学号 {STU_ID} , 打卡错误,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        # userdb.db_delete_user_info(STU_ID)
        userdb.db_put_dk_callback_info(STU_ID, f'打卡失败,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    finally:
        driver.close()
        driver.quit()
        # gen_log.info("打卡退出")
