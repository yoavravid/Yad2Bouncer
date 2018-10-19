import argparse
from yad2 import Yad2


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