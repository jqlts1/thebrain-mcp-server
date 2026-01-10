# Gets a list of modification logs for the specified brain within a specified date and time range

**接口路径**: `/brains/{brainId}/modifications`
**方法**: `GET`

## 描述
Omit `startTime` and `endTime` values to retrieve **all** modification logs for the specified brain.

Provide `startTime` and `endTime` values to return modification logs only within a specific time range.

<hr />

Parameters `startTime` and `endTime` accept values formatted as either `date` or `date-time` strings, conforming to [RFC 3339, section 5.6](https://tools.ietf.org/html/rfc3339#section-5.6).

**Examples:**
- `2017-07-03` (Date only)
- `2017-07-03T01:42:28Z` (Date and Time in UTC)
            
<hr />
            
`modType` values and their corresponding actions:

- **Generic Actions:**
  - 101: Created
  - 102: Deleted
  - 103: Changed Name
  - 104: Created By Paste
  - 105: Modified By Paste

- **Thoughts and Links:**
  - 201: Changed Color
  - 202: Changed Label
  - 203: Set Type
  - 204: Changed Color2
  - 205: Created Icon
  - 206: Deleted Icon
  - 207: Changed Icon
  - 208: Changed Field Instance
  - 209: Created Field Instance
  - 210: Deleted Field Instance

- **Thought Specific:**
  - 301: Forgot
  - 302: Remembered
  - 303: Changed Thought Access Type
  - 304: Changed Kind

- **Link Specific:**
  - 401: Changed Thickness
  - 402: Moved Link
  - 403: Changed Direction
  - 404: Changed Meaning
  - 405: Changed Relation

- **Attachment Specific:**
  - 501: Changed Content
  - 502: Changed Location
  - 503: Changed Position

- **Brain and Brain Setting Specific:**
  - 601: Changed Setting
  - 602: Reordered Pins

- **Brain Access Specific:**
  - 701: Changed Brain Access Entry

- **Note Specific:**
  - 801: Created Note
  - 802: Deleted Note
  - 803: Changed Note
  - 804: Deleted Note Asset
  - 805: Created Note Asset
  - 806: Changed Note Asset
  - 807: Deleted Markdown Image
  - 808: Created Markdown Image
  - 809: Changed Markdown Image
  - 810: Deleted Dynamic Wallpaper Image
  - 811: Created Dynamic Wallpaper Image
  - 812: Changed Dynamic Wallpaper Image

- **Calendar Event Specific:**
  - 900: Created Calendar Event
  - 901: Modified Calendar Event
  - 902: Deleted Calendar Event
  - 903: Deleted Calendar Event Recurring Instance

- **Field Definition Specific:**
  - 1001: Changed Field Definition
  - 1002: Created Field Definition
  - 1003: Deleted Field Definition
            
<hr />
            
`entityType` values (used by `sourceType`, `extraAType` and `extraBType`)

  - -1: Unknown
  - 1: Brain
  - 2: Thought
  - 3: Link
  - 4: Attachment
  - 5: Brain Setting
  - 6: Brain Access Entry
  - 7: Calendar Event
  - 8: Field Instance
  - 9: Field Definition

## 参数
| 名称 | 位置 | 描述 | 必填 | 类型 |
| --- | --- | --- | --- | --- |
| brainId | path | The ID of the brain | Yes | string (uuid) |
| maxLogs | query | The maximum number of modifications to return in the list, beginning from the `startTime` | Yes | integer (int32) |
| startTime | query | The start of the datetime range, inclusive. Only modification logs that occurred at or after this datetime will be returned. | No | string (date-time) |
| endTime | query | The end of the datetime range, inclusive. Only modification logs that occurred at or before this datetime will be returned. | No | string (date-time) |

## 响应
| 状态码 | 描述 |
| --- | --- |
| 200 | Success |
| 400 | If the modification logs failed to be retrieved |
| 401 | If the API Key is missing or invalid |
