#!/usr/bin/env python3
#encoding=utf-8
# seleniumwire not support python 2.x.
# if you want running under python 2.x, you need to assign driver_type = 'stealth'
import os
import sys
import platform
import json
import random

# for close tab.
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import UnexpectedAlertPresentException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import WebDriverException
# for alert 2
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
# for selenium 4
from selenium.webdriver.chrome.service import Service
# for wait #1
import time
# for error output
import logging
logging.basicConfig()
logger = logging.getLogger('logger')
# for check reg_info
import requests
import warnings
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore',InsecureRequestWarning)

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

CONST_APP_VERSION = "MaxinlineBot (2023.05.31)"
CONST_HOMEPAGE_DEFAULT = "https://inline.app/"

CONST_CHROME_VERSION_NOT_MATCH_EN="Please download the WebDriver version to match your browser version."
CONST_CHROME_VERSION_NOT_MATCH_TW="請下載與您瀏覽器相同版本的WebDriver版本，或更新您的瀏覽器版本。"

def get_app_root():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)
    return app_root

def get_config_dict():
    config_json_filename = 'settings.json'
    app_root = get_app_root()
    config_filepath = os.path.join(app_root, config_json_filename)
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)
    return config_dict

def get_favoriate_extension_path(webdriver_path):
    print("webdriver_path:", webdriver_path)
    no_google_analytics_path = os.path.join(webdriver_path,"no_google_analytics_1.1.0.0.crx")
    no_ad_path = os.path.join(webdriver_path,"Adblock_3.16.1.0.crx")
    buster_path = os.path.join(webdriver_path,"Buster_2.0.1.0.crx")
    return no_google_analytics_path, no_ad_path, buster_path

def get_chromedriver_path(webdriver_path):
    chromedriver_path = os.path.join(webdriver_path,"chromedriver")
    if platform.system().lower()=="windows":
        chromedriver_path = os.path.join(webdriver_path,"chromedriver.exe")
    return chromedriver_path

def get_chrome_options(webdriver_path, adblock_plus_enable, browser="chrome", headless = False):
    chrome_options = webdriver.ChromeOptions()
    if browser=="edge":
        chrome_options = webdriver.EdgeOptions()
    if browser=="safari":
        chrome_options = webdriver.SafariOptions()

    # some windows cause: timed out receiving message from renderer
    if adblock_plus_enable:
        # PS: this is ocx version.
        no_google_analytics_path, no_ad_path, buster_path = get_favoriate_extension_path(webdriver_path)

        if os.path.exists(no_google_analytics_path):
            chrome_options.add_extension(no_google_analytics_path)
        if os.path.exists(no_ad_path):
            chrome_options.add_extension(no_ad_path)
        if os.path.exists(buster_path):
            chrome_options.add_extension(buster_path)
    if headless:
        #chrome_options.add_argument('--headless')
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--disable-features=TranslateUI')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--lang=zh-TW')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument("--no-sandbox");

    # for navigator.webdriver
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # Deprecated chrome option is ignored: useAutomationExtension
    #chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    #caps = DesiredCapabilities().CHROME
    caps = chrome_options.to_capabilities()

    #caps["pageLoadStrategy"] = u"normal"  #  complete
    caps["pageLoadStrategy"] = u"eager"  #  interactive
    #caps["pageLoadStrategy"] = u"none"

    #caps["unhandledPromptBehavior"] = u"dismiss and notify"  #  default
    #caps["unhandledPromptBehavior"] = u"ignore"
    #caps["unhandledPromptBehavior"] = u"dismiss"
    caps["unhandledPromptBehavior"] = u"accept"

    return chrome_options, caps

