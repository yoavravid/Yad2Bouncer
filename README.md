# Yad2 Bouncer
A script for bouncing Yad2 ads.
The script runs in 2 ways:
* Windows mode - runs with a normal chrome instance
* Linux mode - runs with a headless chrome instance (without GUI)

# Usage
In order to run the script execute for next command:

## Linux
```
make EMAIL=<username> PASSWORD=<password> run
```

## Windows
```
python3 src\main.py <chrome_drive> <username> <password>
```

# Requirements
* Python 3
* Pip
* Python packages
	+ Run `pip3 install -r requirements.txt`
* Chrome driver
	+ For linux run `make chromedrive`
    + Download at https://sites.google.com/a/chromium.org/chromedriver/home.
