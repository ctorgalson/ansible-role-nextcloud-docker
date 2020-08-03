import os

import testinfra.utils.ansible_runner

import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.mark.parametrize('string,existence', [
    ('POSTGRES_DB=nextcloud', True),
    ('POSTGRES_PASSWORD=postgres-password', True),
    ('POSTGRES_USER=nextcloud', True),
])
def test_docker_db_env_file(host, string, existence):
    f = host.file('/tmp/nextcloud/db.env')

    assert f.exists
    assert f.is_file
    assert existence is (string in f.content_string)


@pytest.mark.parametrize('string,existence', [
    ('443', False),
    ('cert', False),
    ('letsencrypt', False),
    ('POSTGRES_HOST=db', True),
    ('REDIS_HOST=redis', True),
    ('REDIS_HOST_PASSWORD=redis-host-password', True),
    ('REDIS_HOST_PORT=6379', True),
    ('VIRTUAL_HOST=instance', True),
])
def test_docker_compose_file(host, string, existence):
    f = host.file('/tmp/nextcloud/docker-compose.yml')

    assert f.exists
    assert f.is_file
    assert existence is (string in f.content_string)


@pytest.mark.parametrize('container', [
    'nextcloud_app_1',
    'nextcloud_cron_1',
    'nextcloud_db_1',
    'nextcloud_redis_1',
    'nextcloud_proxy_1',
])
def test_docker_container_status(host, container):
    c = 'docker ps --all --quiet --format "{{.Names}}" --filter status=running'
    r = host.run(c)

    assert container in r.stdout


@pytest.mark.parametrize('network', [
    'nextcloud_default',
    'nextcloud_proxy-tier',
])
def test_docker_network_status(host, network):
    c = 'docker network ls --quiet --format "{{.Name}}"'
    r = host.run(c)

    assert network in r.stdout


@pytest.mark.parametrize('volume', [
    'nextcloud_db',
    'nextcloud_html',
    'nextcloud_nextcloud',
    'nextcloud_vhost.d',
])
def test_docker_volume_status(host, volume):
    c = 'docker volume ls --quiet'
    r = host.run(c)

    assert volume in r.stdout
