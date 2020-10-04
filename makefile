
database_files = webapp.db

.PHONY : make_stage \
	run \
	make_freshest_migration \
	apply_migration \
	clean

# Подготовить сервер к запуску.
make_stage:
	pip3 install -r requirements.txt
	rm -f ${database_files} && \
	export FLASK_APP=webapp && \
	export FLASK_ENV= && \
	flask db upgrade

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

# Уничтожаем все файлы которые умеет делать этот makefile.
clean :
	rm -f ${database_files}
