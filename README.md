:WIP: Граф роликов с pornhub.com и их перелинковка между собой 
---
[![Build Status](https://travis-ci.org/esemi/pornhub-graph.svg?branch=master)](https://travis-ci.org/esemi/pornhub-graph)


### todo
- обновить зависимости
- poetry
- доверстать на фрилансерах
- ga/metric 
- хабр/медиум - статья
- ссылка на паблик
- удалить дампы из гита


### Local run
```bash
$ cd backend
$ ./crawler.py -c2 -i1 10
$ ./crawler.py --continue -c2 -i1000 10
$ ./optional_info_fetch.py
$ ./export_dot.py -d 5

$ gephi process and export w/ sigmajs plugin

$ ./post_process.py
```
