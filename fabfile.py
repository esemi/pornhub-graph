#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from shutil import copy, rmtree, copytree

from fabric.api import cd, env, run, local, lcd, put
from fabric.contrib.files import exists


env.user = 'esemi'
env.app_env = 'default'
env.hosts = ['35.204.15.134']

BUILD_FILENAME = 'build.tar.gz'
BUILD_FOLDERS = ['data', 'www']
BUILD_FILES = []
LOCAL_APP_PATH = os.path.dirname(__file__)
LOCAL_BUILD_PATH = os.path.join(LOCAL_APP_PATH, 'build')
LOCAL_BUILD_BUNDLE = os.path.join(LOCAL_APP_PATH, BUILD_FILENAME)

REMOTE_HOME_PATH = os.path.join('/home', env.user)
APP_PATH = os.path.join(REMOTE_HOME_PATH, 'semhub')
DEPLOY_PATH = os.path.join(REMOTE_HOME_PATH, 'semhub-deploy')
BACKUP_PATH = os.path.join(REMOTE_HOME_PATH, 'semhub-backup')


def deploy():
    # init remote host
    if not exists(APP_PATH):
        run('mkdir -p %s' % APP_PATH)

    if os.path.exists(LOCAL_BUILD_PATH):
        rmtree(LOCAL_BUILD_PATH)
    os.mkdir(LOCAL_BUILD_PATH)
    for folder in BUILD_FOLDERS:
        copytree(os.path.join(LOCAL_APP_PATH, folder), os.path.join(LOCAL_BUILD_PATH, folder))
    for filename in BUILD_FILES:
        copy(os.path.join(LOCAL_APP_PATH, filename), os.path.join(LOCAL_BUILD_PATH, filename))
    with lcd(LOCAL_BUILD_PATH):
        local('find . -name \*.pyc -delete')
        local('tar -czf %s .' % LOCAL_BUILD_BUNDLE)
    rmtree(LOCAL_BUILD_PATH)

    # load build
    if exists(DEPLOY_PATH):
        run('rm -rf %s' % DEPLOY_PATH)
    run('mkdir -p %s' % DEPLOY_PATH)
    put(LOCAL_BUILD_BUNDLE, DEPLOY_PATH)

    with cd(DEPLOY_PATH):
        run('tar -xzf %s' % BUILD_FILENAME)

    # deploy (move build to production)
    if exists(BACKUP_PATH):
        run('rm -rf %s' % BACKUP_PATH)
    run('mv %s %s' % (APP_PATH, BACKUP_PATH))
    run('mv %s %s' % (DEPLOY_PATH, APP_PATH))
    run('chown -R %s:www-data %s' % (env.user, APP_PATH))
    run('chmod -R 755 %s' % APP_PATH)
