import os
import re
import time
import pyperclip
import Xlib.display
from pathlib import Path
from typing import List, Tuple, Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from backend.server import process_bank_payments, parse_bank_payments
from backend.helper.utils import get_hash
from backend.helper.my_types import ImageWhatsappDownload
from backend.helper.my_types import SubscriptionRequestList
from backend.helper.my_types import ParseBankPaymentRequestList
from webdriver_manager.chrome import ChromeDriverManager
from frontend.config import CHROME_PROFILE, CHROME_VERSION
from pyvirtualdisplay.display import Display
from frontend.config import DISPLAY_WIDTH, DISPLAY_HEIGHT
from webdriver_manager.chrome import ChromeDriverManager
from keyboard import press_and_release
# from pyautogui import hotkey, press, scroll

print(os.environ)
SIZE = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
# display = Display(visible=True, size=SIZE, backend="xvfb", use_xauth=True)
# display.start()
#pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])


def extract_phone(chat_bubble):
    phone_pattern = r'\+?\d{0,3}[-\s\(]?\d{3}[-\s\)]?\d{3}[-\s]?\d{4}'
    phone_number = re.search(phone_pattern, chat_bubble)
    return phone_number.group() if phone_number else None


def extract_img_url(img_bubble):
    img_url_pattern = r'(blob)+(.)+?(")'
    img_url = re.search(img_url_pattern, img_bubble)
    return img_url.group()[:-1] if img_url else None


def extract_username(chat_bubble):
    username_pattern = r'(edeob0r2)+(.)+?(</span>)'
    username = re.search(username_pattern, chat_bubble)
    if not username: return None

    start = username.group().find('>')+1
    return username.group()[start:-7]


def extract_msg_time(chat_bubble):
    msg_time_pattern = r'(l7jjieqr)+(.)+?(</span>)'
    msg_time_match = re.finditer(msg_time_pattern, chat_bubble)
    msg_time = [x.group() for x in msg_time_match].pop()
    if not msg_time: return None

    start = msg_time.find('>')+1
    return msg_time[start:-7]


def extract_info(chat, group_name):
    phone, user = extract_phone(chat), extract_username(chat)
    img_url, msg_time = extract_img_url(chat), extract_msg_time(chat)
    local_path = get_file_path(phone, user, group_name)
    return phone, user, img_url, msg_time, local_path


def get_image_directory(group):
    parent_dir = os.path.join(os.getcwd(), "img_download")
    year, month, day = time.strftime("%Y"), time.strftime("%b"), time.strftime("%d")
    image_directory = os.path.join(parent_dir, group, year, month, day)
    os.makedirs(image_directory, exist_ok=True)
    return image_directory


def get_file_path(phone, user, group):
    filename = f"{phone or user}{time.strftime('_%H_%M_%S')}.jpeg"
    return os.path.join(get_image_directory(group), filename)


def clear_text(element):
    element.send_keys('')
    press_and_release('ctrl+a')
    time.sleep(0.4)
    press_and_release('delete')


def send_multi_line(lines, element):
    clear_text(element)
    for line in lines:
        element.send_keys(line)
        press_and_release('shift+enter')
    time.sleep(0.3)
    press_and_release('enter')


def get_options():
    options = Options()
    # options.headless = True
    options.accept_insecure_certs = True
    options.browser_version = CHROME_VERSION
    options.add_argument(CHROME_PROFILE)
    options.add_argument('--disable-gpu')
    options.add_argument(f'--window-size={DISPLAY_WIDTH}x{DISPLAY_HEIGHT}')
    options.add_argument('--no-sandbox')
    options.add_argument('--enable-logging')
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-dev-shm-usage")
    return options


