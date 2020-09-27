# Freelance Exchange (webapp)

Это - репозиторий дипломного проекта нашей команды! Как дипломный проект, мы
делаем сайт-биржу фриланса. На бирже фриланса, посетители-Заказчики могут
размещать на Доске Объявлений свои заказы и находить посетителей-Фрилансеров
которые смогут эти заказы воплощать в жизнь.

Установка тестового сервера
---------------------------

Склонируйте себе этот Git-репозиторий:\
`git clone https://github.com/SagirovVitaliy/web_project.git`\

Установите зависимости:\
Из папки-корня проекта (туда где лежит README.md) запустите команду:\
Для Windows:\
`pip install -r requirements.txt`\
Для Mac или Linux:\
`pip3 install -r requirements.txt`

Запуск тестового сервера
------------------------

Из папки-корня проекта (туда где лежит README.md) запустите команду:\
На Windows:\
`export FLASK_APP=webapp && export FLASK_ENV=development && set FLASK_DEBUG=1 && flask run`\
На Mac или Linux:\
`export FLASK_APP=webapp && export FLASK_ENV=development && flask run`

После того как сервер запущен, войдите в браузер и перейдите на ссылку
http://localhost:5000 \
Поздравляем, вы зашли на главную страницу нашего тестового сервера!
