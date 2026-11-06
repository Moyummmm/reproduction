# Crossref 扩展检索

- 每条检索返回最多 100 条，结果按 Crossref 默认相关性排序，未分页。
- 使用此前 100 条查询及相同的去引号/布尔词转换，以 query.bibliographic 搜索；不等价于 Google Scholar 原表达式。
- 过滤 from-pub-date:2022-01-01；未设结束日期，与此前 Crossref 查询口径一致。
- results.csv 保留各查询全部返回结果，不去重；search_log.csv 记录实际表达式、URL、状态、总数、截断和时间。
- raw/ 是每条成功请求的原始 JSON；数据库变化可能导致与此前前 20 条的排序不一致。
- 结果为未筛选候选，不能作为已纳入论文或完整系统检索。
