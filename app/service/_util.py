from selenium import webdriver


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
