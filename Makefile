install:
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

run:
	/etc/init.d/mongodb start
	sleep 2
	heroku local
