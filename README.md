# 新年祝福项目API

RESTFul API 的根路径为 `http://greeting.wedfairy.com/api/`

所有 API 都采用 JSON 格式和 HTTP Token Authorization 与服务器进行通信

## 省份列表

获取省份列表和每个省的祝福数量

```
GET http://greeting.wedfairy.com/api/greetings/place/province/
```
```json
HTTP 200 OK
[
  {
    "id": 1,
    "name": "北京",
    "greetings": 6
  },
  {
    "id": 21,
    "name": "天津",
    "greetings": 2
  }
]
```

## 城市列表

获取城市列表和每个城市的祝福数量，**需要在url中带province参数**

```
GET http://greeting.wedfairy.com/api/greetings/place/city/?province=940
```
```json
HTTP 200 OK
[
  {
    "id": 993,
    "name": "绍兴",
    "greetings": 2
  },
  {
    "id": 979,
    "name": "嘉兴",
    "greetings": 0
  }
]
```

## 行政区列表

获取一个城市的行政区列表和每个区的祝福数量，**需要在url中带city参数**

```
GET http://greeting.wedfairy.com/api/greetings/place/district/?city=993
```
```json
HTTP 200 OK
[
  {
    "id": 994,
    "name": "越城区",
    "greetings": 17
  },
  {
    "id": 995,
    "name": "绍兴县",
    "greetings": 3
  },
]
```

## 祝福语音列表

获取祝福语音列表，包括用户的昵称、头像、语音文件地址、创建时间

在 url 中带 place 参数可以按地点进行过滤，place 可以是任意省、市、区的 place id

```
GET http://greeting.wedfairy.com/api/greetings/greeting/?place=993
```
```json
HTTP 200 OK
{
  "count": 10,
  "next": "http://localhost:8001/api/greetings/greeting/?page=2&place=993",
  "previous": null,
  "results": [
    {
      "id": 11,
      "owner_id": 15546,
      "time_created": "2016-01-14T21:25:27",
      "url": "http://mm.8yinhe.cn/wechat/vxaBbzYnUd0P27u_SCzzsRO60uptS2bR4YtVoN5W3Rh6_-P9wz1OjezzpcRI_vPP.mp3",
      "profile": {
        "id": 15504,
        "name": "鬼骨孖",
        "avatar": "http://up.img.8yinhe.cn/wechat/hMloFwqj78k8H1neJvk5nI2WgUPKvHgkdDgbBLZLsUSCDt4xP08x5uG_U6Z7G9GC",
        "data": null
      },
      "places": [
        {
          "id": 940,
          "category": "province",
          "parent": null,
          "name": "浙江"
        },
        {
          "id": 993,
          "category": "city",
          "parent": 940,
          "name": "绍兴"
        }
      ],
      "key": null
    },
    {
      "id": 10,
      "owner_id": 15546,
      "time_created": "2016-01-14T21:22:57",
      "url": "http://mm.8yinhe.cn/wechat/lrsGlwyNW7Xvkn6PaHWt45H0YyfkDqrps5tck6u5lEtcKNnQ9xi2HQ1QP_4-UOnI.mp3",
      "profile": {
        "id": 15504,
        "name": "鬼骨孖",
        "avatar": "http://up.img.8yinhe.cn/wechat/hMloFwqj78k8H1neJvk5nI2WgUPKvHgkdDgbBLZLsUSCDt4xP08x5uG_U6Z7G9GC",
        "data": null
      },
      "places": [
        {
          "id": 940,
          "category": "province",
          "parent": null,
          "name": "浙江"
        },
        {
          "id": 993,
          "category": "city",
          "parent": 940,
          "name": "绍兴"
        },
        {
          "id": 994,
          "category": "district",
          "parent": 993,
          "name": "越城区"
        }
      ],
      "key": null
    }
  ]
}
```

places 参数包含该语音祝福所对应的所有**省/市/区**信息

## 用户语音

获取一个用户的语音，包含语音信息，个人信息，位置信息

```
GET http://greeting.wedfairy.com/api/greetings/usergreeting/15670/
```
```json
HTTP 200 OK
{
  "id": 129,
  "owner_id": 15670,
  "time_created": "2016-01-23T12:59:50",
  "url": "http://mm.8yinhe.cn/wechat/hwKfTVVCqLhRtiTF1cxF1MFbbEAQsC7jOXs8fA_rPvvcOZTATlCakMgBtlZBJk8l.mp3",
  "status": "online",
  "title": null,
  "description": "有爱有俩个都说觉得好多可以。亚太风机就乖好声音说，每次和她做榜样。金茂大厦姥姥过特别多的伤害都是三十多等一等。跳跃太自大干吃不开户时间搞微信搞的这么好。",
  "profile": {
    "id": 15628,
    "name": "今年本命年",
    "avatar": "http://wx.qlogo.cn/mmopen/LB0icf6Q5rSSvy4EIS0jITQJo4tkELg2VCCVWJtBLvtkyqWomia7AgfzyVAyU3CbJFibQkNicDJWm0ibtYbEpGuaNXYib3ypEVS4Sp/0",
    "data": null
  },
  "places": [
    {
      "id": 800,
      "category": "province",
      "parent": null,
      "name": "上海"
    },
    {
      "id": 801,
      "category": "city",
      "parent": 800,
      "name": "上海"
    },
    {
      "id": 814,
      "category": "district",
      "parent": 801,
      "name": "浦东新区"
    }
  ]
}
```
