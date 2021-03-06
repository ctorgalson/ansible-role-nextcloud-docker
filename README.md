# Ansible Role Nextcloud Docker

[![Build Status](https://travis-ci.com/ctorgalson/ansible-role-nextcloud-docker.svg?branch=master)](https://travis-ci.com/ctorgalson/ansible-role-nextcloud-docker)

This role builds a Nexcloud instance on Ubuntu 18.04 using Docker containers.

The role (which should probably work on other Linux distros and releases) is based on [this helpful blog post at blog.ssdnodes.com](https://blog.ssdnodes.com/blog/installing-nextcloud-docker/).

## Requirements

This role uses [`docker_container_info` tasks](https://docs.ansible.com/ansible/latest/modules/docker_container_info_module.html#docker-container-info-module), and so requires [Ansible 2.8](https://docs.ansible.com/ansible/2.8/) or later.

## Role Variables

### nextcloud_config vars

These variables are used to configure the Nextcloud application itself. Some of them--such as e.g. the database variables--are also used in constructing the containers.

#### `nextcloud_config_allow_insecure_defaults`

This role ships with insecure default values, but will fail unless they're overridden, or this variable is explicitly set to allow insecure values. Always use long, random passwords and use [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) or similar tools if storing them in version-control systems.

    nextcloud_config_allow_insecure_defaults: false

#### `nextcloud_config_domain`

The principal domain that the Nextcloud instance will be accessed at.

    nextcloud_config_domain: "example.local"

#### `nextcloud_config_db_root_password`

The mariadb root password. This is an insecure default.

    nextcloud_config_db_root_password: "root"

#### `nextcloud_config_db_database`

The type of database engine to be used. This role is currently untested with othe db engines supported by Nextcloud.

    nextcloud_config_db_database: "mysql"

#### `nextcloud_config_db_database_name`

The name of the Nextcloud database.

    nextcloud_config_db_database_name: "nextcloud"

#### `nextcloud_config_db_database_user`

The name of the database user for the Nextcloud database.

    nextcloud_config_db_database_user: "nextcloud"

#### `nextcloud_config_db_database_password`

The Nextcloud database password. This is an insecure default.

    nextcloud_config_db_database_password: "mysql"

#### `nextcloud_config_trusted_domains`

The list of trusted domains from which Nextcloud can be accessed.

    nextcloud_config_trusted_domains:
      - "localhost"
      - "{{ nextcloud_config_domain }}"

#### `nextcloud_config_admin_user`

The Nextcloud admin user name.

    nextcloud_config_admin_user: "admin"

#### `nextcloud_config_admin_password`

The nextcloud admin user password. This is an insecure default.

    nextcloud_config_admin_password: "pass"

#### `nextcloud_encryption_module`

The encryption module to use in Nextcloud.

    nextcloud_encryption_module: "encryption"

### nextcloud_app_container vars

These variables are used to configure the container that runs the Nextcloud application itself. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

    nextcloud_app_container_env:
      - key: "VIRTUAL_HOST"
        value: "{{ nextcloud_config_domain }}"
      - key: "LETSENCRYPT_HOST"
        value: "{{ nextcloud_config_domain }}"
      - key: "LETSENCRYPT_EMAIL"
        value: "{{ nextcloud_letsencrypt_container_email }}"

The list of environment vars for the Nextcloud App container including `LETSENCRYPT_*` if required. See `nextcloud_letsencrypt_enable`, below.

#### `nextcloud_app_container_image`

The specific Nextcloud container image to use.

    nextcloud_app_container_image: "nextcloud:latest"

#### `nextcloud_app_container_name`

The name for the running nextcloud container.

    nextcloud_app_container_name: "nextcloud-app"

#### `nextcloud_app_container_ports`

The ports exposed by the nextcloud _app_ (note: **not** the nginx proxy).

    nextcloud_app_container_ports:
      - "80"

#### `nextcloud_app_container_restart`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_app_container_restart: true

#### `nextcloud_app_container_state`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `started` setting for this container.

    nextcloud_app_container_state: started

#### `nextcloud_app_container_volumes`

Volumes for Nextcloud app container.

    nextcloud_app_container_volumes:
      - "nextcloud:/var/www/html"
      - "./app/config:/var/www/html/config"
      - "./app/custom_apps:/var/www/html/custom_apps"
      - "./app/data:/var/www/html/data"
      - "./app/themes:/var/www/html/themes"
      - "/etc/localtime:/etc/localtime:ro"

### nextcloud_mariadb_container vars

These variables are used to configure the container that runs mariadb. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

#### `nextcloud_mariadb_container_image`

The specific mariadb container image to use.

    nextcloud_mariadb_container_image: "mariadb"

#### `nextcloud_mariadb_container_name`

The name for the running mariadb container.

    nextcloud_mariadb_container_name: "nextcloud-mariadb"

#### `nextcloud_mariadb_container_restart`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_mariadb_container_restart: true

#### `nextcloud_mariadb_container_state`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `started` setting for this container.

    nextcloud_mariadb_container_state: started

#### `nextcloud_mariadb_container_volumes`

Volumes for mariadb app container.

    nextcloud_mariadb_container_volumes:
      - "db:/var/lib/mysql"
      - "/etc/localtime:/etc/localtime:ro"

#### `nextcloud_mariadb_container_env`

Environment variables for mariadb app container.

    nextcloud_mariadb_container_env:
      - key: "MYSQL_ROOT_PASSWORD"
        value: "{{ nextcloud_config_db_root_password }}"
      - key: "MYSQL_PASSWORD"
        value: "{{ nextcloud_config_db_database_password }}"
      - key: "MYSQL_DATABASE"
        value: "{{ nextcloud_config_db_database_name }}"
      - key: "MYSQL_USER"
        value: "{{ nextcloud_config_db_database_user }}"
      - key: "MYSQL_HOST"
        value: "{{ nextcloud_mariadb_container_name }}"

### nextcloud_nginx_container vars

These variables are used to configure the container that runs nginx-proxy. Many of them map directly to the [`docker_container` task](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) used to create the container.

#### `nextcloud_nginx_container_image`

The specific nginx-proxy container image to use.

    nextcloud_nginx_container_image: "jwilder/nginx-proxy:alpine"

#### `nextcloud_nginx_container_name`

The name for the running nginx-proxy container.

    nextcloud_nginx_container_name: "nextcloud-nginx"

#### `nextcloud_nginx_container_ports`

The list of ports for the nginx-proxy container to listen on.

    nextcloud_nginx_container_ports:
      - "80:80"
      - "443:443"

#### `nextcloud_nginx_container_restart`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_nginx_container_restart: true

#### `nextcloud_nginx_container_state`

[`docker_container` module](https://docs.ansible.com/ansible/latest/modules/docker_container_module.html#docker-container-module) `restart` setting for this container.

    nextcloud_nginx_container_state: started

#### `nextcloud_nginx_container_volumes`

Volumes for nginx-proxy container.

    nextcloud_nginx_container_volumes:
      - "./proxy/conf.d:/etc/nginx/conf.d:rw"
      - "./proxy/vhost.d:/etc/nginx/vhost.d:rw"
      - "./proxy/html:/usr/share/nginx/html:rw"
      - "./proxy/certs:/etc/nginx/certs:ro"
      - "/etc/localtime:/etc/localtime:ro"
      - "/var/run/docker.sock:/tmp/docker.sock:ro"

### nextcloud_network vars.

These variables are used to configure the Docker network used in the Nextcloud setup. They are used to configure the [`docker_network` task](https://docs.ansible.com/ansible/latest/modules/docker_network_module.html#docker-network-module) used to create the network.

#### `nextcloud_network_name`

The name for the running Docker network that containers use for communication.

    nextcloud_network_name: "nextcloud_network"

### Nextcloud volume vars.

This variable is used to create the persistent Docker volumes used in the Nextcloud setup. It is passed directly to the [`docker_volume` task](https://docs.ansible.com/ansible/latest/modules/docker_volume_module.html#docker-volume-module) used to create those volumes.

#### `nextcloud_volumes`

The list of nextcloud volumes to create. If created, these are used by the `nextcloud-app` and `nextcloud-mariadb` containers (above). If not created, it's necessary to provide a path in place of the volume name to the `nextcloud_app_container_volumes` or `nextcloud_mariadb_container_volumes` variable(s).

    nextcloud_volumes:
      - "nextcloud"
      - "mariadb"

### Nextcloud cli install vars

These variables are used to configure the command that's used to complete the Nextcloud install on the role's initial run.

#### `nextcloud_occ_prefix`

The prefix used to specify the Docker container to run `occ` commands on, and also the user to run the commands as.

    nextcloud_occ_prefix: "docker exec --user www-data {{ nextcloud_app_container_name }}"

#### `nextcloud_occ_install`

The actual command used to install the Nextcloud instance.

    nextcloud_occ_install: >
      php occ maintenance:install
      --database="{{ nextcloud_config_db_database }}"
      --database-name="{{ nextcloud_config_db_database_name }}"
      --database-user="{{ nextcloud_config_db_database_user }}"
      --database-pass="{{ nextcloud_config_db_database_password }}"
      --database-host="{{ nextcloud_mariadb_container_name }}"
      --admin-user="{{ nextcloud_config_admin_user }}"
      --admin-pass="{{ nextcloud_config_admin_password }}"

### Nextcloud cron vars

These variables are used to configure the cron job(s) configured by the role for the Nextcloud app.

#### `nextcloud_cron_tasks_include`

The include file containing the tasks for configuring cron. Override this path to provide your own cron tasks.

    nextcloud_cron_tasks_include: "nextcloud_cron.yml"

#### `nextcloud_cron_tasks`

A list of the default cron tasks to add to crontab.

    nextcloud_cron_tasks:
      - "php -f /var/www/html/cron.php"

## Example Playbook

Including an example of how to use your role (for instance, with variables
passed in as parameters) is always nice for users too:

    - hosts: servers
      become: true
      vars:
        nextcloud_config_db_root_password: "G7kTJU4kfzDUfxBwbLrnjufL"
        nextcloud_config_db_database_password: "XGwUnenyBMQMNJrkvuEhzXeh"
        nextcloud_config_admin_password: "SpaEUmFmZjsWG6T2deyef76C"
      roles:
         - role: ansible-role-nextcloud-docker

## License

GPLv2
