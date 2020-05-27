import time

from selenium import webdriver
from selenium.webdriver.support.select import Select
import os


def dakala(student, config):
    print(student, config)
    STU_ID = student['stuid']
    STU_PASSWD = student['password']

    if STU_ID == "" and STU_PASSWD == "":
        print("没有设置教务处用户名和密码")
        return False

    mobileEmulation = {'deviceName': 'iPhone X'}
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_experimental_option('mobileEmulation', mobileEmulation)
    # start chrome and maximize window
    driver = webdriver.Chrome(options=options)

    driver.maximize_window()

    # go to login page
    driver.get("http://jszx-jxpt.cuit.edu.cn/Jxgl/Xs/netks/sj.asp")

    time.sleep(1)
    # find input element
    username_input = driver.find_element_by_id("txtId")
    password_input = driver.find_element_by_id("txtMM")
    login_submit_btn = driver.find_element_by_id("IbtnEnter")

    """
    vc_input       = driver.find_element_by_id("txtVC")
    vc_img         = driver.find_element_by_id("verifypic")
    """

    # clean and input value
    username_input.clear()
    username_input.send_keys(STU_ID)
    password_input.clear()
    password_input.send_keys(STU_PASSWD)
    time.sleep(3)
    # submit
    login_submit_btn.click()

    a_tag_list = driver.find_elements_by_tag_name("a")
    for link in a_tag_list:
        if link.get_attribute("href").count('jkdk=Y') > 0:
            link.click()
            break

    time.sleep(3)
    n = driver.window_handles  # 这个时候会生成一个新窗口或新标签页的句柄，代表这个窗口的模拟driver
    print('当前句柄: ', n)  # 会打印所有的句柄
    driver.switch_to.window(n[-1])

    linkList = driver.find_elements_by_tag_name("a")
    linkList[1].click()

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

    time.sleep(1)
    # alert_window = driver.switch_to.alert
    # alert_window.accept()

    # get screenshot
    form_body = driver.find_element_by_tag_name("form")
    vc_image_path = f'./static/vc_images/{STU_ID}_img.png'
    form_body.screenshot(vc_image_path)
    print(os.path.dirname(os.path.abspath(vc_image_path)))
    # close browser window
    driver.quit()
    return True
