# GitHub Actions 配置说明

## 权限设置

如果遇到 403 权限错误，需要在 GitHub 仓库设置中开启 Actions 写入权限：

1. 进入仓库页面
2. 点击 **Settings** (设置)
3. 左侧菜单找到 **Actions** → **General**
4. 滚动到底部找到 **Workflow permissions**
5. 选择 **Read and write permissions** (读写权限)
6. 勾选 **Allow GitHub Actions to create and approve pull requests**
7. 点击 **Save** 保存

## 配置 Secrets

需要在 Settings → Secrets and variables → Actions 中添加：

- `YDHID`
- `MACHINEID`
- `USERNAME`
- `XCXAPPID`

## 运行方式

- **自动运行**: 每天北京时间凌晨 5:00
- **手动运行**: Actions 页面点击 "Run workflow"
