#! /usr/bin/env python
# -*- coding: utf-8 -*-


if __name__ == '__main__':
    with open('../www/data.json', 'r', encoding='utf-8') as src:
        content = src.read()
        content = content.replace('\\u0026amp;', '&').replace('\\u0026nbsp;', '')
        with open('../www/data-prepared.json', 'w+', encoding='utf-8') as dst:
            dst.write(content)

