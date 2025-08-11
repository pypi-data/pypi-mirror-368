# KWS app auth plugin for httpie

## Using command line arguments

```shell
https -A kws -u $appid:$appsecret https://kws.knd.com.cn/api/v4/manufacturers/
```

## Using environment variables

```shell script
export KWS_APP_ID=$appid
export KWS_APP_SECRET=$appsecret

https -A kws https://kws.knd.com.cn/api/v4/manufacturers/
```

## Using configuration file

Download app auth file to `$HOME/.kws-auth`

```shell script
https -A kws https://kws.knd.com.cn/api/v4/manufacturers/
```
