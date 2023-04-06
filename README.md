# 数据库大作业

因为 Oracle 安装太麻烦了，于是用了 MySQL

## install

安装 Docker
```shell
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo service docker start
```
启动数据库
```shell
sudo docker compose up -d
```
初始化数据库
```shell
sudo docker exec flask-mysql /bin/sh -c "mysql -uroot -pexample < /db/setup.sql"
```
配置 python 虚拟环境

如果已经安装了 conda ，可以用 conda 配置虚拟环境：
```shell
conda create -y -n db_project python=3.9
conda activate db_project
pip install -r requirements.txt
```
如果没有安装 conda ，也可以通过如下方法配置虚拟环境：
```shell
python -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

## start

```shell
python -m flask run
```
如果刚安装完能成功运行，一段时间后运行不了，请检查一下 docker 和 python venv：
```shell
sudo docker ps -a
which python
```
用 `sudo service docker restart` 可以重启 docker。
