## Installing the required dependencies

```
$ virtualenv env
$ source ./env/bin/activate
(env) $ pip pip install python-nmap requests
```

## Setting up and installing the script

```
(env) $ git clone https://github.com/soko1/loop-network-scanner && cd loop-network-scanner
(env) $ mv loop-network-scanner.conf.sample loop-network-scanner.conf
(env) $ vim loop-network-scanner.conf
...
(env) $ ./loop-network-scanner.py
```


