
django-rossvyaz
===============

Приложение содержит:

* Таблица данных привязки номера телефона к региону (только Россия - РФ), взятая из Россвязи (Федеральное агенство связи);
* Система импорта из разных источников (Сейчас есть только для диапозона DEF);
* Небольшой QuerySet Manager;

Установка
---------

Проделываем в командной строке ::

  $ git clone git://github.com/satels/django-rossvyaz.git
  $ cd django-rossvyaz
  $ python setup.py install

Потом следует добавить 'django_rossvyaz' в INSTALLED_APPS и выполнить ::

  $ python manage.py syncdb  # Django < 1.7
  $ python manage.py migrate django_rossvyaz  # Django >= 1.7

Настройка
---------

Добавить app в settings.py ::

  INSTALLED_APPS = [
      ..
      'django_rossvyaz',
      ..
  ]

Необязательные параметры (в settings.py):

* ROSSVYAZ_CODING - дефолтная кодировка файла с таблицей от РосСвязи (по-умолчанию windows-1251).
* ROSSVYAZ_SOURCE_URLS - ссылки на файлы на сайте-источнике (сейчас по-умолчанию только DEF диапозон)
* ROSSVYAZ_SEND_MESSAGE_FOR_ERRORS - отправлять ли сообщения об ошибках на почту при обновлении (по-умолчание, True)

Использование
-------------

Для получения объекта (для определения региона) ::

  from __future__ import print_function, unicode_literals
  from django_rossvyaz.logic import clean_phone, CleanPhoneError
  from django_rossvyaz.models import PhoneCode

  try:
      phone = clean_phone('89687298907', PhoneCode.PHONE_TYPE_DEF)
  except CleanPhoneError as e:
      raise e

  phonecodes = PhoneCode.objects.by_phone(phone)
  if phonecodes.exists():
      for num, phonecode in enumerate(phonecodes.iterator()):
          print('Найден #{}'.format(num + 1))
          print(phonecode.first_code)  # 968
          print(phonecode.from_code, phonecode.to_code)  # Диапозон кодов (В этом примере: '3500000'-'7999999')
          print(phonecode.block_size)  # Кол-во номеров в диапозоне (4500000)
          print(phonecode.operator)  # Оператор связи ('ВымпелКом')
          print(phonecode.region)  # Код региона (или название региона) (77)
          print(phonecode.phone_type)  # 'def'

Пример использования через Postgres SQL ::

        SELECT
            regioncode.region_name AS region_name
        FROM
            phones_phone AS phone,
            django_rossvyaz_phonecode AS phonecode,
            regions_regioncode AS regioncode
        WHERE
            regioncode.region_id = phonecode.region AND
            substring(phone.phone from 3 for 3) = phonecode.first_code AND
            substring(phone.phone from 6 for 8)::int >= phonecode.from_code::int AND
            substring(phone.phone from 6 for 8)::int <= phonecode.to_code::int AND
            phone.id = 5
        ORDER BY block_size ASC;

Обновления базы
---------------

Чтобы обновить базу ::

  $ python manage.py rossvyaz_update --phone-type=def --clean-region
  
Рекомендуется обновлять базу с кодами отсюда: https://zniis.ru/bdpn/tablitsa-marshrutnykh-nomerov/router-table - скачивается файл XLSX, форматируете в CSV формат (можно использовать этот сервис для форматирования: https://www.kontrolnaya-rabota.ru/convert/xlsx2csv/): **zniis.csv**  ::

  $ python manage.py rossvyaz_update --phone-type=def --encoding='utf-8' --filename=/path/to/zniis.csv

Готовое API
-----------

* Но номеру: https://calltools.ru/lk/cabapi_external/api/v1/def_codes/by_phone/?phone=9687298907
* Вся база: https://calltools.ru/lk/cabapi_external/api/v1/def_codes/all/