def load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable, headless):
    driver = None

    chromedriver_path = get_chromedriver_path(webdriver_path)
    if not os.path.exists(chromedriver_path):
        print("Please download chromedriver and extract zip to webdriver folder from this url:")
        print("請下在面的網址下載與你chrome瀏覽器相同版本的chromedriver,解壓縮後放到webdriver目錄裡：")
        print(URL_CHROME_DRIVER)
    else:
        chrome_service = Service(chromedriver_path)
        chrome_options, caps = get_chrome_options(webdriver_path, adblock_plus_enable, headless=headless)
        try:
            # method 6: Selenium Stealth
            driver = webdriver.Chrome(service=chrome_service, options=chrome_options, desired_capabilities=caps)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)

    if driver_type=="stealth":
        from selenium_stealth import stealth
        # Selenium Stealth settings
        stealth(driver,
              languages=["zh-TW", "zh"],
              vendor="Google Inc.",
              platform="Win32",
              webgl_vendor="Intel Inc.",
              renderer="Intel Iris OpenGL Engine",
              fix_hairline=True,
          )
    #print("driver capabilities", driver.capabilities)

    return driver

def load_chromdriver_uc(webdriver_path, adblock_plus_enable, headless):
    import undetected_chromedriver as uc

    chromedriver_path = get_chromedriver_path(webdriver_path)

    options = uc.ChromeOptions()
    options.page_load_strategy="eager"

    #print("strategy", options.page_load_strategy)

    if adblock_plus_enable:
        no_google_analytics_path, no_ad_path, buster_path = get_favoriate_extension_path(webdriver_path)
        no_google_analytics_folder_path = no_google_analytics_path.replace('.crx','')
        no_ad_folder_path = no_ad_path.replace('.crx','')
        buster_path = buster_path.replace('.crx','')
        load_extension_path = ""
        if os.path.exists(no_google_analytics_folder_path):
            load_extension_path += "," + no_google_analytics_folder_path
        if os.path.exists(no_ad_folder_path):
            load_extension_path += "," + no_ad_folder_path
        if os.path.exists(buster_path):
            load_extension_path += "," + buster_path
        if len(load_extension_path) > 0:
            options.add_argument('--load-extension=' + load_extension_path[1:])

    if headless:
        #options.add_argument('--headless')
        options.add_argument('--headless=new')
    options.add_argument('--disable-features=TranslateUI')
    options.add_argument('--disable-translate')
    options.add_argument('--lang=zh-TW')
    options.add_argument('--disable-web-security')
    options.add_argument("--no-sandbox");

    options.add_argument("--password-store=basic")
    options.add_experimental_option("prefs", {"credentials_enable_service": False, "profile.password_manager_enabled": False, "translate":{"enabled": False}})

    caps = options.to_capabilities()
    caps["unhandledPromptBehavior"] = u"accept"

    driver = None
    try:
        driver = uc.Chrome(executable_path=chromedriver_path, options=options, desired_capabilities=caps, suppress_welcome=False)
    except Exception as exc:
        error_message = str(exc)
        left_part = None
        if "Stacktrace:" in error_message:
            left_part = error_message.split("Stacktrace:")[0]
            print(left_part)

        if "This version of ChromeDriver only supports Chrome version" in error_message:
            print(CONST_CHROME_VERSION_NOT_MATCH_EN)
            print(CONST_CHROME_VERSION_NOT_MATCH_TW)

    else:
        #print("Oops! web driver not on path:",chromedriver_path )
        print('undetected_chromedriver automatically download chromedriver.')
        try:
            driver = uc.Chrome(options=options, desired_capabilities=caps, suppress_welcome=False)
        except Exception as exc:
            error_message = str(exc)
            left_part = None
            if "Stacktrace:" in error_message:
                left_part = error_message.split("Stacktrace:")[0]
                print(left_part)

            if "This version of ChromeDriver only supports Chrome version" in error_message:
                print(CONST_CHROME_VERSION_NOT_MATCH_EN)
                print(CONST_CHROME_VERSION_NOT_MATCH_TW)
            pass

    if driver is None:
        print("create web drive object by undetected_chromedriver fail!")

        if os.path.exists(chromedriver_path):
            print("Unable to use undetected_chromedriver, ")
            print("try to use local chromedriver to launch chrome browser.")
            driver_type = "selenium"
            driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable, headless)
        else:
            print("建議您自行下載 ChromeDriver 到 webdriver 的資料夾下")
            print("you need manually download ChromeDriver to webdriver folder.")

    return driver

def close_browser_tabs(driver):        
    if not driver is None:
        try:
            window_handles_count = len(driver.window_handles)
            if window_handles_count >= 1:
                driver.switch_to.window(driver.window_handles[1])
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
        except Exception as excSwithFail:
            pass

