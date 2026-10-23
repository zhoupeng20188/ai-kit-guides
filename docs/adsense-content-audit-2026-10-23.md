# AdSense 内容整改与 GSC 复核 — 2026-10-23

后续已补充完整 Boot 案例、真实 HTTP 检查和运行证据，详见 [案例补强记录](boot4-case-study-results-2026-10-23.md)。下文的执行范围和测试数字保留初次全量整改时的口径。

## 完成范围

逐篇核查 52 个原始条目（51 个原有 Git 跟踪文件，加上工作区新增的 AFTER_COMMIT 文章）。两组重复选题各合并一篇，当前保留 50 篇可访问文章。所有当前文章均已实质修订，标题、摘要、正文、更新时间及 FAQ 一并检查。本地预览：http://127.0.0.1:4321/ 。本报告初稿记录的是本地整改完成时的状态；后续提交、推送及自动部署以 Git 历史和线上检查为准。AdSense 复审需在账户中另行提交。

整改目标是提高内容准确性、独创分析和读者可验证性。AdSense 的“低价值内容”提示不提供具体文章归因；本报告记录自行审查的问题，不能声称 Google 已确认这些就是拒审原因，也不能保证修改后获批。

## GSC 数据来源与边界

来源：[用户提供的原始 XLSX](/Users/forever/Downloads/https___aikitguides.com_-Performance-on-Search-2026-10-21.xlsx)，只读分析，未修改原文件。日期按“图表”工作表，而非导出文件名计算。

- 实际区间：2026-07-19 至 2026-10-18；92 天。图表 A2:C93：94 次点击、10,277 次展示；总 CTR = 点击合计 / 展示合计 = 0.91%，不平均每日 CTR。
- 最近 28 天：30 次点击、3,283 次展示。
- “网页”表有 75 个数据行，合计 95 次点击、10,427 次展示。它与日期表是不同聚合口径，不能混用为同一个站点总数。
- “查询数”表有 470 个数据行，列出的点击仅 1 次。不能把可见查询当作完整点击来源；本导出也没有查询与网页的配对明细，不做查询到文章的推断匹配。
- 设备表：桌面 79 次点击，移动设备 15 次点击。文章以代码、命令和诊断为核心，仍需保持移动端可读。
- 搜索表现用于整改排序和保护已有入口，不等于 AdSense 审核结果；零点击不构成删除文章的充分理由。

### 保留并重点整改的搜索入口

下表来自“网页”工作表，展示的是页面维度原始口径。所有这些 URL 保持不变。

| 页面 | 点击 | 展示 | CTR | 平均排名 | 本次处理重点 |
| --- | ---: | ---: | ---: | ---: | --- |
| [codex-spring-boot](../src/content/blog/codex-spring-boot.md) | 19 | 276 | 6.88% | 6.80 | 保留安装/仓库工作流，移除无依据亲历与过时模式 |
| [claude-code-spring-boot](../src/content/blog/claude-code-spring-boot.md) | 11 | 407 | 2.70% | 13.06 | 重写任务边界、测试和权限说明 |
| [cursor-spring-boot](../src/content/blog/cursor-spring-boot.md) | 11 | 282 | 3.90% | 13.89 | 保留 IDE 使用意图，给出明确验收路径 |
| [spring-boot-4-migration-ai-agents](../src/content/blog/spring-boot-4-migration-ai-agents.md) | 9 | 278 | 3.24% | 6.21 | 核对迁移与支持周期，删除无记录排名 |
| [chatgpt-api-429-fix](../src/content/blog/chatgpt-api-429-fix.md) | 5 | 1,426 | 0.35% | 26.83 | 收拢重复选题，纠正额度与重试分类 |
| [codex-spring-boot-4-dependencies-silent-failures](../src/content/blog/codex-spring-boot-4-dependencies-silent-failures.md) | 3 | 869 | 0.35% | 7.41 | 区分依赖解析、自动配置和实际行为 |
| [cursor-ai-editor-tutorial](../src/content/blog/cursor-ai-editor-tutorial.md) | 0 | 1 | 0.00% | 11.00 | 高曝光低点击，标题与正文聚焦具体工作流 |
| [openclaw-vs-hermes-agent](../src/content/blog/openclaw-vs-hermes-agent.md) | 1 | 712 | 0.14% | 52.04 | 保留比较意图，撤除虚构体验及错误依赖/隐私说法 |
| [flyway-checksum-mismatch-ai-agent](../src/content/blog/flyway-checksum-mismatch-ai-agent.md) | 0 | 299 | 0.00% | 7.74 | 纠正 repair 与真实 schema 修复的关系 |

