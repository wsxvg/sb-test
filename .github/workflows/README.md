# 自动更新商品数据

## 功能说明

此 GitHub Actions 工作流会自动抓取最新的商品数据并更新到仓库。

## 运行时间

- **定时任务**: 每天北京时间凌晨 5:00 自动运行
- **手动触发**: 可以在 Actions 页面手动触发

## 配置说明

### 必需的 Secrets

在仓库的 Settings → Secrets and variables → Actions 中添加以下密钥：

| 密钥名称 | 说明 | 示例值 |
|---------|------|--------|
| `YDHID` | 用户ID | `925A0C75146730FFF9078159F7E72C9A` |
| `MACHINEID` | 机器ID | `oztRg413C-XBkvyZdNF4zUYq7i6I` |
| `USERNAME` | 用户名 | `13666527113` |
| `XCXAPPID` | 小程序AppID | `wxebf4afe4b3c9a03d` |

### 如何添加 Secrets

1. 进入仓库页面
2. 点击 Settings（设置）
3. 左侧菜单选择 Secrets and variables → Actions
4. 点击 New repository secret
5. 输入名称和值，点击 Add secret

## 工作流程

1. ✅ 检出代码
2. ✅ 安装 Python 环境和依赖
3. ✅ 运行爬虫脚本抓取数据
4. ✅ 验证数据有效性（文件大小、JSON 格式、商品数量）
5. ✅ 检查数据是否有变化
6. ✅ 如果有变化，自动提交并推送
7. ✅ 如果失败，自动创建 Issue 报告

## 数据验证

工作流会自动检查：

- ✅ `products_db.json` 文件是否生成
- ✅ 文件大小是否合理（至少 100KB）
- ✅ JSON 格式是否正确
- ✅ 商品数量是否正常（至少 10000 个）

如果任何检查失败，工作流会停止并创建 Issue 通知。

## 手动触发

1. 进入仓库的 Actions 页面
2. 选择 "更新商品数据" 工作流
3. 点击 "Run workflow" 按钮
4. 选择分支（通常是 main）
5. 点击绿色的 "Run workflow" 按钮

## 查看运行日志

1. 进入 Actions 页面
2. 点击具体的运行记录
3. 查看每个步骤的详细日志

## 故障排查

### 如果更新失败

1. 检查 Actions 页面的运行日志
2. 查看自动创建的 Issue
3. 确认 Secrets 配置是否正确
4. 检查登录凭证是否过期

### 常见问题

**Q: 为什么没有自动更新？**
A: 检查是否有数据变化，如果数据没变化不会提交。

**Q: 如何修改运行时间？**
A: 编辑 `.github/workflows/update-products.yml` 文件中的 cron 表达式。

**Q: 如何临时停止自动更新？**
A: 在 Actions 页面禁用该工作流，或者删除 workflow 文件。

## 注意事项

⚠️ **重要提示**：
- 确保 Secrets 中的凭证信息正确且未过期
- 定期检查 Actions 运行状态
- 如果连续失败，及时处理 Issue 通知
- GitHub Actions 免费额度：公开仓库无限制，私有仓库每月 2000 分钟
