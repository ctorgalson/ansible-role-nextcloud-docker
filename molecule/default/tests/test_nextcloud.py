import os

import testinfra.utils.ansible_runner

import pytest

import re

import json

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('trusted_domain', [
  'localhost',
  'instance',
])
def test_nextcloud_trusted_domains(host, trusted_domain):
    c = ('docker exec --user www-data nextcloud_app_1 php occ '
         'config:system:get trusted_domains')
    r = host.run(c)

    assert trusted_domain in r.stdout


@pytest.mark.parametrize('config_line', [
  '\'dbtype\' => \'pgsql\','
])
def test_nextcloud_configuration(host, config_line):
    c = ('cat '
         '/var/lib/docker/volumes/nextcloud_nextcloud/_data/config/config.php')
    r = host.run(c)

    assert config_line in r.stdout


def test_nextcloud_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ status --output=json')
    r = host.run(c)
    n = json.loads(r.stdout)

    assert n['installed']


def test_nextcloud_encryption_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ encryption:status --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)

    assert e['enabled']


def test_nextcloud_encryption_module_status(host):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ app:list --output=json')
    r = host.run(c)
    e = json.loads(r.stdout)
    p = re.compile('\\d+\\.\\d+\\.\\d+')

    assert p.match(e['enabled']['encryption'])


def test_nextcloud_crontab_task(host):
    c = 'docker exec nextcloud_cron_1 crontab -l'
    c = ('docker exec --user www-data nextcloud_cron_1 '
         'busybox cat /var/spool/cron/crontabs/www-data')
    r = host.run(c)

    assert 'php -f /var/www/html/cron.php' in r.stdout


@pytest.mark.parametrize('property,result', [
    ('redis', 'host: redis'),
    ('memcache.distributed', '\\OC\\Memcache\\Redis'),
])
def test_nextcloud_redis_config(host, property, result):
    c = ('docker exec --user www-data nextcloud_app_1 '
         'php occ config:system:get {}'.format(property))
    r = host.run(c)

    assert result in r.stdout
