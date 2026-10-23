# 内容修订记录 — 2026-10-23（第一阶段归档）

后续已完成全量整改，当前状态以 [全站审核记录](adsense-content-audit-2026-10-23.md) 为准。下文保留第一阶段的工作范围与当时未完成事项。

本轮处理 AdSense 拒审后抽查发现的事实矛盾、证据不足和重复选题。没有将 Google 的笼统拒审提示当作具体页面的判定，也不承诺本轮修改能够获批。

## 已完成

- 重写工具选择和 Claude/ChatGPT 对比文章，统一 Java 工程师的作者背景。移除缺少记录支持的亲测排名、订阅金额、耗时收益和模型能力断言，改为带有明确输入、验收标准和评分表的评估方法。
- 重写 OpenAI 429 排错文章，区分需要账户操作的错误、暂时性压力及未知错误。示例均标注为合成数据，可离线执行。
- 将 `openai-429-fix-variations` 合并到 `chatgpt-api-429-fix`，删除重复文章，并为旧地址的带斜杠和无斜杠形式配置 301。更新后的 sitemap 和 RSS 不再包含旧条目。
- 将 rate limits 文章收窄为容量规划，删除旧的五级额度表和无法核实的账户经验，使用明确标注的假设数值展示计算。
- 将 429001 数字映射限定为腾讯 TokenHub 的已文档化约定，处理字符串和整数两种代码形式，删除“普通 429 就是直连 OpenAI”等错误判断。
- 两篇 CSRF 文章补充作者报告与公开复现材料的区别，列出缺失材料；纠正无状态 Basic 认证必然免于 CSRF 的说法，并撤回缺少过滤器记录支持的 401 解释。
- About 补充证据类型、AI 辅助编辑和更正说明。修正四篇文章中因目标内容重写而失准的内部链接描述。
- 原有三篇已修改文章和新增 AFTER_COMMIT 文章及图片、脚本未由本轮编辑。

## 参考来源

- [OpenAI 错误码](https://developers.openai.com/api/docs/guides/error-codes)
- [OpenAI 速率限制](https://developers.openai.com/api/docs/guides/rate-limits)
- [OpenAI Python SDK 重试](https://developers.openai.com/api/reference/python#retries)
- [腾讯 TokenHub 错误码](https://www.tencentcloud.com/document/product/1300/82348)
- [Claude 网页搜索](https://support.claude.com/en/articles/10684626-enable-and-use-web-search)
- [Spring 无状态浏览器的 CSRF 风险](https://docs.spring.io/spring-security/reference/7.0/features/exploits/csrf.html#csrf-and-stateless-browser-applications)
- [Spring CsrfFilter 的错误处理](https://docs.spring.io/spring-security/site/docs/current/api/org/springframework/security/web/csrf/CsrfFilter.html)

## 验证及边界

使用本机 Node 22.23.2 构建；默认 Node 20.20.2 低于 Astro 要求。构建及本轮 Python 示例的离线断言已通过。没有调用付费模型 API，也没有重新执行历史 Java 实验。

本轮没有发布网站、提交代码或重新申请 AdSense。Cloudflare 的 301 已写入构建产物；线上生效仍需部署后确认。

## 仍需真实材料的部分

历史 CSRF 实验需要原始项目、起始 commit、完整指令文件、工具版本和原始运行记录。新建示例不能替代历史数据的证据。本轮已明确这些限制，尚未补齐原始材料。

其余文章仍需要逐篇核对版本、产品功能、个人经历和复现依据。本轮是重点修订，不能视为全站审核完成。重新申请应在确认线上内容更新、重定向正常及其余关键内容复核之后进行。
