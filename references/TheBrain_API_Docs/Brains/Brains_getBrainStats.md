# Gets statistics about the specified brain

**接口路径**: `/brains/{brainId}/statistics`
**方法**: `GET`

## 描述
`internalFilesSize` and `iconsFilesSize` values are in bytes.

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path |  | Yes | string (uuid) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the statistics failed to be generated |
| 401 | If the API Key is missing or invalid |
