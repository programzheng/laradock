#讀取.env
include .env
export $(shell sed 's/=.*//' ./.env)

#當前年-月-日
date=$(shell date +"%F")
COMPOSE=docker-compose
SERVICES=nginx mysql phpmyadmin redis ngrok mosquitto

.PHONY: up, restart, down, bash, change-php
#預設bash
bash?=bash
bash:
	$(COMPOSE) exec workspace bash -c "$(bash)"
	
#php worker sh
php-worker-sh:
	$(COMPOSE) exec php-worker sh

#php worker reload
php-worker-reload:
	$(COMPOSE) exec php-worker sh -c "supervisorctl reload"

#php worker update
php-worker-update:
	$(COMPOSE) exec php-worker sh -c "supervisorctl update"

#php worker restart
php-worker-restart-%:
	$(COMPOSE) exec php-worker sh -c "supervisorctl restart $*"

#php worker restart
php-worker-stop:
	$(COMPOSE) exec php-worker sh -c "supervisorctl stop all"

#啟動服務
up: 
	$(COMPOSE) up -d $(SERVICES)

#重啟服務
restart:
	$(COMPOSE) restart $(service)

#重新啟動、建立單一服務(重新取得docker-composer.yml設定)
reup:
	$(COMPOSE) up -d --force-recreate --no-deps --build $(service)

#關閉服務
down:
	$(COMPOSE) down

#列出使用中的容器
ps:
	$(COMPOSE) ps

#服務log
#serivce=service name
logs:
	$(COMPOSE) logs $(serivce)

#備份mysql all database
mysql-backup:
	$(MAKE) check-data-directory directory=mysql-backup_$(MYSQL_VERSION)
	cp -R -f $(DATA_PATH_HOST)/mysql_$(MYSQL_VERSION) $(BACKUP_PATH_HOST)/mysql-backup_$(MYSQL_VERSION)/$(date)
	# remove 3 days ago backup directory
	rm -r $(BACKUP_PATH_HOST)/mysql-backup_$(MYSQL_VERSION)/$(shell date --date="3 days ago" +"%F")

#version=php版本號 Ex: 7.0, 7.1
change-php: export PHP_VERSION=$(version)
change-php:
	echo 'changing Php Version to '${PHP_VERSION}
	# change version in env file 
	# sed -i is write file, search char PHP_VERSION=... replace PHP_VERSION=$*
	sed -i "s/PHP_VERSION=.../PHP_VERSION=${PHP_VERSION}/g" '.env'

	# Build fpm and worker for new version
	$(COMPOSE) build php-fpm
	$(COMPOSE) build php-worker
	$(COMPOSE) build workspace

	# Restart Container to use new version of php
	$(MAKE) up

#檢查資料夾並建立
#directory=備份主資料夾位置 Ex: mysql-backup
check-data-directory:
	if test -d $(BACKUP_PATH_HOST)/$(directory); \
	then echo $(directory) is exists; \
	else mkdir $(BACKUP_PATH_HOST)/$(directory); \
	fi