def get_driver_by_config(config_dict, driver_type):
    global driver

    homepage = ""
    browser = "chrome"              # skip 'firefox'...
    language = "English"
    adblock_plus_enable = False     # inline is not need adblock plus.

    adult_picker = ""
    book_now_time = ""
    book_now_time_alt = ""

    user_name = ""
    user_gender = ""
    user_phone = ""
    user_email = ""

    cardholder_name=""
    cardholder_email = ""
    cc_number = ""
    cc_exp = ""
    cc_ccv = ""

    if not config_dict is None:
        # output config:
        print("maxbot app version", CONST_APP_VERSION)
        print("python version", platform.python_version())
        print("homepage", config_dict["homepage"])
        print("adult_picker", config_dict["adult_picker"])
        print("book_now_time", config_dict["book_now_time"])
        print("book_now_time_alt", config_dict["book_now_time_alt"])
        
        print("user_name", config_dict["user_name"])
        print("user_gender", config_dict["user_gender"])
        print("user_phone", config_dict["user_phone"])
        print("user_email", config_dict["user_email"])

        print("cardholder_name", config_dict["cardholder_name"])
        print("cardholder_email", config_dict["cardholder_email"])
        print("cc_number", config_dict["cc_number"])
        print("cc_exp", config_dict["cc_exp"])
        print("cc_ccv", config_dict["cc_ccv"])
        
        if 'cc_auto_submit' in config_dict:
            print("cc_auto_submit", config_dict["cc_auto_submit"])

        homepage = config_dict["homepage"]
        adult_picker = config_dict["adult_picker"]
        book_now_time = config_dict["book_now_time"]
        book_now_time_alt = config_dict["book_now_time_alt"]
        
        user_name = config_dict["user_name"]
        user_gender = config_dict["user_gender"]
        user_phone = config_dict["user_phone"]
        user_email = config_dict["user_email"]

        cardholder_name = config_dict["cardholder_name"]
        cardholder_email = config_dict["cardholder_email"]
        cc_number = config_dict["cc_number"]
        cc_exp = config_dict["cc_exp"]
        cc_ccv = config_dict["cc_ccv"]

        if 'cc_auto_submit' in config_dict:
            cc_auto_submit = config_dict["cc_auto_submit"]

        # entry point
        if homepage is None:
            homepage = ""
        if len(homepage) == 0:
            homepage = CONST_HOMEPAGE_DEFAULT

        Root_Dir = get_app_root()
        webdriver_path = os.path.join(Root_Dir, "webdriver")
        print("platform.system().lower():", platform.system().lower())

        headless = False
        if browser == "chrome":
            # method 6: Selenium Stealth
            if driver_type != "undetected_chromedriver":
                driver = load_chromdriver_normal(webdriver_path, driver_type, adblock_plus_enable)
            else:
                # method 5: uc
                # multiprocessing not work bug.
                if platform.system().lower()=="windows":
                    if hasattr(sys, 'frozen'):
                        from multiprocessing import freeze_support
                        freeze_support()
                driver = load_chromdriver_uc(webdriver_path, adblock_plus_enable, headless)

        #print("try to close opened tabs.")
        '''
        time.sleep(1.0)
        for i in range(1):
            close_browser_tabs(driver)
        '''

        if driver is None:
            print("create web driver object fail @_@;")
        else:
            try:
                print("goto url:", homepage)
                driver.get(homepage)
            except WebDriverException as exce2:
                print('oh no not again, WebDriverException')
                print('WebDriverException:', exce2)
            except Exception as exce1:
                print('get URL Exception:', exec1)
                pass
    else:
        print("Config error!")

    return driver

