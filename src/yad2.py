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
    LOGOUT_BUTTON_CLASS = 'logout'
    LOGIN_URL = 'https://my.yad2.co.il/login.php'
    PERSONAL_AREA_URL = 'https://my.yad2.co.il//newOrder/index.php?action=personalAreaIndex'
    AD_DETAILS_MAX_LEN = 64

    def __init__(self, executable_path=None):
        options = webdriver.ChromeOptions()
        if platform == "linux" or platform == "linux2":
            options.binary_location = '/usr/bin/google-chrome-stable'
            options.add_argument('headless')

        chrome_kwargs = {'options': options}

        if executable_path is not None:
            chrome_kwargs['executable_path'] = executable_path

        self._driver = webdriver.Chrome(**chrome_kwargs)
        self._create_logger('yad2.log')

    def _create_logger(self, logfile):
        logger_handler = logging.FileHandler(logfile, encoding='utf8')
        logger_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logger_handler.setFormatter(logger_formatter)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logger_handler)

    @contextmanager
    def login(self, email, password):
        self._logger.info('Logging in to %s', email)
        self._login(email, password)
        self._logger.info('Logged in to %s', email)
        try:
            yield
        finally:
            self._logger.info('Logging out from %s', email)
            self._logout()
            self._logger.info('Logged out from %s', email)

    def _login(self, email, password):
        self._driver.get(Yad2.LOGIN_URL)
        username_textbox = self._driver.find_element_by_id(Yad2.USERNAME_TEXTBOX_ID)
        password_textbox = self._driver.find_element_by_id(Yad2.PASSWORD_TEXTBOX_ID)
        submit_button = self._driver.find_element_by_id(Yad2.SUBMIT_FORM_ID)
        username_textbox.send_keys(email)
        password_textbox.send_keys(password)
        submit_button.click()
        if self._driver.current_url != Yad2.PERSONAL_AREA_URL:
            self._raise_error('Login failed for {}'.format(email))

    def _logout(self):
        logout_button = self._driver.find_element_by_class_name(Yad2.LOGOUT_BUTTON_CLASS)
        logout_button.click()
        with self.enter_alert() as alert:
            alert.accept()

    def iterate_categories(self):
        """
        Iterates over all the available categories.
        Every available category in entered and its name is yielded.
        Note:
        Every time a category is selected the page changes - this invalidates all the object that represent
        elements in the page, therefor every time a category is selected all the categories should be
        queried again and iterated until all the categories where visited.
        """
        visited_categories = list()
        iterated_all_categories = False
        while not iterated_all_categories:
            # Obtain the list of categories
            link_containers = self._driver.find_elements_by_class_name('links_container')
            if len(link_containers) != 1:
                self._raise_error('Failed to find a single link container')

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
                iterated_all_categories = True

    def iterate_ads(self):
        return (ad for ad in self._driver.find_elements_by_class_name('item'))

    def bounce_all_ads(self):
        for category_text in self.iterate_categories():
            self._logger.info(u'Opened category: ' + category_text)
            for ad in self.iterate_ads():
                ad_status = ad.find_element_by_class_name('status_wrapper')
                if ad_status.text == u'פג תוקף':
                    ad_text = ad.find_element_by_class_name('textArea').text
                    self._logger.info('The following ad is out dated: %s', ad_text)
                    continue

                with self.enter_ad(ad):
                    ad_details = self._driver.find_element_by_class_name('details_area').text.strip().replace('\n', ' ')
                    ad_details = (
                        ad_details[:Yad2.AD_DETAILS_MAX_LEN] if len(ad_details) <= Yad2.AD_DETAILS_MAX_LEN else
                        ad_details[:Yad2.AD_DETAILS_MAX_LEN-3] + '...'
                    )
                    self._logger.info('Handling ad: %s', ad_details)
                    bounce_button = self._driver.find_element_by_id('bounceRatingOrderBtn')
                    if bounce_button.value_of_css_property('background').startswith(u'rgb(204, 204, 204)'):
                        self._logger.info('Bounce button is disabled')
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
        ad_content_frames = list(ad_content_frames)
        if len(ad_content_frames) != 1:
            self._raise_error('Failed to find a single iframe')

        try:
            with self.enter_iframe(ad_content_frames.pop()):
                yield
        except Exception as exc:
            self._logger.error("Failed to handle ad: %s", str(exc))
        finally:
            # Close the ad
            ad.click()

    @contextmanager
    def enter_iframe(self, iframe):
        self._driver.switch_to.frame(iframe)
        try:
            yield
        finally:
            self._driver.switch_to.default_content()

    @contextmanager
    def enter_alert(self):
        try:
            yield self._driver.switch_to.alert
        finally:
            self._driver.switch_to.default_content()

    def get_screenshot_as_file(self, filename):
        self._driver.get_screenshot_as_file(filename)

    def _raise_error(self, error_message):
        self._logger.error(error_message)
        raise Yad2Error(error_message)