前三个入口均为 AI 编程工具与 Spring Boot，合计 41 次页面点击，说明这一方向已有搜索需求。保留 Java 开发者定位比继续扩充无证据工具榜单更有依据。低 CTR 同时受排名、查询组合和摘要影响，不能仅凭本表归因于标题，也不预测整改后的排名或点击增幅。

## 整改原则与实质变化

- 用户确认实验通常由 AI 搭建，未保留原始项目、运行日志或对话。删除把这些实验包装为作者生产经历的叙述，以及缺少依据的成功率、耗时、花费、样本数和模型排名。
- 把有价值的机制改写成标明假设的技术说明：输入、观察、诊断、修复、验证及适用边界。保留有用的代码与检查路径，不能仅加免责声明后保留错误结论。
- 核对官方产品/框架文档。纠正 CSRF、配置绑定、JUnit 发现、Gradle 缓存、ArchUnit 空选择、MCP 文件系统权限、事务邮件可靠性、Flyway repair 等实质问题。
- 避免把提示文件说成安全边界，或把进程退出成功等同于业务正确。区分已运行、未运行、环境阻塞与文档说明。
- 统一首图为不包含旧“亲测”成绩的通用图；PDF 工具保留实际项目截图，并明确截图不等于本轮复测。去掉与新正文不一致的旧 FAQ。
- 保持原始发布日期，实质修订日期为 2026-10-23。文长由问题所需内容决定，不把固定词数视为 Google 审批门槛。

## 逐篇清单（52 / 52）

GSC 列为“网页”维度的点击 / 展示。横线表示导出没有该精确 URL 的记录，并非判断为没有流量。来源是主要核查入口；正文在具体论断附近保留了更多引用。