def is_House_Rules_poped(driver):
    ret = False
    #---------------------------
    # part 1: check house rule pop
    #---------------------------
    house_rules_div = None
    try:
        house_rules_div = driver.find_element(By.ID, 'house-rules')
    except Exception as exc:
        pass

    houses_rules_button = None
    if house_rules_div is not None:
        is_visible = False
        try:
            if house_rules_div.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        if is_visible:
            try:
                #houses_rules_button = house_rules_div.find_element(By.TAG_NAME, 'button')
                houses_rules_button = house_rules_div.find_element(By.XPATH, '//button[@data-cy="confirm-house-rule"]')
            except Exception as exc:
                pass

    if houses_rules_button is not None:
        #print("found disabled houses_rules_button, enable it.")
        
        # method 1: force enable, fail.
        # driver.execute_script("arguments[0].disabled = false;", commit)

        # metho 2: scroll to end.
        houses_rules_scroll = None
        try:
            houses_rules_scroll = house_rules_div.find_element(By.XPATH, '//div[@data-show-scrollbar="true"]/div/div')
        except Exception as exc:
            pass
        
        if houses_rules_scroll is not None:
            try:
                if houses_rules_scroll.is_enabled():
                    #print("found enabled scroll bar. scroll to end.")
                    houses_rules_scroll.click()
                    
                    #PLAN A -- fail.
                    #print('send end key.')
                    #houses_rules_scroll.send_keys(Keys.END)
                    
                    #PLAN B -- OK.
                    #driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", houses_rules_scroll)
                    driver.execute_script("arguments[0].innerHTML='';", houses_rules_scroll);
            except Exception as exc:
                #print("check house rules fail...")
                #print(exc)
                pass


        houses_rules_is_visible = False
        try:
            if houses_rules_button.is_enabled():
                houses_rules_is_visible = True
        except Exception as exc:
            pass
        
        if houses_rules_is_visible:
            print("found enabled houses_rules_button.")
            try:
                houses_rules_button.click()
            except Exception as exc:
                    try:
                        driver.execute_script("arguments[0].click();", houses_rules_button);
                    except Exception as exc2:
                        pass


    return ret

def button_submit(el_form, by_method, query_keyword):
    # user name
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        is_visible = False
        try:
            if el_text_name.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        
        if is_visible:
            try:
                el_text_name.click()
            except Exception as exc:
                print("send el_text_%s fail" % (query_keyword))
                #print(exc)

                try:
                    driver.execute_script("arguments[0].click();", el_text_name);
                except Exception as exc:
                    print("try javascript click on el_text_%s, still fail." % (query_keyword))
                    #print(exc)


def click_radio(el_form, by_method, query_keyword, assign_method='CLICK'):
    is_radio_selected = False
    # user name
    
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))

    if el_text_name is not None:
        #print("found el_text_name")
        try:
            is_radio_selected = el_text_name.is_selected()
        except Exception as exc:
            pass

        if not is_radio_selected:
            if assign_method=='CLICK':
                try:
                    el_text_name.click()
                except Exception as exc:
                    print("send el_text_%s fail" % (query_keyword))

                    #print(exc)
                    try:
                        driver.execute_script("arguments[0].click();", el_text_name);
                    except Exception as exc:
                        print("try javascript click on el_text_%s, still fail." % (query_keyword))
                        #print(exc)

            if assign_method=='JS':
                try:
                    driver.execute_script("arguments[0].checked;", el_text_name);
                except Exception as exc:
                    print("send el_text_%s fail" % (query_keyword))
                    print(exc)
        else:
            pass
            #print("text not empty, value:", text_name_value)

    return is_radio_selected


def checkbox_agree(el_form, by_method, query_keyword, assign_method='CLICK'):
    ret = False
    # user name
    
    el_text_name = None
    el_label_name = None

    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
        if by_method == By.ID:
            el_label_name = el_form.find_element(By.XPATH, '//label[@for="%s"]' % (query_keyword))
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        ret = el_text_name.is_selected()
        if not el_text_name.is_selected():
            if assign_method=='CLICK':
                #el_text_name.click()
                if el_label_name is not None:
                    print('click label for chekbox:', query_keyword)
                    try:
                        el_label_name.click()
                    except Exception as exc:
                        print("send el_text_%s fail" % (query_keyword))
                        #print(exc)
                        try:
                            driver.execute_script("arguments[0].click();", el_label_name);
                        except Exception as exc:
                            print("try javascript click on el_text_%s, still fail." % (query_keyword))
                            #print(exc)

            if assign_method=='JS':
                driver.execute_script("arguments[0].checked;", el_text_name);
        else:
            pass
            #print("text not empty, value:", text_name_value)

    return ret

