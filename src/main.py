import argparse
from yad2 import Yad2


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('driver_path')
    parser.add_argument('email')
    parser.add_argument('password')
    return parser.parse_args()


def main():
    arguments = get_arguments()
    yad2 = Yad2(arguments.driver_path)
    try:
        yad2.login(arguments.email, arguments.password)
        yad2.bounce_all_ads()
    except:
        yad2.get_screenshot_as_file('error.png')
        raise


if __name__ == '__main__':
    main()
