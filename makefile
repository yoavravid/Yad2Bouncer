
run:
	python src/main.py bin/chromedriver dimulka.75@gmail.com October123

chromedrive:
	mkdir -p bin
	wget -P ./bin/ https://chromedriver.storage.googleapis.com/2.43/chromedriver_linux64.zip
	unzip bin/chromedriver_linux64.zip -d bin
	rm bin/chromedriver_linux64.zip

