import argparse
from selenium import webdriver

CHROME_EXECUTABLE_PATH = r"C:\Users\Yoav\Desktop\chromedriver.exe"


class Yad2:
	USERNAME_TEXTBOX_ID = 'userName'
	PASSWORD_TEXTBOX_ID = 'password'
	SUBMIT_FORM_ID = 'submitLogonForm'
	ADS_PAGE_LINK_TEXT = u'מכירות'
	LOGIN_URL = 'https://my.yad2.co.il/login.php'

	def __init__(self):
		self._driver = webdriver.Chrome(executable_path=CHROME_EXECUTABLE_PATH)
		self._driver.maximize_window()

	def login(self, email, password):
		self._driver.get(Yad2.LOGIN_URL)
		username_textbox = self._driver.find_element_by_id(Yad2.USERNAME_TEXTBOX_ID)
		password_textbox = self._driver.find_element_by_id(Yad2.PASSWORD_TEXTBOX_ID)
		submit_button = self._driver.find_element_by_id(Yad2.SUBMIT_FORM_ID)
		username_textbox.send_keys(email)
		password_textbox.send_keys(password)
		submit_button.click()

	def _go_to_ads_page(self):
		self._driver.find_element_by_partial_link_text(Yad2.ADS_PAGE_LINK_TEXT).click()

	def _open_all_ads(self):
		rows = self._driver.find_elements_by_tag_name('tr')
		item_rows = [row for row in rows if len(row.find_elements_by_tag_name('td')) > 3]
		for item_row in item_rows:
			item_row.click()

	def bounce_all_ads(self):
		self._go_to_ads_page()
		self._open_all_ads()

		frames = self._driver.find_elements_by_tag_name('iframe')
		for frame in frames:

			self._driver.switch_to.frame(frame)
			try:
				btn = self._driver.find_element_by_id('bounceRatingOrderBtn')
				btn.click()
				print('Bounced Ad!')
			except Exception:
				pass

			self._driver.switch_to.default_content()


def get_arguments():
	parser = argparse.ArgumentParser()
	parser.add_argument('email')
	parser.add_argument('password')
	return parser.parse_args()


def main():
	credentials = get_arguments()
	yad2 = Yad2()
	yad2.login(credentials.email, credentials.password)
	yad2.bounce_all_ads()

if __name__ == '__main__':
	main()