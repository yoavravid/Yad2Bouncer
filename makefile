run:
	python src/main.py bin/chromedriver ${EMAIL} ${PASSWORD}

install: chrome chromedriver
	sudo apt install unzip
	sudo apt install python-pip
	pip install -r requirements.txt

chrome:
	sudo apt-get install libxss1 libappindicator1 libindicator7
	wget -P ./bin/ https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
	sudo dpkg -i bin/google-chrome*.deb
	sudo apt-get install -f
	
chromedrive: bin/chromedriver
	mkdir -p bin
	wget -P ./bin/ https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip
	unzip bin/chromedriver_linux64.zip -d bin
	rm bin/chromedriver_linux64.zip
