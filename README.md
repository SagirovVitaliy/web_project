# Freelance Exchange (webapp)

Для того чтобы запустить наш замечательный проект-сервер локально (это может
быть удобно для тестироваания), вам потребуется выполнить следующие действия:

1. Установить на тестовый компьютер
- Python версии 3.8 - https://www.python.org/downloads/
- pip - https://pip.pypa.io/en/stable/installing/
- Git - https://git-scm.com/downloads

2. Теперь необходимо выбрать на компьютере место папку, в которую вы установите
наш замечательный проект. Допустим, вы решили установить проект в папку
**~/projects/**\
**Внимание!** Обязательно убедитесь что в этой папке (в примере это
**~/projects/**) нет дочерней папки web_project.\
Если дочерняя папка
**web_project** существует, вам необходимо принять решение как вам будет удобней
поступить:
- либо удалить её;
- либо найти на компьютере другое место куда вы установите текущий проект.

3. Теперь вы должны развернуть в этой папке копию нашего замечательного проекта.
Войдите в папку которую вы выбрали через командную строку и введите команду:\
`git clone https://github.com/SagirovVitaliy/web_project.git`\
Гит-репозиторий создан!

4. Через коммандную строку, войдите в папку проекта. В нашем примере это будет
**~/projects/web_project/**

5. Теперь необходимо создать виртуальное окружение. Оно нужно чтобы модули
Python которые вы установите в шаге 7 этой инструкции, были доступны только в
текущем проекте и не мешали вам в других проектах.\
Введите в коммандную строку:\
На Windows:\
`python -m venv env`\
На Mac или Linux:\
`python3 -m venv env`

6. Виртуальное окружение создано, но надо дать явную команду чтобы в него войти
и получить преимущества ради которых мы его устанавливали.\
Введите в коммандную строку:\
На Windows:\
`env\Scripts\activate`\
На Mac или Linux:\
`source env/bin/activate`\
(пометка - для того чтобы выйти из виртуального окружения, введите в коммандную
строку команду deactivate)

7. Теперь надо установить зависимости без которых этот сервер не может
работать.\
Введите в коммандную строку:\
`pip install -r requirements.txt`

8. Если все зависимости установлены успешно, можно запускать программу!\
Введите в коммандную строку:\
На Windows:\
`export FLASK_APP=webapp && export FLASK_ENV=development && set FLASK_DEBUG=1 && flask run`
На Mac или Linux:\
`export FLASK_APP=webapp && export FLASK_ENV=development && flask run`

9. Для того чтобы тестировать наш веб-сервер, войдите в браузер и перейдите на
ссылку http://localhost:5000 \
Поздравляем, вы зашли на главную страницу нашего тестового сервиса!
