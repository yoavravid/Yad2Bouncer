# coding=utf-8
import logging
from selenium import webdriver
from contextlib import contextmanager
from sys import platform


class Yad2Error(Exception):
    pass


class Yad2:
    USERNAME_TEXTBOX_ID = 'userName'
    PASSWORD_TEXTBOX_ID = 'password'
    SUBMIT_FORM_ID = 'submitLogonForm'
    ADS_PAGE_LINK_TEXT = u'מכירות'
    LOGIN_URL = 'https://my.yad2.co.il/login.php'

    def __init__(self, executable_path):
        options = webdriver.ChromeOptions()
        if platform == "linux" or platform == "linux2":
            options.binary_location = '/usr/bin/google-chrome-stable'
            options.add_argument('headless')
        self._driver = webdriver.Chrome(executable_path=executable_path, options=options)
        logger_handler = logging.FileHandler('yad2.log')
        logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(logger_formatter)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logger_handler)

    def login(self, email, password):
        self._logger.info('Started login')
        self._driver.get(Yad2.LOGIN_URL)
        username_textbox = self._driver.find_element_by_id(Yad2.USERNAME_TEXTBOX_ID)
        password_textbox = self._driver.find_element_by_id(Yad2.PASSWORD_TEXTBOX_ID)
        submit_button = self._driver.find_element_by_id(Yad2.SUBMIT_FORM_ID)
        username_textbox.send_keys(email)
        password_textbox.send_keys(password)
        submit_button.click()
        self._logger.info('Finished login')

    def iterate_categories(self):
        visited_categories = list()
        while True:
            # Obtain the list of categories
            link_containers = self._driver.find_elements_by_class_name('links_container')
            if len(link_containers) != 1:
                raise Yad2Error('Failed to find a single link container')

            for category_link in link_containers.pop().find_elements_by_class_name('catSubcatTitle'):
                if category_link.text not in visited_categories:
                    visited_categories.append(category_link.text)
                    # Clicking the category will direct us to its page
                    category_text = category_link.text
                    category_link.click()
                    yield category_text
                    # After clicking a category we need to obtain the reloaded category list
                    break
            else:
                # All category links where visited
                break

    def iterate_ads(self):
        for item_row in self._driver.find_elements_by_class_name('item'):
            yield item_row

    def bounce_all_ads(self):
        for category_text in self.iterate_categories():
            self._logger.info(u'Opened category: ' + category_text)
            for ad in self.iterate_ads():
                with self.enter_ad(ad):
                    bounce_button = self._driver.find_element_by_id('bounceRatingOrderBtn')
                    if bounce_button.value_of_css_property('background').startswith(u'rgb(204, 204, 204)'):
                        self._logger.info('Button is disabled')
                    else:
                        bounce_button.click()
                        self._logger.info('Bounced Ad!')

    @contextmanager
    def enter_ad(self, ad):
        # Open the ad
        ad.click()
        ad_content_frames = self._driver.find_elements_by_tag_name('iframe')
        # Find the iframe of the ad by ad's orderid
        ad_content_frames = filter(
            lambda e: e.get_attribute('src').endswith(u'OrderID=' + ad.get_attribute('data-orderid')),
            ad_content_frames
        )
        if len(ad_content_frames) != 1:
            raise Yad2Error('Failed to find a single iframe')

        with self.enter_iframe(ad_content_frames.pop()):
            yield
        # Close the ad
        ad.click()

    @contextmanager
    def enter_iframe(self, iframe):
        self._driver.switch_to.frame(iframe)
        yield
        self._driver.switch_to.default_content()

    def get_screenshot_as_file(self, filename):
        self._driver.get_screenshot_as_file(filename)

