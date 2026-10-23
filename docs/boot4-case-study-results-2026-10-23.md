# 完整案例与入口补强 — 2026-10-23

用户确认继续补强独特价值、相似文章分工与首页入口。本轮在原有 50 篇文章基础上增加完整可执行材料，没有增加凑数量的文章。设计取舍见 [实施说明](boot4-case-study-design-2026-10-23.md)。

## 新增材料

- [完整 Java 项目](../examples/boot4-verification-lab/README.md)：Java 17、Maven、Boot 3.5.7 / 4.0.0 两个 profile；内存 H2，无需 Docker。
- [GitHub 源码与脱敏证据](https://github.com/zhoupeng20188/ai-kit-guides-verification-labs/tree/main/boot4-verification-lab)。
- [源码与证据 ZIP](../public/examples/boot4-verification-lab.zip)，包含 30 个文件。
- [结果清单](../examples/boot4-verification-lab/evidence/results.json)：实际依赖版本、命令、退出码、执行数量和 POM / 应用及测试源码摘要。
- [在线材料页源码](../src/pages/examples/boot4-verification-lab.astro)：下载、运行步骤、版本表、日志、源码地图与验证边界；站点路径 `/examples/boot4-verification-lab/`。
- [打包脚本](../scripts/package_boot4_lab.py)：先核对已执行源码的摘要及报告，再生成站点材料。不会打包 Maven target 或本机原始输出目录。

该项目是本次用 AI 协助新建并执行的教学案例，不是历史实验的恢复材料，也不代表作者在生产环境经历过相同事故。

## 实际执行结果

环境：macOS arm64、Amazon Corretto Java 17.0.19、Maven 3.9.11。执行时间保存在结果清单中。本地设置显式选择了 JDK 17，默认系统 Java 8 不适合运行本例。

| 执行 | tests | failures | errors | skipped | 退出 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Boot 3.5.7 常规套件 | 11 | 0 | 0 | 0 | 0 |
| Boot 4.0.0 常规套件 | 11 | 0 | 0 | 0 | 0 |
| 显式选择未发现的 sentinel | 1 | 1，预期 | 0 | 0 | 1 |
| 关闭 ERROR 分派许可的故障用例 | 1 | 1，预期 | 0 | 0 | 1 |

两个正常套件执行的是相同的 11 项检查，共 22 次通过；不是 22 种独立需求。验证器核对用例身份及具体失败，依赖下载失败或编译失败不会被当作成功复现。

实际解析的版本：

| 组件 | boot3 | boot4 |
| --- | --- | --- |
| Spring Security | 6.5.6 | 7.0.0 |
| Flyway | 11.7.2 | 11.14.1 |
| H2 | 2.3.232 | 2.4.240 |
| JUnit Jupiter API | 5.12.2 | 6.0.1 |

## 本例提供的独立观察

1. **HTTP 状态需要追踪完整分派。** 最初 catch-all authenticated 配置下，真实 HTTP 请求显示 401。日志确认 CSRF 先拒绝为 403，随后 `/error` 的 ERROR 分派触发认证入口。正常配置仅允许 servlet ERROR 分派，保留 CSRF、普通请求认证及直接 `/error` 请求的保护。故障开关可重现该差异。
2. **200 需要说明测试链。** 配置安全过滤器的 MockMvc 拒绝缺 token 的 POST；刻意不加过滤器的 standalone harness 返回 200。两者提供不同证据。
3. **repair 后 validate 成功不证明 schema 一致。** 旧库的 tag 仍可为空，按修改后 V2 安装的新库不可为空；旧行与新行的 tag 值也不同。恢复旧 V2 后用 V3 回填并约束，两个路径的受检字段与行值才一致。
4. **pending 与 checksum 不同。** 新建但未执行的 V3 可能让独立 validate 报告 pending；本例在写 V3 前验证恢复后的历史，再迁移并验证最终状态。
5. **正常 suite 不证明所有源文件被发现。** 故意失败的 `UndiscoveredShould` 默认未选中；显式选择后按具体断言失败。

日志中的 `OBSERVATION` 行记录实际响应状态及查询值。公开日志去除了项目 / home 路径和本机账户名，XML 移除了系统属性；未删除用例身份、结果、故障或关键过滤器记录。本机原始输出保留在被忽略的 `verification-output/` 和审核缓存中。

## 文章与入口

- 迁移总览用于选择应用契约和检查范围；walkthrough 改为围绕完整项目的运行与解释，保留 URL 和发布日期。
- CSRF、JUnit 发现、Flyway 文章加入对应源码案例与真实记录；Java 聚合页增加完整案例入口。
- 首页明确 Java 开发者定位，提供案例与源码入口和三步学习路径。移除空广告区块，减少重复精选展示。
- About、默认站点描述、页脚同步定位和证据说明。

## 页面验证及额外修复

- Node 22.23.2 / Astro 7 构建通过，64 个内容页面，RSS 保持 50 篇文章。
- 359 个不同内部链接 / 锚点 / 资源目标检查通过，无缺失；65 个主要本地页面与资源请求通过。新增 ZIP、结果 JSON 和四类日志另行确认 200。
- ZIP 校验通过；包内受检源码摘要与实际执行清单一致，JUnit XML 可解析。
- 已检查手机宽度首页与案例页、桌面首页；手机页面没有横向页面溢出，表格在容器内滚动。
- 浏览器发现 Cookie 提示框点击拒绝会报 `gtag is not defined`。原因是带 `define:vars` 的脚本作用域内声明了局部函数，其他组件无法访问。改为明确设置及调用 `window.gtag`。生产构建在独立本地 origin 中测试，拒绝按钮正常关闭提示框，未产生该脚本错误。

该 Cookie 修复只处理正常浏览行为，不将自定义 banner 认定为 Google 认证 CMP。

## 适用边界

H2 不能证明 PostgreSQL/MySQL 的锁、SQL 方言或生产升级安全；两个 profile 在独立 JVM 中使用一次性数据库，不是将同一个持久数据库跨引擎版本升级。真实 HTTP 限于 loopback 测试，示例不是完整业务产品。固定历史版本用于比较，不表示推荐部署旧补丁。

本轮旨在增加可验证的实质内容与清晰入口；没有流量门槛、字数门槛或通过率承诺。AdSense 申请审核仍需在账户界面执行。
