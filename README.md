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
