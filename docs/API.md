# Olib API 接口文档

## 概述

Olib 客户端通过 HTTP 请求与后端服务器通信。所有请求需携带设备 UUID 作为 Header。

## 通用说明

### 请求头

| Header | 说明 |
|--------|------|
| UUID | 设备唯一标识，基于 MAC 地址生成的 UUID5 |

### 服务器地址

根据环境变量 `APP_ENV` 决定：
- 开发: `http://127.0.0.1:8000`
- 测试: `https://测试服务器`
- 生产: `https://生产服务器`

---

## 接口列表

### 1. 搜索书籍

**POST** `/getbooks`

#### 请求体 (JSON)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| bookname | string | 是 | 搜索关键词 |
| page | int/null | 否 | 页码 |
| languages | string/null | 否 | 语言筛选 |
| extensions | string/null | 否 | 格式筛选 (txt/pdf/epub/mobi/azw/azw3) |
| order | string/null | 否 | 排序方式 (popular/bestmatch/title/date/year) |
| limit | string | 否 | 每页数量，默认 "100" |
| e | string/null | 否 | 精准搜索标志 ("1" 为精准) |
| yearFrom | string/null | 否 | 出版年份起始 |
| yearTo | string/null | 否 | 出版年份结束 |

#### 成功响应

```json
{
  "success": 1,
  "books": [
    {
      "id": "书籍ID",
      "hash": "哈希值",
      "title": "书名",
      "year": "出版年份",
      "author": "作者",
      "extension": "文件格式",
      "filesize": "文件大小(字节)",
      "filesizeString": "文件大小(可读)",
      "readOnlineUrl": "在线阅读链接"
    }
  ],
  "pagination": {
    "current": 1,
    "total_pages": 10,
    "next": 2,
    "before": null
  }
}
```

#### 错误响应

- **429**: 速率限制（15次/分钟）
- **其他**: `success` 字段非 1

---

### 2. 获取下载链接

**POST** `/getdownurl`

#### 请求体 (JSON)

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| bookid | string | 是 | 书籍ID |
| hashid | string | 是 | 书籍哈希 |
| source | string | 是 | 固定值 "client" |
| remix_id | string/null | 否 | 认证ID |
| remix_key | string/null | 否 | 认证Key |

#### 成功响应

```json
{
  "durl": "https://下载直链地址"
}
```

#### 错误响应

- **429**: 速率限制（5次/分钟）
- **其他**: 下载失败

---

### 3. 获取服务端配置

**GET** `/OlibServer`

#### 响应

```json
{
  "Versions": [
    {
      "version": "2.0.4",
      "forcedUpdate": false
    }
  ],
  "Notice": {
    "show": true,
    "title": "公告标题",
    "content": "公告内容"
  },
  "UpdateUrl": "https://更新下载地址"
}
```

---

## 错误码说明（客户端内部）

| 错误码 | 说明 |
|--------|------|
| 0 | 搜索成功但结果为空 |
| -1 | 未知异常 |
| -999 | 搜索词违禁 |
| 999 | 服务器速率限制 |
