<div align="center">

[![Documentation](https://img.shields.io/github/v/release/daytonaio/docs?label=Docs&color=23cc71)](https://www.daytona.io/docs)
![License](https://img.shields.io/badge/License-AGPL--3-blue)
[![Go Report Card](https://goreportcard.com/badge/github.com/daytonaio/daytona)](https://goreportcard.com/report/github.com/daytonaio/daytona)
[![Issues - daytona](https://img.shields.io/github/issues/daytonaio/daytona)](https://github.com/daytonaio/daytona/issues)
![GitHub Release](https://img.shields.io/github/v/release/daytonaio/daytona)

</div>

&nbsp;

<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/daytonaio/daytona/raw/main/assets/images/Daytona-logotype-white.png">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/daytonaio/daytona/raw/main/assets/images/Daytona-logotype-black.png">
    <img alt="Daytona logo" src="https://github.com/daytonaio/daytona/raw/main/assets/images/Daytona-logotype-black.png" width="50%">
  </picture>
</div>

<h3 align="center">
  Run AI Code.
  <br/>
  Secure and Elastic Infrastructure for
  Running Your AI-Generated Code.
</h3>

<p align="center">
    <a href="https://www.daytona.io/docs"> Documentation </a>·
    <a href="https://github.com/daytonaio/daytona/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=%F0%9F%90%9B+Bug+Report%3A+"> Report Bug </a>·
    <a href="https://github.com/daytonaio/daytona/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.md&title=%F0%9F%9A%80+Feature%3A+"> Request Feature </a>·
    <a href="https://go.daytona.io/slack"> Join our Slack </a>·
    <a href="https://x.com/daytonaio"> Connect on X </a>
</p>

<p align="center">
    <a href="https://www.producthunt.com/posts/daytona-2?embed=true&utm_source=badge-top-post-badge&utm_medium=badge&utm_souce=badge-daytona&#0045;2" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/top-post-badge.svg?post_id=957617&theme=neutral&period=daily&t=1746176740150" alt="Daytona&#0032; - Secure&#0032;and&#0032;elastic&#0032;infra&#0032;for&#0032;running&#0032;your&#0032;AI&#0045;generated&#0032;code&#0046; | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
    <a href="https://www.producthunt.com/posts/daytona-2?embed=true&utm_source=badge-top-post-topic-badge&utm_medium=badge&utm_souce=badge-daytona&#0045;2" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/top-post-topic-badge.svg?post_id=957617&theme=neutral&period=monthly&topic_id=237&t=1746176740150" alt="Daytona&#0032; - Secure&#0032;and&#0032;elastic&#0032;infra&#0032;for&#0032;running&#0032;your&#0032;AI&#0045;generated&#0032;code&#0046; | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p>

---

## Installation

### Python SDK

```bash
pip install daytona
```

### TypeScript SDK

```bash
npm install @daytonaio/sdk
```

---

## Features

- **Lightning-Fast Infrastructure**: Sub-90ms Sandbox creation from code to execution.
- **Separated & Isolated Runtime**: Execute AI-generated code with zero risk to your infrastructure.
- **Massive Parallelization for Concurrent AI Workflows**: Fork Sandbox filesystem and memory state (Coming soon!)
- **Programmatic Control**: File, Git, LSP, and Execute API
- **Unlimited Persistence**: Your Sandboxes can live forever
- **OCI/Docker Compatibility**: Use any OCI/Docker image to create a Sandbox

---

## Quick Start

1. Create an account at https://app.daytona.io
1. Generate a [new API key](https://app.daytona.io/dashboard/keys)
1. Follow the [Getting Started docs](https://www.daytona.io/docs/getting-started/) to start using the Daytona SDK

## Creating your first Sandbox

### Python SDK

```py
from daytona import Daytona, DaytonaConfig, CreateSandboxParams

# Initialize the Daytona client
daytona = Daytona(DaytonaConfig(api_key="YOUR_API_KEY"))

# Create the Sandbox instance
sandbox = daytona.create(CreateSandboxParams(language="python"))

# Run code securely inside the Sandbox
response = sandbox.process.code_run('print("Sum of 3 and 4 is " + str(3 + 4))')
if response.exit_code != 0:
    print(f"Error running code: {response.exit_code} {response.result}")
else:
    print(response.result)

# Clean up the Sandbox
daytona.remove(sandbox)
```

### Typescript SDK

```jsx
import { Daytona } from '@daytonaio/sdk'

async function main() {
  // Initialize the Daytona client
  const daytona = new Daytona({
    apiKey: 'YOUR_API_KEY',
  })

  let sandbox
  try {
    // Create the Sandbox instance
    sandbox = await daytona.create({
      language: 'python',
    })
    // Run code securely inside the Sandbox
    const response = await sandbox.process.codeRun('print("Sum of 3 and 4 is " + str(3 + 4))')
    if (response.exitCode !== 0) {
      console.error('Error running code:', response.exitCode, response.result)
    } else {
      console.log(response.result)
    }
  } catch (error) {
    console.error('Sandbox flow error:', error)
  } finally {
    if (sandbox) await daytona.remove(sandbox)
  }
}

main().catch(console.error)
```

---

## Contributing

Daytona is Open Source under the [GNU AFFERO GENERAL PUBLIC LICENSE](LICENSE), and is the [copyright of its contributors](NOTICE). If you would like to contribute to the software, read the Developer Certificate of Origin Version 1.1 (https://developercertificate.org/). Afterwards, navigate to the [contributing guide](CONTRIBUTING.md) to get started.

# 🚀 Daytona 本地部署修复版本

## 📋 概述

本项目包含了经过完整测试和修复的 Daytona 本地部署配置，解决了所有常见的部署问题。

## 🛠️ 修复的问题

- ✅ **API 密钥配置问题** - 自动生成和管理
- ✅ **Docker 镜像版本问题** - 使用稳定的官方镜像
- ✅ **端口冲突问题** - 配置非标准端口避免冲突
- ✅ **Feature 路径错误** - 使用正确的官方 Feature 路径
- ✅ **Python SDK 连接问题** - 完整的错误处理和重试机制
- ✅ **容器配置语法错误** - 所有配置文件语法验证通过

## 🚀 快速开始

### 1. 一键部署验证

```bash
# 下载并运行验证脚本
chmod +x deploy_verification.sh
./deploy_verification.sh
```

### 2. 手动验证

```bash
# 运行 Python 验证脚本
python3 fixed_basic_usage.py
```

## 📁 文件说明

| 文件 | 描述 |
|------|------|
| `deploy_verification.sh` | 🔧 一键部署验证脚本 |
| `fixed_basic_usage.py` | 🐍 修复后的 Python SDK 示例 |
| `Daytona_配置修复与验证指南.md` | 📖 详细修复说明 |
| `requirements.txt` | 📦 Python 依赖包列表 |
| `.devcontainer/` | 🐳 容器配置目录 |

## 🎯 验证步骤

验证脚本会自动执行以下步骤：

1. **检查系统依赖** - Docker, Python, curl 等
2. **安装 Daytona** - 自动下载和安装
3. **启动服务** - 启动 Daytona 服务器
4. **生成 API Key** - 自动生成和配置
5. **测试连接** - 验证 API 连接
6. **创建沙盒** - 测试沙盒创建
7. **运行测试** - 综合功能测试

## 📊 验证结果

成功部署后，您将看到：

```
✅ Daytona 服务器: 运行中
✅ Docker 服务: 运行中
✅ API 连接: 正常
✅ 沙盒创建: 成功
✅ 代码执行: 正常
```

## 🔗 访问方式

- **Web 界面**: http://localhost:3000
- **API 地址**: http://localhost:3000/api
- **健康检查**: http://localhost:3000/health

## 💡 常用命令

```bash
# 查看工作区
daytona list

# 创建工作区
daytona create

# 查看日志
tail -f daytona.log

# 重启服务
pkill -f 'daytona server' && daytona server

# 生成新的 API Key
daytona api-key generate --name my-key
```

## 🐳 Container 配置

### 基础 Python 环境

```json
{
  "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "version": "24.0"
    }
  },
  "forwardPorts": [8000, 8888],
  "remoteUser": "vscode"
}
```

### AI/ML 环境

```json
{
  "image": "nvidia/cuda:11.8-devel-ubuntu22.04",
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.10"
    },
    "ghcr.io/devcontainers/features/nvidia-cuda:1": {
      "installCudnn": true
    }
  }
}
```

## 🔧 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口占用
   sudo netstat -tulpn | grep :3000
   
   # 终止冲突进程
   sudo kill -9 $(sudo lsof -t -i:3000)
   ```

2. **Docker 权限问题**
   ```bash
   # 添加用户到 docker 组
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **API Key 失效**
   ```bash
   # 重新生成 API Key
   daytona api-key generate --name new-key
   export DAYTONA_API_KEY="your-new-key"
   ```

### 重置环境

```bash
# 停止所有容器
docker stop $(docker ps -aq)

# 清理 Daytona 数据
rm -rf ~/.daytona

# 重新启动
daytona server
```

## 📚 参考资源

- [Daytona 官方文档](https://docs.daytona.io/)
- [Dev Container 规范](https://containers.dev/)
- [Docker 官方文档](https://docs.docker.com/)

## 🤝 贡献

如果您发现任何问题或有改进建议，请：

1. 检查现有的问题描述
2. 创建详细的问题报告
3. 提供复现步骤
4. 包含系统信息和日志

## 📄 许可证

本项目采用 MIT 许可证。

## 🎉 成功部署确认

当您看到以下信息时，表示部署成功：

```
🎉 恭喜！Daytona 部署完全成功
✅ 所有功能正常工作
🌐 Web 界面: http://localhost:3000
🔑 API Key: abcdef1234...
```

现在您可以开始使用 Daytona 进行开发了！🚀
