# 世标五金静态测试版

## 功能测试

✅ 商品数据加载（11007个商品）
✅ 搜索功能（按名称或编号）
✅ 图片加载测试（验证防盗链）
✅ PWA 支持（可安装到手机）

## 部署到 GitHub Pages

1. 在 GitHub 创建新仓库（如 `shibiao-static-test`）
2. 把 `static-shop-test` 目录的所有文件推送上去
3. 在仓库设置中启用 GitHub Pages（选择 main 分支）
4. 访问 `https://你的用户名.github.io/shibiao-static-test/`

## 本地测试

由于浏览器安全限制，需要用本地服务器：

```bash
# 方法1：Python
cd static-shop-test
python -m http.server 8000

# 方法2：Node.js
npx serve static-shop-test

# 然后访问 http://localhost:8000
```

## 测试重点

1. **图片加载**：页面顶部会显示图片加载状态
2. **搜索功能**：输入商品名称或编号测试
3. **手机兼容性**：用手机访问测试

## 注意事项

- 图标文件（icon-192.png, icon-512.png）需要自己创建或使用占位图
- 如果图片加载失败，说明有防盗链，需要下载图片到本地
