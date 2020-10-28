
database_files = webapp.db


.PHONY : make_stage \
	run \
	install_python_modules \
	make_migration \
	apply_migration \
	apply_fixture \
	clean

# Установить все необходимые компонеты сервера - модули Python, пустую Базу
# Данных, загрузить в БД некий минимальный набор данных (фикстуру).
make_stage: install_python_modules apply_fixture

# Запуск проекта.
# Запускает на локальном компьюетер веб-сервер который можно использовать для
# тестов.
run:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask run

# Установить необходимые модули Python.
install_python_modules:
	pip3 install -r requirements.txt

# Создаёт миграцию на основе текущего состояния Базы Данных.
make_migration:
	# Устанавливаем дефолтное состояние для make-парааметра в положение "". При
	# вызове make_migration или любого рецепта который её требует, вы можете
	# изменить параметр comment вот так:
	# make make_migration comment=abc
	$(eval comment=) \
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask db migrate -m '$(comment)'

# Применяет самую свежую миграцию к Базе Данных.
apply_migration:
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	flask db upgrade

# Удаляет текущую БД. Насмерть, окончательно.
# Создаёт заново пустую БД со структурой на основе миграции.
# Загружает фикстуру в БД.
apply_fixture: clean apply_migration
	# Устанавливаем дефолтное состояние для make-парааметра в положение "". При
	# вызове apply_fixture или любого рецепта который её требует, вы можете
	# изменить параметр fixture вот так:
	# make apply_fixture fixture=abc
	$(eval fixture=) \
	export FLASK_APP=webapp && \
	export FLASK_ENV=development && \
	python3 load_fixture.py $(fixture)

# Уничтожаем все файлы которые умеет делать этот makefile.
clean :
	rm -f ${database_files}
