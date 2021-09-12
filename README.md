:WIP: Граф роликов с pornhub.com и их перелинковка между собой 
---
[![Build Status](https://travis-ci.org/esemi/pornhub-graph.svg?branch=master)](https://travis-ci.org/esemi/pornhub-graph)


### todo
- travis+fabric -> actions
- доверстать на фрилансерах
- ga/metric 
- хабр/медиум - статья
- ссылка на паблик


### Local run
```bash
$ git clone
$ cd pornhub-graph
$ python3.9 -m venv venv
$ source venv/bin/activate
$ pip install poetry
$ poetry config virtualenvs.create false --local
$ poetry install
$ poetry run python backend/crawler.py -c2 -i1 10
$ poetry run python backend/crawler.py --continue -c2 -i1000 10
$ poetry run python backend/optional_info_fetch.py
$ poetry run python backend/export_dot.py -d 5

### gephi process and export w/ sigmajs plugin

$ poetry run python backend/post_process.py

### deploy
```
