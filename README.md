# Fix your weaknesses and nobody can bleed you

<img src="./img/eye_of_sauron.svg" alt="sauron" style="display: block; width:50%; margin-left: auto;margin-right: auto"/>

<i>One ring to rule them all,
<br>One ring to find them,
<br>One ring to bring them all
<br>And in the darkness bind them.</i>
<p>- John R.R. Tolkien "Lord of The Rings"</p>

## Contents
- [Introduction](#introduction)
- [Found vulnerabilities and possible attacks](#found-vulnerabilities-and-possible-attacks)
  - [SQL Injection](#sqli)
  - [HTML Injection](#htmli)
  - [Error Handlers](#error-handlers)
- [Prevention](#prevention)
- [References](#references)

## Introduction
According to OWASP TOP 10 2021, `Injection` And `Security Logging and Monitoring` vulnerabilities are on the 3rd and 9th places correspondingly.<br>

#### A03:2021 - Injection
> An application is vulnerable to attack when: <br>
> User-supplied data is not validated, filtered, or sanitized by the application.<br>
> Dynamic queries or non-parameterized calls without context-aware escaping are used directly in the interpreter.<br>
> Hostile data is used within object-relational mapping (ORM) search parameters to extract additional, sensitive records. <br>
> Hostile data is directly used or concatenated. The SQL or command contains the structure and malicious data in dynamic queries, commands, or stored procedures. <br>

#### A09:2021 – Security Logging and Monitoring Failures
> Returning to the OWASP Top 10 2021, this category is to help detect, escalate, and respond to active breaches. Without logging and monitoring, breaches cannot be detected. Insufficient logging, detection, monitoring, and active response occurs any time:<br>
> Auditable events, such as logins, failed logins, and high-value transactions, are not logged.<br>
> Warnings and errors generate no, inadequate, or unclear log messages.<br>
> Logs of applications and APIs are not monitored for suspicious activity.<br>
> Logs are only stored locally.<br>
> Appropriate alerting thresholds and response escalation processes are not in place or effective.<br>
> Penetration testing and scans by dynamic application security testing (DAST) tools (such as OWASP ZAP) do not trigger alerts.<br>
> The application cannot detect, escalate, or alert for active attacks in real-time or near real-time.<br>

## Found Vulnerabilities and possible attacks

### SQLi
First vulnerability is SQL injection is here [1]:
```python
def add_to_order(
    user_id: int,
    order_id:int,
    item_id: int,
    quantity: int,
    price: int):
    ...
    cursor = db_connection.execute(
            'insert into "Orders" values (%s, %s, %s, %s, %s)',
            (user_id, order_id, item_id, quantity, price)
    )
    ...
```
and here [2]:
```python
def show_order(order_id: int, user_id: int):
    try:
    cursor = db_connection.execute(
        'select from "Orders" where id = {}'.format(order_id)
    )
```

Let's look at example attack on [2]. SQL command isn't parametrized and sanitized carefully.<br>
Thus, command such that could lead to unpredictable results: <br>
```python
order_id = "' OR 1=1 --" # Or order_id = "'1; DROP TABLE Orders"
'select from "Orders" where id = {}'.format(order_id)
``` 

For [2] is a bit tricky, because we didn't handle some arguments and error in that case too. Will be discussed below on Error Handlers part.

Both of these SQL injection's could lead to any results. Most popular one - <b>data could be leaked or service will be shut down.</b><br>

### HTMLi
Another vulnerability is HTML injection [3]:
```python
def show_order(order_id: int, user_id: int):
    ...
    return f'<html><body><p>{order_info}</p></body></html>'
```
Example attack here:
```python
order_info = "<script>vulnerable_payload();</script>"; # we can show it by simple alert(1);
```

This type of vulnerability could lead to execution of arbitrary code, apparently.<br>

### Error Handlers

<img src="./img/input_validation.jpg" alt="sauron" style="display: block; width:40%; margin-left: auto;margin-right: auto"/><br>

It's not a vulnerability, but it's a good practice if errors handled and logged correctly [4]:<br>

```python
def show_order(order_id: int, user_id: int):
    ...
    return (
           f'<html><body><p>Error was happend for {order_id}' # typo: happened, not happend
           '</p></body></html>')
```
Also, [5]:
```python
def add_to_order(
  user_id: int,
  order_id:int,
  item_id: int,
  quantity: int,
  price: int):
    ...
```
Where is the quantity and price handlers? Are we sure that they're positive integers?

Also, [6], how can we be sure that there exists element in `[0]` index?<br>

```python
current_price = cursor.fetchone()[0]
```
Could lead to unexpected quit and error.<br>
## Prevention

For [1] (SQLi), check ranges of quantity and price. Although, we can check for all of the arguments, if there's no such handler at all:<br>
```python
if quantity < 0 or price < 0:
  return "Error: arguments in add_to_order(...) aren't proper.\n"
cursor = db_connection.execute(
            'insert into "Orders" values (%s, %s, %s, %s, %s)',
            (user_id, order_id, item_id, quantity, price)
    )
```

Prevention for [2] (SQLi) is using parametrized query and sanitized arguments:
```python
def show_order(order_id: int, user_id: int):
    try:
    cursor = db_connection.execute(
        'select from "Orders" where id = %s', (order_id,)
    )
```

For [3] (HTMLi) we should remove all JS/HTML tags:<br>
```python
import lxml
from lxml.html.clean import Cleaner

cleaner = Cleaner()
cleaner.javascript = True
cleaner.style = True

parsed_order_id = int(lxml.html.tostring(cleaner.clean_html(lxml.html.parse(order_id))))
```

Correction for [4]:
```python
def show_order(order_id: int, user_id: int):
    ...
    except Exception as e:
        return (
           f'<html><body><p>Error while fecthing {order_id} in show_order()'
           '</p></body></html>')
```

For [5] fix mentioned in [1]

For [6]:
```python
...
current_price = cursor.fetchone()
if current_price:
    current_price = current_price[0]
...
```

## References

1. [OWASP TOP-10](https://owasp.org/www-project-top-ten/)
2. [Injection Attacks Prevention cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)
3. [Secure coding](https://en.wikipedia.org/wiki/Secure_coding)
