from datetime import datetime
import userdb
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logsetting import logger

DAKA_URL = "http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netKs/editSj.asp?UTp=Xs&Tx=33_1&ObjId="
daka_logger = logger


def is_scheduler_exec(config: dict, stuid):
    if not config.get("scheduler_start_time"):
        return False

    start_time = datetime.strptime(config.get("scheduler_start_time"), '%Y-%m-%d')
    if datetime.now().date() == start_time.date():  # 预定打卡时间是今天
        daka_logger.info(f'{stuid}，开始执行定时打卡任务')
        return True

    if not config.get("scheduler_time_segment"):  # 如果不是今天，但也没有设置打卡间隔
        return False

    if int(config.get("scheduler_time_segment")) <= 0:  # 如果打卡时间间隔小于等于0,说明是一次性的预定
        return False
    scheduler_time_segment = int(config.get("scheduler_time_segment"))

    last_exec_time_str = userdb.db_get_last_scheduler_exec_time(stuid)
    daka_logger.debug(
        f'{stuid},设定的开始时间为{start_time.date()},上次执行时间是{last_exec_time_str},设定的间隔为{scheduler_time_segment}天,今天是{datetime.now().date()}')

    if not last_exec_time_str:  # 如果没有上一次执行的结果
        time_interval = datetime.now().date() - start_time.date()  # 得到今天距离预定时间的时间间隔
        if time_interval.days >= scheduler_time_segment:  # 如果间隔大于等于预定的间隔
            userdb.db_put_last_scheduler_exec_time(stuid, str(datetime.now().date()))
            daka_logger.info(f'{stuid}，开始执行定时打卡任务')
            return True
        else:
            return False
    last_exec_time = datetime.strptime(last_exec_time_str, '%Y-%m-%d')
    time_interval = datetime.now().date() - last_exec_time.date()
    if time_interval.days >= scheduler_time_segment:
        userdb.db_put_last_scheduler_exec_time(stuid, str(datetime.now().date()))
        daka_logger.info(f'{stuid}，开始执行定时打卡任务')
        return True
    else:
        return False


def dakaing(link, driver, student, config):
    link.click()  # 进入打卡界面

    from selenium.common.exceptions import \
        NoSuchElementException, NoAlertPresentException, UnexpectedAlertPresentException, InvalidSelectorException, \
        InvalidElementStateException, TimeoutException
    STU_ID = student['stuid']
    try:
        if is_scheduler_exec(config, STU_ID):
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
            daka_logger.warning(
                f'学号: {STU_ID},确认窗口未弹出，当前时间为: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

            form_body = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "wjTA"))
            )

            if not form_body:
                import time
                time.sleep(2)
                driver.refresh()
                form_body = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, "wjTA"))
                )
                if not form_body:
                    raise TimeoutException

                    # form_body = driver.find_element_by_tag_name("form")
            vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
            form_body.screenshot(vc_image_path)
            daka_logger.info(
                f"{STU_ID} 打卡： 确认窗口未弹出但打卡成功并已经截图,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")
            userdb.db_put_dk_callback_info(STU_ID, "打卡成功")

        # get screenshot

        # time.sleep(1)

        form_body = WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.TAG_NAME, "form"))
        )

        if not form_body:
            driver.refresh()
            form_body = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.ID, "wjTA"))
            )
            if not form_body:
                raise TimeoutException

        # form_body = driver.find_element_by_tag_name("form")
        vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
        import os
        form_body.screenshot(os.path.abspath(vc_image_path))

        userdb.db_put_dk_callback_info(STU_ID, "打卡成功")
        daka_logger.info(
            f"{STU_ID}: 打卡成功,时间为{datetime.now().strftime('%m/%d/%Y, %H:%M:%S')}")

        # close browser window

    except NoSuchElementException or NoAlertPresentException or UnexpectedAlertPresentException or InvalidSelectorException or InvalidElementStateException:
        daka_logger.warning(f'学号 {STU_ID} , 打卡错误,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
        userdb.db_put_dk_callback_info(STU_ID, f'打卡失败,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')


def dakala(student, config: dict):
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
    try:
        driver.maximize_window()

        # go to login page
        driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/sj.asp")
        # time.sleep(1)

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

        linkList = driver.find_elements_by_tag_name("a")

        target_a = None
        for a in linkList[:5]:
            if a.text.startswith(f'{datetime.now().strftime("%m%d")}'):
                target_a = a
                break

        if target_a:
            dakaing(target_a, driver, student, config)
            daka_logger.info(f"{STU_ID},打卡任务执行完毕")
        else:
            daka_logger.warning(f"{STU_ID}没有找到今天的打卡链接!!!,今天是{datetime.now().strftime('%m%d')},\n{str([link.text for link in linkList[:5]])}")
            userdb.db_put_dk_callback_info(STU_ID, f'打卡失败,没有找到今天的打卡链接,时间为{datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}')
    finally:
        driver.quit()
        daka_logger.debug(f"{STU_ID}打卡结束，浏览器退出")
    return STU_ID