class WhatsAppDriver:
    def __init__(self, url, group_name):

        self.group_name, options = group_name, get_options()
        chrome_driver_path = ChromeDriverManager().install()
        self.browser = Chrome(service=Service(chrome_driver_path), options=options)

        _, _ = self.browser.get(url), self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 28)
        group_xpath = f"//span[contains(text(),'{group_name}')]"
        # self.browser.save_screenshot(os.path.join(os.getcwd(), "2.png"))
        self.group_chat = self.wait.until(EC.element_to_be_clickable((By.XPATH, group_xpath)))
        #pyautogui.moveTo(DISPLAY_WIDTH//2, DISPLAY_HEIGHT//2)

    def __del__(self):
        self.browser.quit()
        # self.display.stop()

    def get_chat_row(self):
        chat_row_xpath = r'//div[@role="row"]'
        row = self.wait.until(EC.element_to_be_clickable((By.XPATH, chat_row_xpath)))
        return row

    def select_chat_row(self):
        chat_row = self.get_chat_row()
        chat_row.click()
        time.sleep(0.5)

    def get_auto_scroll(self):
        auto_scroll_xpath = r'//div[@aria-label="Scroll to bottom"]'
        wait = WebDriverWait(self.browser, 9)
        auto_scroll = wait.until(EC.element_to_be_clickable((By.XPATH, auto_scroll_xpath)))
        return auto_scroll

    def scroll_bottom_chat(self):
        try:
            self.get_auto_scroll().click()
        except TimeoutException:
            self.select_chat_row()
            for _ in range(5):
                press_and_release('page down')
        finally:
            time.sleep(0.5)

    def scroll_up_chat(self):
        time.sleep(0.2)
        self.select_chat_row()
        for _ in range(5):
            press_and_release('page up')
        time.sleep(0.3)

    def right_click_element(self, element):
        actions = ActionChains(self.browser)
        actions.context_click(element).perform()
        time.sleep(1)

    def open_tab(self, image_url):
        self.browser.execute_script("window.open('', '_blank');")
        self.browser.switch_to.window(self.browser.window_handles[1])
        self.browser.get(image_url)
        time.sleep(2)

    def close_tab(self):
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[0])

    def new_tab_operation(self, url, func, *args, **kwargs):
        self.open_tab(url)
        func(*args, **kwargs)
        self.close_tab()

    def open_group_chat(self):
        search_box_xpath = r'//div[@contenteditable="true"][@data-tab="3"]'
        search_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, search_box_xpath)))
        search_box.send_keys(self.group_name)
        time.sleep(1.3)
        self.group_chat.click()
        self.scroll_bottom_chat()

    def save_image(self, file_path):
        body = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//body")))
        self.right_click_element(body)
        press_and_release('down')
        press_and_release('down')
        press_and_release('enter')
        pyperclip.copy(file_path)
        time.sleep(2.5)
        press_and_release('ctrl+v')
        press_and_release('enter')

    def get_images_elements(self):
        def is_image(chat_bubble):
            txt = chat_bubble.get_attribute('innerHTML')
            return bool(re.search('.*src="blob:http.+', txt))

        time.sleep(2.6)
        images_xpath = "//div[contains(@class,'cm280p3y')]"
        elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, images_xpath)))
        images_elements = list(filter(is_image, elements))
        print(f"There are {len(images_elements)} images found")
        return images_elements

    def get_images_html(self):
        images_elements = self.get_images_elements()
        images_html = [x.get_attribute('innerHTML') for x in images_elements]
        return images_html

    def download_image(self, message) -> ImageWhatsappDownload:
        phone, username, image_url, msg_time, local_path = extract_info(message, self.group_name)
        self.new_tab_operation(image_url, self.save_image, local_path)

        time.sleep(3.1)
        if not os.path.exists(local_path):
            print(f"Unable user:{phone or username} to download img: {image_url} to {local_path}")
            return None

        print(f"phone: {phone}, username: {username}, image_url: {image_url}, local_path: {local_path}")
        img_hash = get_hash(local_path)
        return ImageWhatsappDownload(phone, username, local_path, msg_time, img_hash)

    def download_images(self) -> List[ImageWhatsappDownload]:
        img_info = [self.download_image(msg) for msg in self.get_images_html()]
        return img_info

    def delete_element(self, element):
        self.right_click_element(element)
        time.sleep(2)

    def delete_elements(self, elements):
        for element in elements:
            self.delete_element(element)

    # move to backend
    @staticmethod
    def not_subscribed(ele_html):
        _, txt = ele_html
        phone, user = extract_phone(txt), extract_username(txt)
        # if phone/user not in db return false
        return bool(phone or user)

    def delete_unsubscribed_images(self):
        ele_html = zip(self.get_images_elements(), self.get_images_html())
        unsubscribed_ele_html = list(filter(WhatsAppDriver.not_subscribed(), ele_html))
        unsubscribed_elements = [ele for ele, html in unsubscribed_ele_html]
        self.delete_elements(unsubscribed_elements)

    def get_chat_box(self):
        chat_box_xpath = r'//div[@contenteditable="true"][@tabindex="10"]'
        chat_box = self.wait.until(EC.element_to_be_clickable((By.XPATH, chat_box_xpath)))
        return chat_box

    def reply_customer_img(self, response):
        self.open_img_dialog(response)
        press_and_release('down')
        press_and_release('enter')

    def send_customer_responses(self, response):
        time.sleep(0.5)
        chat_box = self.get_chat_box()
        for res in response.res_list:
            if not res:
                continue
            lines = res.txt.split('\n')
            send_multi_line(lines, chat_box)
        time.sleep(2)


def run():
    whatsapp_handler = WhatsAppDriver("https://web.whatsapp.com/", group_name="Test Buyers")
    whatsapp_handler.open_group_chat()
    whatsapp_handler.scroll_up_chat()
    time.sleep(5)
    images: List[ImageWhatsappDownload] = whatsapp_handler.download_images()
    whatsapp_handler.scroll_bottom_chat()
    parsedPaymentRes = parse_bank_payments(ParseBankPaymentRequestList(images))
    whatsapp_handler.send_customer_responses(parsedPaymentRes)
