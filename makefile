
database_files = webapp.db

.PHONY : make_stage \
	run \
	make_freshest_migration \
	apply_migration \
	load_initial_fixtures \
	clean

# Подготовить сервер к запуску.
make_stage:
	pip3 install -r requirements.txt && \
	rm -f ${database_files} && \
	export FLASK_APP=webapp && \
	export FLASK_ENV= && \
	flask db upgrade && \
	python3 load_fixture.py

# Запуск проекта.
# Запускает на локальном компьюетер веб-сервер который можно использовать для
# тестов.
run:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask run

# Создаёт миграцию на основе текущего состояния Базы Данных.
make_freshest_migration:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask db migrate

# Применяет самую свежую миграцию к Базе Данных.
apply_migration:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask db upgrade

# Загружает фикстуры в БД. Имеет смысл только если БД - чистая.
load_initial_fixtures:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	python3 load_fixture.py

# Уничтожаем все файлы которые умеет делать этот makefile.
clean :
	rm -f ${database_files}