# assign value in text.
# return:
#   True: value in text
#   False: assign fail.
def fill_text_by_default(el_form, by_method, query_keyword, default_value, assign_method='SENDKEY'):
    ret = False

    # user name
    el_text_name = None
    try:
        el_text_name = el_form.find_element(by_method, query_keyword)
    except Exception as exc:
        pass
        #print("find el_text_%s fail" % (query_keyword))
    if el_text_name is not None:
        #print("found el_text_name")
        text_name_value = None
        try:
            text_name_value = str(el_text_name.get_attribute('value'))
        except Exception as exc:
            pass
        if not text_name_value is None:
            if text_name_value == "":
                #print("try to send keys:", user_name)
                if assign_method=='SENDKEY':
                    try:
                        el_text_name.send_keys(default_value)
                        ret = True
                    except Exception as exc:
                        try:
                            driver.execute_script("arguments[0].value='%s';" % (default_value), el_text_name);
                        except Exception as exc:
                            pass
                if assign_method=='JS':
                    try:
                        driver.execute_script("arguments[0].value='%s';" % (default_value), el_text_name);
                    except Exception as exc:
                        pass

            else:
                ret = True

    return ret

def fill_personal_info(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False
    #print("fill form")

    # user form
    el_form = None
    try:
        el_form = driver.find_element(By.ID, 'contact-form')
    except Exception as exc:
        pass

    if not el_form is None:
        #print("found form")

        # gender-female
        # gender-male
        user_gender = config_dict["user_gender"]
        if user_gender == "先生":
            ret = click_radio(el_form, By.ID, 'gender-male')
        if user_gender == "小姐":
            ret = click_radio(el_form, By.ID, 'gender-female')

        user_name = config_dict["user_name"]
        user_phone = config_dict["user_phone"]
        user_email = config_dict["user_email"]
        ret = fill_text_by_default(el_form, By.ID, 'name', user_name)
        ret = fill_text_by_default(el_form, By.ID, 'phone', user_phone)
        ret = fill_text_by_default(el_form, By.ID, 'email', user_email)
        
        
        cardholder_name = config_dict["cardholder_name"]
        cardholder_email = config_dict["cardholder_email"]
        ret = fill_text_by_default(el_form, By.ID, 'cardholder-name', cardholder_name)
        ret = fill_text_by_default(el_form, By.ID, 'cardholder-email', cardholder_email)

        cc_number = config_dict["cc_number"]
        cc_exp = config_dict["cc_exp"]
        cc_ccv = config_dict["cc_ccv"]
        
        iframes = None
        try:
            iframes = el_form.find_elements(By.TAG_NAME, "iframe")
        except Exception as exc:
            pass

        if iframes is None:
            iframes = []

        #print('start to travel iframes...')
        cc_check=[False,False,False]
        idx_iframe=0
        for iframe in iframes:
            iframe_url = ""
            try:
                iframe_url = str(iframe.get_attribute('src'))
                #print("url:", iframe_url)
            except Exception as exc:
                print("get iframe url fail.")
                #print(exc)
                pass

            idx_iframe += 1
            try:
                driver.switch_to.frame(iframe)
            except Exception as exc:
                pass

            if "card-number" in iframe_url:
                if not cc_check[0]:
                    #print('check cc-number at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-number', cc_number)
                    cc_check[0]=ret
                    #print("cc-number ret:", ret)
            if "expiration-date" in iframe_url:
                if not cc_check[1]:
                    #print('check cc-exp at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-exp', cc_exp)
                    cc_check[1]=ret
                    #print("cc-exp ret:", ret)
            if "ccv" in iframe_url:
                if not cc_check[2]:
                    #print('check cc-ccv at loop(%d)...' % (idx_iframe))
                    ret = fill_text_by_default(driver, By.ID, 'cc-ccv', cc_ccv)
                    cc_check[2]=ret
                    #print("cc-ccv ret:", ret)
            try:
                driver.switch_to.default_content()
            except Exception as exc:
                pass

        pass_all_check = True

        # check credit card.
        for item in cc_check:
            if item == False:
                pass_all_check = False

        # check agree
        try:
            #print("check agree...")
            #driver.execute_script("$(\"input[type='checkbox']\").prop('checked', true);")
            #driver.execute_script("document.getElementById(\"deposit-policy\").checked;")
            #driver.execute_script("document.getElementById(\"privacy-policy\").checked;")
            agree_ret = checkbox_agree(el_form, By.ID, 'deposit-policy')
            if not agree_ret:
                pass_all_check = False
            agree_ret = checkbox_agree(el_form, By.ID, 'privacy-policy')
            if not agree_ret:
                pass_all_check = False
        except Exception as exc:
            print("javascript check agree fail")
            print(exc)
            pass

        #print("auto_submit:", cc_auto_submit)
        if pass_all_check and cc_auto_submit:
            print("press submit button.")
            ret = button_submit(el_form, By.XPATH,'//button[@type="submit"]')
            pass

    return ret

# reutrn: 
#   False: book fail.
#   True: one of book item is seleted, must to do nothing.
# fail_code:
#   0: no target time in button list.
#   1: time_picker not viewable.
#   100: target time full.
#   200: target button is not viewable or not enable.
#   201: target time click fail.
def book_time(el_time_picker_list, target_time):
    ret = False
    fail_code = 0

    is_one_of_time_picket_viewable = False

    for el_time_picker in el_time_picker_list:
        is_visible = False
        try:
            if el_time_picker.is_enabled():
                is_visible = True
        except Exception as exc:
            pass
        
        time_picker_text = None
        if is_visible:
            is_one_of_time_picket_viewable = True
            try:
                time_picker_text = str(el_time_picker.text)
            except Exception as exc:
                pass
        
        if time_picker_text is None:
            time_picker_text = ""

        if len(time_picker_text) > 0:
            if ":" in time_picker_text:
                #print("button text:", time_picker_text)
                button_class_string = None
                try:
                    button_class_string = str(el_time_picker.get_attribute('class'))
                except Exception as exc:
                    pass
                if button_class_string is None:
                    button_class_string = ""
                
                is_button_able_to_select = True
                if "selected" in button_class_string:
                    is_button_able_to_select = False
                    ret = True
                    #print("button is selected:", button_class_string, time_picker_text)

                    # no need more loop.
                    break

                if "full" in button_class_string:
                    is_button_able_to_select = False
                    if target_time in time_picker_text:
                        #print("button is full:", button_class_string, time_picker_text)
                        fail_code = 100

                        # no need more loop.
                        break
                
                if is_button_able_to_select:
                    if target_time in time_picker_text:
                        is_able_to_click = True
                        if is_able_to_click:
                            print('click this time block:', time_picker_text)

                            try:
                                el_time_picker.click()
                                ret = True
                            except Exception as exc:
                                # is not clickable at point
                                #print("click target time fail.", exc)
                                fail_code = 201

                                # scroll to view ... fail.
                                #driver.execute_script("console.log(\"scroll to view\");")
                                #driver.execute_script("arguments[0].scrollIntoView(false);", el_time_picker)

                                # JS
                                print('click to button using javascript.')
                                try:
                                    driver.execute_script("console.log(\"click to button.\");")
                                    driver.execute_script("arguments[0].click();", el_time_picker)
                                except Exception as exc:
                                    pass
                        else:
                            fail_code = 200
                            print("target button is not viewable or not enable.")
                            pass

        if not is_one_of_time_picket_viewable:
            fail_code = 1
    return ret, fail_code

def assign_adult_picker(driver, adult_picker, force_adult_picker):
    is_adult_picker_assigned = False

    # member number.
    el_adult_picker = None
    try:
        el_adult_picker = driver.find_element(By.ID, 'adult-picker')
    except Exception as exc:
        pass
    
    if not el_adult_picker is None:
        is_visible = False
        try:
            if el_adult_picker.is_enabled():
                is_visible = True
        except Exception as exc:
            pass

        if is_visible:
            selected_value = None
            try:
                selected_value = str(el_adult_picker.get_attribute('value'))
                #print('seleced value:', selected_value)
            except Exception as exc:
                pass

            if selected_value is None:
                selected_value = ""
            
            if selected_value == "":
                selected_value = "0"

            is_need_assign_select = True
            if selected_value != "0":
                # not is default value, do assign.
                is_need_assign_select = False
                is_adult_picker_assigned = True

                if force_adult_picker:
                    if selected_value != adult_picker:
                        is_need_assign_select = True

            if is_need_assign_select:
                #print('assign new value("%s") for select.' % (adult_picker))
                adult_number_select = Select(el_adult_picker)
                try:
                    adult_number_select.select_by_value(adult_picker)
                    is_adult_picker_assigned = True
                except Exception as exc:
                    print("select_by_value for adult-picker fail")
                    print(exc)
                    pass

    return is_adult_picker_assigned

def assign_time_picker(driver, book_now_time, book_now_time_alt):
    show_debug_message = True       # debug.
    #show_debug_message = False      # online

    ret = False

    el_time_picker_list = None
    button_query_string = 'button.time-slot'
    try:
        el_time_picker_list = driver.find_elements(By.CSS_SELECTOR, button_query_string)
    except Exception as exc:
        if show_debug_message:
            print("find time buttons excpetion:", exc)
        pass

    if not el_time_picker_list is None:
        el_time_picker_list_size = len(el_time_picker_list)
        if show_debug_message:
            print("el_time_picker_list_size:", el_time_picker_list_size)

        if el_time_picker_list_size > 0:
            # default use main time.
            book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time)
            
            if show_debug_message:
                print("booking target time:", book_now_time)
                print("book_time_ret, book_fail_code:", book_time_ret, book_fail_code)
            
            if not book_time_ret:
                if book_fail_code >= 200:
                    # [200,201] ==> retry
                    # retry main target time.
                    book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time)
                    if show_debug_message:
                        print("retry booking target time:", book_time_ret, book_fail_code)
                else:
                    # try alt time.
                    book_time_ret, book_fail_code = book_time(el_time_picker_list, book_now_time_alt)
                    if show_debug_message:
                        print("booking ALT time:", book_now_time_alt)
                        print("booking ALT target time:", book_time_ret, book_fail_code)
        else:
            if show_debug_message:
                print("time element length zero...")
    else:
        if show_debug_message:
            print("not found time elements.")

    
    return ret

