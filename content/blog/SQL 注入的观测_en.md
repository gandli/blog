+++
title= "Observation of SQL Injection"
date= 2025-04-24
tags= ["post"]
draft= false
+++

# Setting Up the Testing Environment

## Pulling the Image and Starting the sqli-lab Container

First, pull and start the `sqli-lab` container using Docker:

```shell
docker run -dt --name sqli-lab -p 80:80 acgpiano/sqli-labs:latest
```

Once started, you should be able to access `http://localhost`.

## Installing the Database

Visit `http://localhost/sql-connections/setup-db.php` to install the SQL injection lab database.

![Installing Database](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/3be35d91bc7a4cee87b16c34df4f9bcc~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=PyK4ULgVT2PnLT%2FaxfTE7Ph09BA%3D)

## Accessing the SQL Injection Lab Page

Next, visit the following URL to access the SQL injection lab page:

    http://localhost/Less-1/

![Accessing Lab Page](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/2e7b9dc27ce343fc8a5c31d36823ba7a~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=5e%2BZJ2%2FEdCXmY7RkskrnDJCtsDc%3D)

## Performing SQL Queries

Try accessing:

    http://localhost/Less-1/?id=1

At this point, the page will execute an SQL query and display the corresponding content:

![SQL Query Page](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/958370066d8845839e12bcc6b8b9fe10~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=E7hmBXSEv9sD%2BZbZAxN5IC%2B4jhI%3D)

# Configuring Server and Database Logs

## Entering the Container

To further observe logs and database queries, enter the `sqli-lab` container:

```shell
docker exec -it sqli-lab bash
```

## Viewing Apache Access Logs

Inside the container, use the following command to view Apache's access logs:

```shell
tail -f /var/log/apache2/access.log
```

## Entering MySQL and Enabling Logging

Next, we will enter MySQL and enable the general query log to observe executed SQL queries. First, access MySQL:

```shell
mysql -u root
```

Then, execute the following commands to enable logging:

```mysql
mysql> SET global general_log = 1;
mysql> SET global log_output = 'FILE';
mysql> SET global general_log_file = '/var/lib/mysql/general.log';
mysql> SHOW VARIABLES LIKE 'general_log%';
```

![Enabling Logging](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/ae6543012fb7458e8d61c147a9b80d8d~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=Iz2guAeuwz6%2BVT3xgPM5WuwAKfc%3D)

These commands will enable the general query log and output it to the file `/var/lib/mysql/general.log`.

## Viewing MySQL Logs

Execute the following command to view MySQL's query logs:

```shell
tail -f /var/lib/mysql/general.log
```

# Observing SQL Injection Experiments

## Using sqlmap for SQL Injection Testing

Finally, use the `sqlmap` tool to perform SQL injection testing and retrieve data from the database. Execute the following command:

```shell
sqlmap -u http://localhost/Less-1?id=1 --dump --batch
```

Upon successful execution, you will see the leaked data from the database:

![sqlmap Injection](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/8b0d77eabeae4ba8be0a798f7cc11524~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=RqpjVEYtDSNbgTlMqxCJ5PFJIpA%3D)

Through Apache and MySQL logs, you can clearly observe how SQL injection attacks are carried out by injecting and executing SQL queries via the `id` parameter:

```shell
tail -f /var/log/apache2/access.log
tail -f /var/lib/mysql/general.log
```

![sqlmap Test Results](https://p0-xtjj-private.juejin.cn/tos-cn-i-73owjymdk6/4890304691b74a77b56449e27367aaeb~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAgRnJlZUN1bHR1cmVCb3k=:q75.awebp?policy=eyJ2bSI6MywidWlkIjoiMjY2NDg3MTkxMzM1NTQ2MyJ9&rk3s=f64ab15b&x-orig-authkey=f32326d3454f2ac7e96d3d06cdbb035152127018&x-orig-expires=1746068975&x-orig-sign=Y0Y9zCg24axJGTGmMYeySZtks5E%3D)