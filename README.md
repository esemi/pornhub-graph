pornGraph 
---

Курлом парсится на ура, но после 40 запросов пытается мешать - выдаёт хтмл с кодом на яваскрипте, который некоторое время думает и только потом открывает тебе страничку.

Версия на пупитере, работает стабильно, ждёт тайтл на странице (обходит блокировку), но долго.

Открываем сразу несколько окон в пупитере, так выходит быстрее, но нарываемся на блокировку уже с 429 кодом (видимо считают количество запросов с ипишки).
Адекватный рейт только при 2 воркерах с одной ипишки, но больше времени на эксперименты не осталось =()



### todo
- ~Спарсить БД от топ10~
- ~Экспортнуть в файл (DOT https://gephi.org/users/supported-graph-formats/graphviz-dot-format/)~
- ~Распасовать в gephi~
- ~Полные названия~
- ~Отрисовать на sigmajs (10к вершин максимум)~
- ~Легенда цветов~
- ~Сохранение ссылки на граф (пул-реквест в плагин)~
- ~Ссылка на видео~
- ~Деплой в DO~ 
- ~https~
- Описание
- Корректный домен
- Логотип на главной + фавикон
- Вверстать
- Причесать код
- Хабр
- Кириллица
- Встроенное превью ?
- Встроенное видео ?
- hubtraffic ?



```bash
$ nohup ./backend/run_crawler_from_top.py --continue -c2 -i100 10

$ ./backend/export_dot.py -d 5

$ gephi handjob and export w/ sigmajs plugin

$ ./backend/post_process.py
```