def inline_reg(driver, config_dict):
    show_debug_message = True       # debug.
    show_debug_message = False      # online

    if config_dict["advanced"]["verbose"]:
        show_debug_message = True

    ret = False

    house_rules_ret = is_House_Rules_poped(driver)

    if show_debug_message:
        print("house_rules_ret:", house_rules_ret)

    if not house_rules_ret:
        adult_picker = config_dict["adult_picker"]
        force_adult_picker = config_dict["force_adult_picker"]

        # date picker.
        is_adult_picker_assigned = assign_adult_picker(driver, adult_picker, force_adult_picker)
        if show_debug_message:
            print("is_adult_picker_assigned:", is_adult_picker_assigned)

        if not is_adult_picker_assigned:
            # retry once.
            is_adult_picker_assigned = assign_adult_picker(driver, adult_picker, force_adult_picker)
            if show_debug_message:
                print("retry is_adult_picker_assigned:", is_adult_picker_assigned)

        # time picker.
        book_now_time = config_dict["book_now_time"]
        book_now_time_alt = config_dict["book_now_time_alt"]
        if is_adult_picker_assigned:
            ret = assign_time_picker(driver, book_now_time, book_now_time_alt)
            if show_debug_message:
                print("assign_time_picker return:", ret)

    return ret