| 文章 / 去向 | GSC 点击 / 展示 | 发现与整改 | 核查来源 |
| --- | ---: | --- | --- |
| [Java CI Gates: Prove ArchUnit Rules Fail on Violations](../src/content/blog/ai-code-ci-gates-archunit-spotless.md) | 4 / 25 | 原始agent成绩无记录、ArchUnit空选择过度概括、固定formatter失败版本泛化。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://www.archunit.org/userguide/html/000_Index.html) |
| [AI Code Review for Java: Check Behavior Beyond the Diff](../src/content/blog/ai-code-review-java.md) | 0 / 9 | 虚构生产事故、自动review默认开启、records版本、switch编译语义、JDK24pinning差异。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)、[来源 2](https://docs.oracle.com/en/java/javase/24/language/pattern-matching-switch.html) |
| [AI for Java Developers: A Guide to Setup and Verification](../src/content/blog/ai-for-java-developers.md) | 1 / 375 | 聚合页混入无证据比例和亲历；改为按读者问题组织的导航与证据说明。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/agent-approvals-security)、[来源 2](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) |
| [AI Hallucinations in Code: Check APIs, Versions, and Evidence](../src/content/blog/ai-hallucination-tips.md) | 0 / 40 | Java11 Files.readString版本错误、假生产事故、编译与运行错误混淆、第二模型一致性当证明。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/nio/file/Files.html) |
| [AI-Generated JUnit Tests: Assertions That Can Detect a Regression](../src/content/blog/ai-junit-tests.md) | 1 / 38 | 无证据覆盖率和经历、把所有mock测试当无效、AI不能写集成测试的绝对断言。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.junit.org/6.1.3/overview.html) |
| [Spring Boot 4 Tests Not Running: Audit Surefire Discovery](../src/content/blog/ai-junit-tests-not-running-spring-boot-4.md) | 2 / 178 | 文件数等于测试数错误、pipe掩盖退出码、failIfNoSpecifiedTests误用、JUnit4类路径泛化。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://maven.apache.org/surefire/maven-surefire-plugin/examples/inclusion-exclusion.html)、[来源 2](https://maven.apache.org/surefire/maven-failsafe-plugin/usage.html) |
| [Choosing AI Tools for a Java Development Workflow](../src/content/blog/best-ai-tools-2026.md) | 0 / 42 | 保留首轮整改：去掉虚构基准与固定模型价格，按任务决策并说明证据边界。复核首轮实质整改并纳入全量清单。 | [来源 1](https://learn.chatgpt.com/docs/pricing)、[来源 2](https://claude.com/pricing) |
| [OpenAI API 429: Diagnose Before You Retry](../src/content/blog/chatgpt-api-429-fix.md) | 5 / 1426 | 保留首轮整改：区分限流、余额和中间网关，加入可运行分类与重试边界。复核首轮实质整改并纳入全量清单。 | [来源 1](https://developers.openai.com/api/docs/guides/error-codes) |
| [ChatGPT for Beginners: Ask, Check, and Refine Your First Task](../src/content/blog/chatgpt-beginners-guide-2026.md) | 0 / 3 | 旧免费模型和价格、无跨聊记忆错误、图片仅付费、个人经历无记录、隐私开关混同。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/use-chatgpt)、[来源 2](https://learn.chatgpt.com/docs/web-search)、[来源 3](https://learn.chatgpt.com/docs/personalize) |
| [AFTER_COMMIT Is Not Durable Delivery: A Spring Outbox Checklist](../src/content/blog/claude-code-after-commit-email-loss.md) | — | AI实验被写成客户事故、18ms等数字无原件、fallbackExecution误解、outbox当exactlyonce。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-framework/reference/data-access/transaction/event.html) |
| [Claude Code in GitHub Actions: Review Trusted Java Changes](../src/content/blog/claude-code-github-actions-spring-boot.md) | 0 / 94 | 旧action字段、未审查workflow_run权限升级、虚构价格和每PR成本、无依据个人故事。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://code.claude.com/docs/en/github-actions)、[来源 2](https://github.com/anthropics/claude-code-action)、[来源 3](https://docs.github.com/en/actions/reference/security/secure-use) |
| [Spring Boot IDOR: Enforce Ownership on Every Order Query](../src/content/blog/claude-code-insecure-api-spring-boot.md) | — | 虚构生产/亲测成绩、未引来源统计、原修复遗漏search仍跨用户泄漏。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html) |
| [Claude Code Memory for Spring Boot: Instructions and Verification](../src/content/blog/claude-code-remember-spring-boot.md) | 4 / 72 | 未验证长期经历、记忆当作强制配置、旧事实重复传播。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://code.claude.com/docs/en/memory)、[来源 2](https://code.claude.com/docs/en/settings) |
| [Claude Code with Spring Boot: A Verifiable Repository Workflow](../src/content/blog/claude-code-spring-boot.md) | 11 / 407 | 无依据个人生产经历、固定模型推荐、验证边界不充分。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://code.claude.com/docs/en/overview)、[来源 2](https://code.claude.com/docs/en/memory)、[来源 3](https://code.claude.com/docs/en/permissions) |
| [Spring Boot 4 403: Diagnose CSRF and Verify the Security Chain](../src/content/blog/claude-code-spring-boot-4-403.md) | 0 / 21 | 撤回401误记和无状态安全断言；两篇同实验近重复合并；无原件数字移除。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-security/reference/7.0/servlet/exploits/csrf.html)、[来源 2](https://docs.spring.io/spring-security/reference/7.0/features/exploits/csrf.html) |
| [Spring Boot 4 Upgrade Walkthrough: A Verification Sequence](../src/content/blog/claude-code-spring-boot-4-migration-walkthrough.md) | 0 / 8 | 未发布完整lab却声称完全可复现、AI实验冒充个人迁移、数据比率不可复核、actuator唯一真相断言。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) |
| [Spring Boot Method Security: Verify @PreAuthorize Is Active](../src/content/blog/claude-code-spring-boot-4-preauthorize.md) | 0 / 17 | 无原始agent失败归因、缺少方法拦截验证、把源码注解当安全生效。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html) |
| [Claude Code Subagents and Hooks: Scope Java Review Tasks](../src/content/blog/claude-code-subagents-hooks-spring-boot.md) | 2 / 27 | zero-token/硬护栏误导、hooks字段和事件行为无依据、个人长期经历。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://code.claude.com/docs/en/sub-agents)、[来源 2](https://code.claude.com/docs/en/hooks) |
| [Claude Projects Tutorial: Organize Sources and Instructions](../src/content/blog/claude-projects-tutorial.md) | 0 / 150 | 50+聊天和生产经历无依据、诱导虚构数字的写作模板、Projects与Code执行混同。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://support.claude.com/en/articles/9517075-what-are-projects) |
| [Claude vs ChatGPT: A Reproducible Evaluation Worksheet](../src/content/blog/claude-vs-chatgpt-2026.md) | 0 / 92 | 保留首轮整改：去掉无来源评分，改为官方能力核查和可复用比较步骤。复核首轮实质整改并纳入全量清单。 | [来源 1](https://learn.chatgpt.com/docs/use-chatgpt)、[来源 2](https://support.claude.com/en/articles/10684626-enable-and-use-web-search) |
| [AGENTS.md for Spring Boot: Discovery, Scope, and Local Overrides](../src/content/blog/codex-agents-md-spring-boot.md) | 0 / 12 | AGENTS.override 被误称自动本地私有、旧权限档位、工具读取语义混同和无依据效果数字。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[来源 2](https://code.claude.com/docs/en/memory) |
| [Codex in CI: Verify the Build and Preserve the Business Rule](../src/content/blog/codex-ci-spring-boot-green-build.md) | 0 / 57 | codex永远exit0绝对断言、7次成绩无日志、只看未提交diff、grep吞退出码。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/agent-approvals-security) |
| [Codex Cannot Run Maven: Diagnose JDK, Cache, and Network Access](../src/content/blog/codex-sandbox-maven-spring-boot.md) | 4 / 141 | 旧approval模式、fullauto行为固定化、DNS单因诊断、嵌套沙箱必失败结论。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/agent-approvals-security) |
| [OpenAI Codex with Spring Boot: Setup, Tasks, and Verification](../src/content/blog/codex-spring-boot.md) | 19 / 276 | 过时权限档位、旧 Boot 模板、模型排名和个人生产经历无依据。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/codex/cli)、[来源 2](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[来源 3](https://learn.chatgpt.com/docs/agent-approvals-security) |
| `codex-spring-boot-4-403-fix` → [claude-code-spring-boot-4-403](../src/content/blog/claude-code-spring-boot-4-403.md) | 0 / 92 | 与Claude CSRF文章内容高度重复；无历史原件；401解释被后续记录推翻。合并到 claude-code-spring-boot-4-403；两种旧URL均301。 | 正文及示例核对 |
| [Spring Boot 4 Dependencies: Resolved Does Not Mean Configured](../src/content/blog/codex-spring-boot-4-dependencies-silent-failures.md) | 3 / 869 | 1/12和5/5成绩无记录、Boot3正确坐标表误导、library/starter绝对化。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://spring.io/blog/2025/10/28/modularizing-spring-boot/)、[来源 2](https://docs.spring.io/spring-boot/reference/using/auto-configuration.html) |
| [Spring Boot 4 YAML: Verify Sources, Binding, and Behavior](../src/content/blog/codex-spring-boot-4-yml-properties.md) | 0 / 111 | metadata当绑定、configprops唯一真相、未复核legacy属性和60%数字。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-boot/reference/features/external-config.html)、[来源 2](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html) |
| [Codex and Testcontainers: Diagnose Docker Socket Access](../src/content/blog/codex-testcontainers-docker-socket-spring-boot.md) | 2 / 155 | socket权限等于低风险错误、profile拼写跨版本保证、grep漏未发现测试、无日志成绩。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://java.testcontainers.org/supported_docker_environment/)、[来源 2](https://java.testcontainers.org/test_framework_integration/junit_5/) |
| [Reviewing Copilot Spring Boot 4 PRs: Evidence and Gaps](../src/content/blog/copilot-spring-boot-4-pr-teardown.md) | 0 / 29 | 原文把 PR 自报状态与未经保留的个人实验混作证据，混淆文件计数、注解和测试发现规则。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)、[来源 2](https://github.com/camunda/camunda/pull/42114)、[来源 3](https://github.com/Azure/azure-sdk-for-java/pull/47195) |
| [Cursor Tutorial: Set Up a Project and Verify Your First Change](../src/content/blog/cursor-ai-editor-tutorial.md) | 0 / 1 | 无依据迁移编辑器经历、过期模型价格表、重复FAQ。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://cursor.com/docs)、[来源 2](https://cursor.com/docs/rules)、[来源 3](https://cursor.com/docs/reference/ignore-file) |
| [Cursor Cloud Agents for Spring Boot: Environment and Acceptance](../src/content/blog/cursor-background-agents-spring-boot.md) | 0 / 43 | 远端携带内容和Dockerfile自动发现假设、无依据生产事故与收益。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://cursor.com/docs/cloud-agent) |
| [Cursor Codebase Context for Spring Boot: Verify Retrieved Files](../src/content/blog/cursor-codebase-spring-boot.md) | 3 / 151 | 索引规模与耗时无记录、@codebase强制全量保证、ignore等同安全边界。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://cursor.com/docs/reference/ignore-file)、[来源 2](https://cursor.com/docs) |
| [Cursor Rules Tutorial: Scope Instructions and Check Activation](../src/content/blog/cursor-rules-tutorial.md) | 0 / 290 | 旧.cursorrules被忽略绝对化、无依据习惯/提升数字、无可验证mdc例子。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://cursor.com/docs/rules) |
| [Cursor with Spring Boot: Rules, Context, and Verification](../src/content/blog/cursor-spring-boot.md) | 11 / 282 | 个人经历/耗时无依据、旧版本模板、DTO-only 验证和索引安全误解。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://cursor.com/docs)、[来源 2](https://cursor.com/docs/rules)、[来源 3](https://cursor.com/docs/reference/ignore-file) |
| [Flyway Checksum Mismatch: Restore History Before Repair](../src/content/blog/flyway-checksum-mismatch-ai-agent.md) | 0 / 299 | repair 被错误推荐为首选；新增版本但不还原旧文件仍会失败；缺失实验原始记录。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://documentation.red-gate.com/fd/validate-277578898.html)、[来源 2](https://documentation.red-gate.com/flyway/reference/commands/repair)、[来源 3](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) |
| [GitHub Copilot with Spring Boot: Evaluate Edits and Reviews](../src/content/blog/github-copilot-spring-boot.md) | 3 / 166 | 长期付费/生产经历无依据、机械70%收益数字、产品比较不受证据支持。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.github.com/en/copilot/get-started/about-github-copilot)、[来源 2](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-code-review) |
| [Gradle Tests Not Rerun: UP-TO-DATE, Cache, and Missing Inputs](../src/content/blog/gradle-build-successful-zero-tests-spring-boot-4.md) | 3 / 98 | 把合法缓存当bug、quiet默认推断、毫秒数字及5/5成绩无证据、Maven显式选择语义错误。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.gradle.org/current/userguide/java_testing.html)、[来源 2](https://docs.gradle.org/current/userguide/incremental_build.html) |
| [Harness Engineering: Make Agent Work Verifiable](../src/content/blog/harness-engineering.md) | 0 / 17 | 术语被当作统一行业标准；个人效果无证据；提示规则与权限和硬门禁混淆。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://learn.chatgpt.com/docs/agent-approvals-security) |
| [LangChain Tool Calling: A Bounded Agent with a Local Fixture](../src/content/blog/langchain-1x-tool-calling-agents.md) | 0 / 260 | 未定义price/变量、无限while、tool.invoke参数错误绝对化、未验证供应商模型。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.langchain.com/oss/python/langchain/agents)、[来源 2](https://docs.langchain.com/oss/python/langchain/tools) |
| [Agent Loop Engineering: Stop, Verify, and Recover](../src/content/blog/loop-engineering.md) | 0 / 54 | 原文无可执行机制且存在无记录的个人案例；补充有限循环、重复检测、独立验证与恢复边界。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.langchain.com/oss/python/langchain/agents) |
| [Filesystem MCP with Claude Code: Scope Paths and Verify Access](../src/content/blog/mcp-filesystem-claude-code-java.md) | 0 / 37 | 不存在/未核实read-only参数、把文件路径当目录、allow列表当硬拒绝、绕过内置工具的边界遗漏。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/filesystem/README.md) |
| [MCP Tutorial: Connect One Tool and Verify Its Boundaries](../src/content/blog/mcp-model-context-protocol-tutorial.md) | 0 / 12 | 无依据个人经历/安全统计、过期git/github配置和协议版本混用。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://modelcontextprotocol.io/docs/learn/architecture) |
| `openai-429-fix-variations` → [chatgpt-api-429-fix](../src/content/blog/chatgpt-api-429-fix.md) | 0 / 484 | 与主 429 排错指南搜索意图重叠，原内容有无依据亲历和数值。首轮合并至 chatgpt-api-429-fix；带斜杠/不带斜杠均 301；内链、RSS、sitemap 更新。 | [来源 1](https://developers.openai.com/api/docs/guides/error-codes) |
| [429001 Errors: Identify the Gateway Before Retrying](../src/content/blog/openai-429001-error-code-fix.md) | 1 / 103 | 保留首轮整改：429001 不冒充 OpenAI 官方码，按实际响应分类。复核首轮实质整改并纳入全量清单。 | [来源 1](https://developers.openai.com/api/docs/guides/error-codes) |
| [OpenAI Rate Limits: Plan Request and Token Capacity](../src/content/blog/openai-rate-limits-guide.md) | 1 / 459 | 保留首轮整改：不把固定层级额度当通用事实，按项目模型实际限制诊断。复核首轮实质整改并纳入全量清单。 | [来源 1](https://developers.openai.com/api/docs/guides/rate-limits) |
| [OpenClaw vs Hermes Agent: What to Compare Before Setup](../src/content/blog/openclaw-vs-hermes-agent.md) | 1 / 712 | 虚构周末体验、Neo4j/Qdrant 强制依赖和全部数据留本地说法；改为源码文档比较和可执行评估方法。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/openclaw/openclaw)、[来源 2](https://github.com/NousResearch/hermes-agent) |
| [Prompt Engineering: Define Inputs, Constraints, and Checks](../src/content/blog/prompt-engineering-techniques.md) | 0 / 14 | 数学例子错误、提示词等于temperature、CoT当内部证明、2x效果无依据。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://developers.openai.com/api/docs/guides/prompt-engineering) |
| [Spring Boot 4 AGENTS.md: A Migration Verification Template](../src/content/blog/spring-boot-4-agents-md-guide.md) | 0 / 4 | 文件数等于测试数、verify 自动运行 Failsafe、tests总是真相等互相矛盾规则；移除模型成绩。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide) |
| [Hibernate 7 Migration: Check Schema, Query Types, and Time Values](../src/content/blog/spring-boot-4-hibernate-7-silent-failures.md) | — | nativequery统一OffsetDateTime错误、默认时区臆测、validate能测语义和性能错误、第三方性能倍数。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.hibernate.org/orm/7.0/migration-guide/)、[来源 2](https://docs.hibernate.org/orm/7.1/migration-guide/) |
| [Spring Boot 4 Migration: Verify Contracts Beyond Compilation](../src/content/blog/spring-boot-4-migration-ai-agents.md) | 9 / 278 | 错误支持终止日期、CSRF401误记、Jackson全局替换、agent能力和成绩泛化。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Migration-Guide)、[来源 2](https://spring.io/projects/spring-boot) |
| [Using AI in a Legacy Java Codebase: Preserve Behavior First](../src/content/blog/using-ai-legacy-java-codebase.md) | 1 / 66 | 无原始记录的工作经历与泛化判断；改为具体契约、调用者和特征测试流程。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html) |
| [AI-Assisted PDF to Word: Review the Converter and Its Checks](../src/content/blog/vibe-coding-pdf-word-converter.md) | 0 / 50 | 227 页零乱码与个人开发分工缺乏原始记录；已有真实项目和截图，保留并核对检测器的能力边界。重写：删除无依据经历/成绩，保留具体问题、步骤和验证方法。 | [来源 1](https://github.com/zhoupeng20188/pdf2word)、[来源 2](https://github.com/zhoupeng20188/pdf2word/blob/main/verify.py) |

## 新增可运行材料

[Java 验证项目](../examples/java-verification/README.md)，[公开下载 ZIP](../public/examples/java-verification.zip)。这是新建教学示例，不能充当历史 AI 实验的证据。

环境：macOS 15.5 arm64、Amazon Corretto Java 17.0.19、Maven 3.9.11。项目固定 JUnit 6.0.3、ArchUnit 1.5.0、Surefire 3.5.6。

| 检查 | 实际结果 |
| --- | --- |
| 常规 `clean test` | 9 项，失败 0、错误 0、跳过 0，退出 0 |
| 显式选择 `UndiscoveredShould` | 1 项故意失败，退出 1；确认默认未发现不等于测试通过 |
| ArchUnit 故意违反规则的 fixture | 触发 AssertionError，由测试断言捕获；干净 fixture 通过 |
| 定价边界与舍入 | 99.99、100.00、100.05 及无效输入；100.05 检查 HALF_UP 半分舍入 |
| 所有权 | 所有者可查，另一用户/无身份/不存在记录不可查 |

ZIP 包含源码、命令说明及移除机器系统属性/控制台流后的 JUnit XML；原始命令日志保留于本地审核缓存。它没有 Spring Boot HTTP 层、数据库或付费模型调用，不支持这些层的成功结论。

## 站点层面的修正

- 首页、About、默认描述撤销“每篇均真实项目亲测”的笼统承诺，说明 AI 辅助编辑、来源和证据边界。
- 清除 1111111111 / 2222222222 / 3333333333 假广告位 ID，包括文章侧栏硬编码；没有配置真实广告位就不渲染广告容器。保留现有 AdSense 站点代码及 publisher ID，未创建账户广告单元。
- 修复没有实际地址的 Twitter 链接；移除不存在的站内搜索功能对应的 SearchAction 标记，RSS 不再充当社交身份 sameAs，并缩短首页默认 title。
- 隐私页更新当前集成的表述，补充 Google 说明链接及本地偏好存储，避免把尚未获批写成已经投放广告。
- 两组合并：旧 429 变体 → 429 主指南，Codex CSRF → CSRF 诊断指南；均为带斜杠/不带斜杠直接 301，排在通用重定向规则之前，已更新站内引用。

## 验证结果

- Node 22.23.2 / Astro 7 生产构建通过，生成 63 个内容页面（另保留 Google 验证静态文件）。
- 50 篇文章的单一 H1、canonical、发布日期、更新时间、标题/摘要长度、Article JSON-LD 及可见 FAQ 一致性检查通过。
- 347 个不同内部路径/锚点/资源目标检查通过；缺失目标 0。
- 本地 64 个页面/资源 HTTP 检查全部返回 200，包括示例 ZIP。
- RSS 50 个条目；被合并文章不在 RSS、sitemap 或构建文章目录中，构建产物包含四条特定文章 301 规则。
- 5 个 Python 代码块语法通过；新增有限循环示例的成功、预算耗尽、重复失败、阻塞和无效预算 5 条离线路径通过。首轮 429 示例也已做离线断言。
- 69 个正文外部 URL 检查未发现 404。直接请求中 ChatGPT 入口返回 403，Oracle TLS 曾超时，Spring 项目地址返回跳转；Oracle 和 Spring 页面随后通过网页工具复核可读。外部网络检查不代表所有服务始终可用。
- ZIP 完整性、源码与当前项目一致性、无机器绝对路径检查通过。

## 上线与账户侧仍需确认

本地整改及验证已完成。以下为发布前检查记录，部署状态应以上线检查为准：Cloudflare 的重定向规则在 Astro 开发服务器中不执行，需上线后验证实际 301、目标 200 和 canonical。部署后再核对 AdSense 中的网站状态与拒审说明，并按账户界面提交复审，不能把本地构建成功当作审批成功。

当前自定义 cookie banner 不是已核实的 Google 认证 CMP。本次未访问 AdSense 账户，无法确认是否已配置 Google Privacy & messaging 的欧洲法规消息。GSC 确有欧洲地区访问；若面向欧洲经济区、英国或瑞士用户投放个性化广告，按 [Google 的发布商 CMP 要求](https://support.google.com/adsense/answer/13554116?hl=en)核查账户配置。此项是账户投放准备，不能据此断言它就是本次低价值内容拒审原因。

没有重新执行历史 Spring Boot/安全/迁移实验、付费模型试跑或私有 PDF 转换。相关正文已按实际证据收窄，不再将缺失记录的结果当作确定事实。未来发布标准见 [editorial-standards.md](editorial-standards.md)。

## 审核依据

- [AdSense 未获批准：内容与导航质量](https://support.google.com/adsense/answer/81904?hl=zh-Hans)
- [Google 搜索：实用、可靠、以用户为中心的内容](https://developers.google.com/search/docs/fundamentals/creating-helpful-content?hl=zh-cn)
- 各条目的官方技术文档、源项目和公开 PR，已列在清单与正文中。技术审查和搜索表现分析均不构成 Google 审批承诺。
