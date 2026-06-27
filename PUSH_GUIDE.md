# 推送到 GitHub 指南

代码已提交到本地 Git，远程仓库已配置为 `git@github.com:zhoupeng20188/ai-kit-guides.git`

## 方式一：在本地终端运行（推荐）

打开本地终端，进入项目目录，运行：

```bash
cd /Users/forever/github/ai-kit-guides
git push -u origin main
```

如果提示需要 SSH 指纹确认，输入 `yes` 即可。

## 方式二：配置 Personal Access Token (HTTPS)

如果不想用 SSH，可以改用 HTTPS + token：

```bash
# 先切换 remote URL
git remote set-url origin https://github.com/zhoupeng20188/ai-kit-guides.git

# 推送（会提示输入 username 和 token）
git push -u origin main
```

Token 获取方式：
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 复制生成的 token

## 推送后配置 Cloudflare Pages

1. 登录 https://dash.cloudflare.com
2. 进入 Pages → Create a project → Connect to Git
3. 选择 `ai-kit-guides` 仓库
4. 配置构建设置：
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Node.js version: `22`
5. 点击 Save and Deploy

## 修改域名

在 `astro.config.mjs` 中把 `site` 改为你的实际域名（如 `https://aikitguides.com`）。

在 `src/config/site.ts` 中把 `url` 也改为实际域名。

## 申请 AdSense 前检查清单

- [ ] 确保有 25-30 篇高质量文章（目前有 5 篇种子文章）
- [ ] 填写 `src/config/site.ts` 中的真实邮箱
- [ ] 修改 `public/ads.txt` 为你的 AdSense Publisher ID
- [ ] 在 `src/components/AdScript.astro` 和 `InContentAd.astro` 中启用广告
- [ ] 域名注册满 1 个月后再申请
