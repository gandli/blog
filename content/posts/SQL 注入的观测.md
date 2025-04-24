+++
title= "SQL 注入的观测"
date= 2025-04-24
tags= ["post"]
draft= false
+++

# SQL 注入的观测

### 拉取镜像并启动 sqli-lab 容器

首先，通过 Docker 拉取并启动 `sqli-lab` 容器：

```shell
docker run -dt --name sqli-lab -p 80:80 acgpiano/sqli-labs:latest
```

启动完成后，你应该能够访问 `http://localhost`。

### 安装数据库

访问 `http://localhost/sql-connections/setup-db.php` 以安装 SQL 注入实验数据库。

![安装数据库](../assets/image-20250423224246712.png)

### 访问注入实验页面

接着，访问以下 URL 进入 SQL 注入实验页面：

```
http://localhost/Less-1/
```

![访问实验页面](../assets/image-20250423224332261.png)

### 进行 SQL 查询

尝试访问：

```
http://localhost/Less-1/?id=1
```

这时，页面会发起 SQL 查询，展示相应内容：

![SQL 查询页面](../assets/image-20250423224359700.png)

### 进入容器

为了进一步观察日志和数据库查询，进入 `sqli-lab` 容器：

```shell
docker exec -it sqli-lab bash
```

### 查看 Apache 访问日志

在容器内，使用以下命令查看 Apache 的访问日志：

```shell
tail -f /var/log/apache2/access.log
```

### 进入 MySQL 并开启日志功能

接下来，我们将进入 MySQL，开启通用查询日志以观察执行的 SQL 查询。首先进入 MySQL：

```shell
mysql -u root
```

然后执行以下命令开启日志功能：

```mysql
mysql> SET global general_log = 1;
mysql> SET global log_output = 'FILE';
mysql> SET global general_log_file = '/var/lib/mysql/general.log';
mysql> SHOW VARIABLES LIKE 'general_log%';
```

![设置 mysql 日志](../assets/image-20250423232035055.png)

这些命令将开启通用查询日志并将其输出到文件 `/var/lib/mysql/general.log`。

### 查看 MySQL 日志

执行以下命令查看 MySQL 的查询日志：

```shell
tail -f /var/lib/mysql/general.log
```

### 使用 sqlmap 进行 SQL 注入测试

最后，使用 `sqlmap` 工具进行 SQL 注入测试，获取数据库中的数据。执行以下命令：

```shell
sqlmap -u http://localhost/Less-1?id=1 --dump --batch
```

成功执行后，你将看到数据库中被泄露的数据：

![sqlmap 测试结果](../assets/image-20250423231015136.png)

通过 Apache 和 MySQL 日志，你可以清楚地观察到 SQL 注入攻击如何通过 `id` 参数注入并执行 SQL 查询：

![Apache 和 MySQL 日志](../assets/image-20250423230352032.png)