def main():
    config_dict = get_config_dict()

    driver_type = 'selenium'
    #driver_type = 'stealth'
    driver_type = 'undetected_chromedriver'

    driver = get_driver_by_config(config_dict, driver_type)

    # internal variable. 說明：這是一個內部變數，請略過。
    url = ""
    last_url = ""

    debugMode = False
    if 'debug' in config_dict:
        debugMode = config_dict["debug"]

    if debugMode:
        print("Start to looping, detect browser url...")

    DISCONNECTED_MSG = ': target window already closed'

    while True:
        time.sleep(0.05)

        is_alert_popup = False

        # pass if driver not loaded.
        if driver is None:
            print("web driver not accessible!")
            break

        #is_alert_popup = check_pop_alert(driver)

        #MUST "do nothing: if alert popup.
        #print("is_alert_popup:", is_alert_popup)
        if is_alert_popup:
            continue

        url = ""
        try:
            url = driver.current_url
        except NoSuchWindowException:
            print('NoSuchWindowException at this url:', url )
            #print("last_url:", last_url)
            #print("get_log:", driver.get_log('driver'))
            window_handles_count = 0
            try:
                window_handles_count = len(driver.window_handles)
                #print("window_handles_count:", window_handles_count)
                if window_handles_count >= 1:
                    driver.switch_to.window(driver.window_handles[0])
                    driver.switch_to.default_content()
                    time.sleep(0.2)
            except Exception as excSwithFail:
                #print("excSwithFail:", excSwithFail)
                pass
            if window_handles_count==0:
                try:
                    driver_log = driver.get_log('driver')[-1]['message']
                    print("get_log:", driver_log)
                    if DISCONNECTED_MSG in driver_log:
                        print('quit bot by NoSuchWindowException')
                        driver.quit()
                        sys.exit()
                        break
                except Exception as excGetDriverMessageFail:
                    #print("excGetDriverMessageFail:", excGetDriverMessageFail)
                    except_string = str(excGetDriverMessageFail)
                    if 'HTTP method not allowed' in except_string:
                        print('quit bot by close browser')
                        driver.quit()
                        sys.exit()
                        break

        except UnexpectedAlertPresentException as exc1:
            print('UnexpectedAlertPresentException at this url:', url )
            # PS: do nothing...
            # PS: current chrome-driver + chrome call current_url cause alert/prompt dialog disappear!
            # raise exception at selenium/webdriver/remote/errorhandler.py
            # after dialog disappear new excpetion: unhandled inspector error: Not attached to an active page
            is_pass_alert = False
            is_pass_alert = True
            if is_pass_alert:
                try:
                    driver.switch_to.alert.accept()
                except Exception as exc:
                    pass

        except Exception as exc:
            logger.error('Maxbot URL Exception')
            logger.error(exc, exc_info=True)

            #UnicodeEncodeError: 'ascii' codec can't encode characters in position 63-72: ordinal not in range(128)
            str_exc = ""
            try:
                str_exc = str(exc)
            except Exception as exc2:
                pass

            if len(str_exc)==0:
                str_exc = repr(exc)

            exit_bot_error_strings = [u'Max retries exceeded'
            , u'chrome not reachable'
            , u'unable to connect to renderer'
            , u'failed to check if window was closed'
            , u'Failed to establish a new connection'
            , u'Connection refused'
            , u'disconnected'
            , u'without establishing a connection'
            , u'web view not found'
            ]
            for each_error_string in exit_bot_error_strings:
                if isinstance(str_exc, str):
                    if each_error_string in str_exc:
                        print('quit bot by error:', each_error_string)
                        driver.quit()
                        sys.exit()
                        break

            # not is above case, print exception.
            print("Exception:", str_exc)
            pass

        if url is None:
            continue
        else:
            if len(url) == 0:
                continue

        # 說明：輸出目前網址，覺得吵的話，請註解掉這行。
        if debugMode:
            print("url:", url)

        if len(url) > 0 :
            if url != last_url:
                print(url)
            last_url = url

        target_domain_list = ['//inline.app/booking/']
        for each_domain in target_domain_list:
            if each_domain in url:
                current_progress_array = url.split('/')
                current_progress_length = len(current_progress_array)
                if current_progress_length >= 6:
                    branch_field = current_progress_array[5]
                    if len(branch_field) >= 0:
                        is_form_mode = False
                        if current_progress_length >= 7:
                            if current_progress_array[6] == 'form':
                                is_form_mode = True

                        if is_form_mode:
                            # fill personal info.
                            ret = fill_personal_info(driver, config_dict)
                        else:
                            # select date.
                            ret = inline_reg(driver, config_dict)


if __name__ == "__main__":
    main()
