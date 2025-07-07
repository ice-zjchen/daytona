# Daytona 本地部署与 Python SDK 调度 Docker 完整教程

## 目录
1. [Daytona 简介](#1-daytona-简介)
2. [环境准备](#2-环境准备)
3. [Daytona 本地部署](#3-daytona-本地部署)
4. [Python SDK 使用](#4-python-sdk-使用)
5. [Docker 调度实践](#5-docker-调度实践)
6. [高级用法与最佳实践](#6-高级用法与最佳实践)
7. [常见问题解决](#7-常见问题解决)

## 1. Daytona 简介

Daytona 是一个开源的开发环境管理工具，主要特点：

- **容器化环境**：通过 Docker 容器创建隔离的开发环境
- **配置文件驱动**：使用 `devcontainer.json` 定义环境配置
- **一致性保证**：确保团队成员使用相同的开发环境
- **快速启动**：一条命令创建完整的开发环境
- **多平台支持**：支持 Linux、macOS 和 Windows

### 核心优势
- 解决"在我机器上能跑"的问题
- 支持 GPU 加速，适合 AI/ML 项目
- 与主流 IDE 无缝集成
- 支持远程开发

## 2. 环境准备

### 2.1 系统要求
- **操作系统**：Linux (推荐 Ubuntu 20.04+)、macOS、Windows 10/11
- **内存**：至少 8GB RAM
- **存储**：至少 20GB 可用空间
- **网络**：稳定的互联网连接

### 2.2 必需软件

#### 安装 Docker
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 验证安装
docker --version
docker-compose --version
```

#### 安装 Docker (其他系统)
```bash
# macOS (使用 Homebrew)
brew install --cask docker

# Windows
# 下载并安装 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### 2.3 Python 环境
```bash
# 确保 Python 3.8+ 已安装
python3 --version

# 安装 pip
sudo apt install python3-pip

# 创建虚拟环境
python3 -m venv daytona-env
source daytona-env/bin/activate  # Linux/macOS
# 或 Windows: daytona-env\Scripts\activate
```

## 3. Daytona 本地部署

### 3.1 安装 Daytona

#### 方法 1：直接安装（推荐）
```bash
# Linux/macOS
curl -fsSL https://download.daytona.io/daytona/install.sh | bash

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://download.daytona.io/daytona/latest/daytona-windows-amd64.exe" -OutFile "daytona.exe"
# 将 daytona.exe 添加到 PATH 环境变量
```

#### 方法 2：从源码构建
```bash
# 克隆仓库
git clone https://github.com/daytonaio/daytona.git
cd daytona

# 构建
make build

# 安装
sudo mv bin/daytona /usr/local/bin/
```

### 3.2 启动 Daytona 服务器

```bash
# 启动 Daytona 服务器
daytona server

# 服务器默认运行在 http://localhost:3000
```

### 3.3 配置 Git 提供商

```bash
# 添加 GitHub 提供商
daytona git-provider add

# 选择 GitHub 并提供 Personal Access Token
# Token 需要以下权限：
# - repo (仓库访问)
# - workflow (GitHub Actions)
# - read:user (用户信息)
```

### 3.4 选择 IDE

```bash
# 配置默认 IDE
daytona ide

# 支持的 IDE：
# - VS Code
# - JetBrains 系列
# - Vim/Neovim
# - 浏览器内 IDE
```

## 4. Python SDK 使用

### 4.1 安装 Python SDK

```bash
# 激活虚拟环境
source daytona-env/bin/activate

# 安装 Daytona SDK
pip install daytona-sdk

# 验证安装
python -c "import daytona_sdk; print('Daytona SDK 安装成功')"
```

### 4.2 基础配置

```python
# config.py
from daytona_sdk import Daytona, DaytonaConfig

# 配置 Daytona 客户端
config = DaytonaConfig(
    api_url="http://localhost:3000",  # Daytona 服务器地址
    api_key="your-api-key-here"       # 从 Daytona Dashboard 获取
)

client = Daytona(config)
```

### 4.3 获取 API Key

```bash
# 在 Daytona Dashboard 中获取 API Key
# 访问：http://localhost:3000/dashboard/keys
# 或使用命令行
daytona api-key generate
```

### 4.4 基本 SDK 使用示例

```python
# basic_usage.py
from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
import time

class DaytonaManager:
    def __init__(self, api_key):
        self.config = DaytonaConfig(
            api_url="http://localhost:3000",
            api_key=api_key
        )
        self.client = Daytona(self.config)
    
    def create_sandbox(self, language="python", image=None):
        """创建新的沙盒环境"""
        try:
            params = CreateSandboxParams(
                language=language,
                image=image or "python:3.9"
            )
            
            sandbox = self.client.create(params)
            print(f"✅ 沙盒创建成功: {sandbox.id}")
            return sandbox
            
        except Exception as e:
            print(f"❌ 沙盒创建失败: {e}")
            return None
    
    def list_sandboxes(self):
        """列出所有沙盒"""
        try:
            sandboxes = self.client.list()
            print(f"📦 当前沙盒数量: {len(sandboxes)}")
            for sandbox in sandboxes:
                print(f"  - {sandbox.id}: {sandbox.status}")
            return sandboxes
        except Exception as e:
            print(f"❌ 获取沙盒列表失败: {e}")
            return []
    
    def execute_code(self, sandbox, code):
        """在沙盒中执行代码"""
        try:
            response = sandbox.process.code_run(code)
            if response.exit_code == 0:
                print(f"✅ 代码执行成功:")
                print(f"📝 输出: {response.result}")
            else:
                print(f"❌ 代码执行失败:")
                print(f"🚨 错误: {response.result}")
            return response
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return None
    
    def cleanup_sandbox(self, sandbox):
        """清理沙盒"""
        try:
            self.client.remove(sandbox)
            print(f"🗑️ 沙盒已清理: {sandbox.id}")
        except Exception as e:
            print(f"❌ 清理失败: {e}")

# 使用示例
if __name__ == "__main__":
    # 替换为你的 API Key
    API_KEY = "your-api-key-here"
    
    manager = DaytonaManager(API_KEY)
    
    # 创建沙盒
    sandbox = manager.create_sandbox()
    
    if sandbox:
        # 执行简单的 Python 代码
        test_code = """
print("Hello from Daytona Sandbox!")
import sys
print(f"Python 版本: {sys.version}")

# 简单计算
result = 2 + 2
print(f"2 + 2 = {result}")
"""
        
        manager.execute_code(sandbox, test_code)
        
        # 列出所有沙盒
        manager.list_sandboxes()
        
        # 清理
        time.sleep(2)
        manager.cleanup_sandbox(sandbox)
```

## 5. Docker 调度实践

### 5.1 创建 Dev Container 配置

```json
// .devcontainer/devcontainer.json
{
    "name": "Python ML Environment",
    "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
    
    "features": {
        "ghcr.io/devcontainers/features/docker-in-docker:2": {},
        "ghcr.io/devcontainers/features/nvidia-cuda:1": {
            "installCudnn": true
        }
    },
    
    "customizations": {
        "vscode": {
            "settings": {
                "python.defaultInterpreterPath": "/usr/local/bin/python",
                "python.linting.enabled": true,
                "python.linting.pylintEnabled": true
            },
            "extensions": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-toolsai.jupyter"
            ]
        }
    },
    
    "postCreateCommand": "pip install -r requirements.txt",
    "remoteUser": "vscode",
    
    "forwardPorts": [8888, 6006],
    "portsAttributes": {
        "8888": {
            "label": "Jupyter Lab",
            "onAutoForward": "notify"
        },
        "6006": {
            "label": "TensorBoard",
            "onAutoForward": "notify"
        }
    },
    
    "mounts": [
        "source=${localWorkspaceFolder}/data,target=/workspace/data,type=bind"
    ]
}
```

### 5.2 高级 Docker 调度示例

```python
# docker_scheduler.py
from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
import json
import time

class DockerScheduler:
    def __init__(self, api_key):
        self.config = DaytonaConfig(
            api_url="http://localhost:3000",
            api_key=api_key
        )
        self.client = Daytona(self.config)
        self.active_containers = {}
    
    def create_ml_environment(self):
        """创建机器学习环境"""
        devcontainer_config = {
            "name": "ML Sandbox",
            "image": "tensorflow/tensorflow:2.15.0-gpu-jupyter",
            "features": {
                "ghcr.io/devcontainers/features/nvidia-cuda:1": {
                    "installCudnn": True
                }
            },
            "postCreateCommand": "pip install pandas scikit-learn matplotlib seaborn",
            "forwardPorts": [8888, 6006]
        }
        
        params = CreateSandboxParams(
            language="python",
            devcontainer_config=json.dumps(devcontainer_config)
        )
        
        return self.client.create(params)
    
    def create_web_environment(self):
        """创建 Web 开发环境"""
        devcontainer_config = {
            "name": "Web Dev Sandbox",
            "image": "node:18-bullseye",
            "features": {
                "ghcr.io/devcontainers/features/docker-in-docker:2": {}
            },
            "postCreateCommand": "npm install -g @vue/cli create-react-app",
            "forwardPorts": [3000, 8080, 5173]
        }
        
        params = CreateSandboxParams(
            language="javascript",
            devcontainer_config=json.dumps(devcontainer_config)
        )
        
        return self.client.create(params)
    
    def deploy_model_service(self, sandbox, model_code):
        """部署模型服务"""
        service_code = f"""
import flask
from flask import Flask, request, jsonify
import pickle
import numpy as np

app = Flask(__name__)

# 模型代码
{model_code}

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # 这里添加预测逻辑
        result = {{"prediction": "success", "data": data}}
        return jsonify(result)
    except Exception as e:
        return jsonify({{"error": str(e)}}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({{"status": "healthy"}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
        
        # 在沙盒中执行服务代码
        response = sandbox.process.code_run(service_code)
        return response
    
    def manage_container_lifecycle(self, sandbox_id, action):
        """管理容器生命周期"""
        actions = {
            'start': lambda: self.client.start(sandbox_id),
            'stop': lambda: self.client.stop(sandbox_id),
            'restart': lambda: self.client.restart(sandbox_id),
            'remove': lambda: self.client.remove(sandbox_id)
        }
        
        if action in actions:
            try:
                return actions[action]()
            except Exception as e:
                print(f"❌ 操作 {action} 失败: {e}")
                return None
        else:
            print(f"❌ 不支持的操作: {action}")
            return None
    
    def monitor_resources(self, sandbox):
        """监控资源使用情况"""
        try:
            # 获取容器统计信息
            stats_code = """
import psutil
import json

stats = {
    'cpu_percent': psutil.cpu_percent(interval=1),
    'memory_info': dict(psutil.virtual_memory()._asdict()),
    'disk_usage': dict(psutil.disk_usage('/')._asdict()),
    'network_stats': dict(psutil.net_io_counters()._asdict())
}

print(json.dumps(stats, indent=2))
"""
            
            response = sandbox.process.code_run(stats_code)
            if response.exit_code == 0:
                return json.loads(response.result)
            else:
                return None
                
        except Exception as e:
            print(f"❌ 监控失败: {e}")
            return None

# 使用示例
def main():
    API_KEY = "your-api-key-here"
    scheduler = DockerScheduler(API_KEY)
    
    print("🚀 创建机器学习环境...")
    ml_sandbox = scheduler.create_ml_environment()
    
    if ml_sandbox:
        print(f"✅ ML 环境创建成功: {ml_sandbox.id}")
        
        # 监控资源
        print("📊 监控资源使用...")
        stats = scheduler.monitor_resources(ml_sandbox)
        if stats:
            print(f"CPU 使用率: {stats['cpu_percent']}%")
            print(f"内存使用: {stats['memory_info']['percent']}%")
        
        # 部署简单的模型服务
        model_code = """
def simple_model(data):
    # 简单的线性模型示例
    return sum(data) / len(data) if data else 0
"""
        
        print("🔄 部署模型服务...")
        scheduler.deploy_model_service(ml_sandbox, model_code)
        
        # 等待一段时间后清理
        time.sleep(10)
        print("🗑️ 清理环境...")
        scheduler.manage_container_lifecycle(ml_sandbox.id, 'remove')

if __name__ == "__main__":
    main()
```

### 5.3 批量容器管理

```python
# batch_manager.py
from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
import concurrent.futures
import time

class BatchContainerManager:
    def __init__(self, api_key):
        self.config = DaytonaConfig(
            api_url="http://localhost:3000",
            api_key=api_key
        )
        self.client = Daytona(self.config)
    
    def create_multiple_sandboxes(self, configs):
        """并行创建多个沙盒"""
        def create_single(config):
            try:
                params = CreateSandboxParams(**config)
                sandbox = self.client.create(params)
                return {"success": True, "sandbox": sandbox, "config": config}
            except Exception as e:
                return {"success": False, "error": str(e), "config": config}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_single, config) for config in configs]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results
    
    def execute_parallel_tasks(self, sandboxes, tasks):
        """在多个沙盒中并行执行任务"""
        def execute_task(sandbox_task):
            sandbox, task = sandbox_task
            try:
                response = sandbox.process.code_run(task['code'])
                return {
                    "sandbox_id": sandbox.id,
                    "task_name": task['name'],
                    "success": response.exit_code == 0,
                    "result": response.result
                }
            except Exception as e:
                return {
                    "sandbox_id": sandbox.id,
                    "task_name": task['name'],
                    "success": False,
                    "error": str(e)
                }
        
        sandbox_tasks = [(sandbox, task) for sandbox in sandboxes for task in tasks]
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(sandboxes)) as executor:
            futures = [executor.submit(execute_task, st) for st in sandbox_tasks]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results
    
    def cleanup_all(self, sandboxes):
        """清理所有沙盒"""
        def cleanup_single(sandbox):
            try:
                self.client.remove(sandbox)
                return {"success": True, "sandbox_id": sandbox.id}
            except Exception as e:
                return {"success": False, "sandbox_id": sandbox.id, "error": str(e)}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(cleanup_single, sandbox) for sandbox in sandboxes]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return results

# 使用示例
def batch_processing_example():
    API_KEY = "your-api-key-here"
    manager = BatchContainerManager(API_KEY)
    
    # 定义多个环境配置
    configs = [
        {"language": "python", "image": "python:3.9"},
        {"language": "python", "image": "python:3.10"},
        {"language": "python", "image": "python:3.11"},
    ]
    
    print("🚀 批量创建沙盒环境...")
    results = manager.create_multiple_sandboxes(configs)
    
    successful_sandboxes = [r["sandbox"] for r in results if r["success"]]
    print(f"✅ 成功创建 {len(successful_sandboxes)} 个沙盒")
    
    # 定义要执行的任务
    tasks = [
        {
            "name": "python_version",
            "code": "import sys; print(f'Python {sys.version}')"
        },
        {
            "name": "basic_computation",
            "code": "result = sum(range(1000)); print(f'Sum: {result}')"
        }
    ]
    
    if successful_sandboxes:
        print("⚡ 执行并行任务...")
        task_results = manager.execute_parallel_tasks(successful_sandboxes, tasks)
        
        for result in task_results:
            if result["success"]:
                print(f"✅ {result['task_name']} @ {result['sandbox_id']}: {result['result']}")
            else:
                print(f"❌ {result['task_name']} @ {result['sandbox_id']}: {result.get('error', 'Unknown error')}")
        
        # 清理所有沙盒
        print("🗑️ 清理所有沙盒...")
        cleanup_results = manager.cleanup_all(successful_sandboxes)
        successful_cleanups = sum(1 for r in cleanup_results if r["success"])
        print(f"✅ 成功清理 {successful_cleanups} 个沙盒")

if __name__ == "__main__":
    batch_processing_example()
```

## 6. 高级用法与最佳实践

### 6.1 环境模板管理

```python
# template_manager.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import json

@dataclass
class EnvironmentTemplate:
    name: str
    description: str
    image: str
    features: Dict
    extensions: List[str]
    settings: Dict
    post_create_commands: List[str]
    forward_ports: List[int]

class TemplateManager:
    def __init__(self):
        self.templates = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """加载默认模板"""
        # 数据科学模板
        self.templates["data-science"] = EnvironmentTemplate(
            name="数据科学环境",
            description="包含 Jupyter、pandas、scikit-learn 等工具",
            image="jupyter/datascience-notebook:latest",
            features={
                "ghcr.io/devcontainers/features/nvidia-cuda:1": {
                    "installCudnn": True
                }
            },
            extensions=[
                "ms-python.python",
                "ms-toolsai.jupyter",
                "ms-python.vscode-pylance"
            ],
            settings={
                "python.defaultInterpreterPath": "/opt/conda/bin/python"
            },
            post_create_commands=[
                "pip install mlflow wandb",
                "conda install -c conda-forge dask"
            ],
            forward_ports=[8888, 4040]
        )
        
        # Web 开发模板
        self.templates["web-dev"] = EnvironmentTemplate(
            name="Web 开发环境",
            description="Node.js + React/Vue 开发环境",
            image="node:18-bullseye",
            features={
                "ghcr.io/devcontainers/features/docker-in-docker:2": {}
            },
            extensions=[
                "ms-vscode.vscode-typescript-next",
                "bradlc.vscode-tailwindcss",
                "esbenp.prettier-vscode"
            ],
            settings={
                "editor.formatOnSave": True,
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            post_create_commands=[
                "npm install -g @vue/cli create-react-app",
                "npm install -g typescript ts-node"
            ],
            forward_ports=[3000, 8080, 5173]
        )
    
    def get_template(self, name: str) -> Optional[EnvironmentTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def create_devcontainer_config(self, template_name: str) -> Dict:
        """基于模板创建 devcontainer 配置"""
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"模板 '{template_name}' 不存在")
        
        config = {
            "name": template.name,
            "image": template.image,
            "features": template.features,
            "customizations": {
                "vscode": {
                    "extensions": template.extensions,
                    "settings": template.settings
                }
            },
            "postCreateCommand": " && ".join(template.post_create_commands),
            "forwardPorts": template.forward_ports
        }
        
        return config
    
    def add_custom_template(self, template: EnvironmentTemplate):
        """添加自定义模板"""
        self.templates[template.name] = template
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())

# 使用示例
template_manager = TemplateManager()
print("可用模板:", template_manager.list_templates())

# 创建数据科学环境配置
ds_config = template_manager.create_devcontainer_config("data-science")
print("数据科学环境配置:")
print(json.dumps(ds_config, indent=2, ensure_ascii=False))
```

### 6.2 自动化工作流

```python
# workflow_automation.py
from daytona_sdk import Daytona, DaytonaConfig
import yaml
import time
from typing import List, Dict, Any

class WorkflowAutomation:
    def __init__(self, api_key: str):
        self.config = DaytonaConfig(api_key=api_key)
        self.client = Daytona(self.config)
        self.workflows = {}
    
    def load_workflow(self, workflow_file: str):
        """从 YAML 文件加载工作流定义"""
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow = yaml.safe_load(f)
        
        workflow_name = workflow.get('name')
        self.workflows[workflow_name] = workflow
        return workflow_name
    
    def execute_workflow(self, workflow_name: str, variables: Dict[str, Any] = None):
        """执行工作流"""
        if workflow_name not in self.workflows:
            raise ValueError(f"工作流 '{workflow_name}' 不存在")
        
        workflow = self.workflows[workflow_name]
        variables = variables or {}
        
        print(f"🚀 开始执行工作流: {workflow_name}")
        
        # 创建环境
        sandbox = self._create_environment(workflow.get('environment', {}))
        if not sandbox:
            return None
        
        try:
            # 执行步骤
            results = []
            for step in workflow.get('steps', []):
                result = self._execute_step(sandbox, step, variables)
                results.append(result)
                
                if not result.get('success', False):
                    print(f"❌ 步骤失败: {step.get('name', 'Unknown')}")
                    break
            
            # 收集输出
            outputs = self._collect_outputs(sandbox, workflow.get('outputs', []))
            
            return {
                'success': all(r.get('success', False) for r in results),
                'results': results,
                'outputs': outputs,
                'sandbox_id': sandbox.id
            }
            
        finally:
            # 清理环境（如果配置了自动清理）
            if workflow.get('cleanup', True):
                self.client.remove(sandbox)
    
    def _create_environment(self, env_config: Dict) -> Any:
        """创建环境"""
        # 这里可以根据 env_config 创建相应的沙盒
        # 示例实现
        return self.client.create(env_config)
    
    def _execute_step(self, sandbox: Any, step: Dict, variables: Dict) -> Dict:
        """执行单个步骤"""
        step_name = step.get('name', 'Unknown Step')
        print(f"⚡ 执行步骤: {step_name}")
        
        # 替换变量
        command = step.get('command', '')
        for var, value in variables.items():
            command = command.replace(f"${{{var}}}", str(value))
        
        try:
            response = sandbox.process.code_run(command)
            success = response.exit_code == 0
            
            if success:
                print(f"✅ 步骤成功: {step_name}")
            else:
                print(f"❌ 步骤失败: {step_name}")
                print(f"错误: {response.result}")
            
            return {
                'step_name': step_name,
                'success': success,
                'output': response.result,
                'exit_code': response.exit_code
            }
            
        except Exception as e:
            print(f"❌ 步骤异常: {step_name} - {e}")
            return {
                'step_name': step_name,
                'success': False,
                'error': str(e)
            }
    
    def _collect_outputs(self, sandbox: Any, output_configs: List[Dict]) -> Dict:
        """收集输出"""
        outputs = {}
        
        for output_config in output_configs:
            name = output_config.get('name')
            command = output_config.get('command')
            
            try:
                response = sandbox.process.code_run(command)
                if response.exit_code == 0:
                    outputs[name] = response.result
                else:
                    outputs[name] = f"Error: {response.result}"
            except Exception as e:
                outputs[name] = f"Exception: {e}"
        
        return outputs

# 工作流配置示例 (workflow.yaml)
workflow_yaml_example = """
name: "ml_model_training"
description: "机器学习模型训练工作流"

environment:
  language: "python"
  image: "tensorflow/tensorflow:2.15.0-gpu"

variables:
  dataset_url: "https://example.com/dataset.csv"
  model_name: "my_model"
  epochs: 10

steps:
  - name: "安装依赖"
    command: |
      pip install pandas scikit-learn matplotlib

  - name: "下载数据"
    command: |
      wget ${dataset_url} -O dataset.csv

  - name: "训练模型"
    command: |
      python -c "
      import pandas as pd
      from sklearn.model_selection import train_test_split
      from sklearn.linear_model import LogisticRegression
      import pickle
      
      # 读取数据（示例）
      data = pd.read_csv('dataset.csv')
      # 这里添加实际的训练逻辑
      
      # 保存模型
      model = LogisticRegression()
      with open('${model_name}.pkl', 'wb') as f:
          pickle.dump(model, f)
      
      print('模型训练完成')
      "

  - name: "验证模型"
    command: |
      python -c "
      import pickle
      
      with open('${model_name}.pkl', 'rb') as f:
          model = pickle.load(f)
      
      print('模型验证通过')
      "

outputs:
  - name: "model_file"
    command: "ls -la ${model_name}.pkl"
  
  - name: "training_log"
    command: "cat training.log"

cleanup: true
"""

# 保存示例工作流
with open('ml_workflow.yaml', 'w', encoding='utf-8') as f:
    f.write(workflow_yaml_example)

# 使用示例
def run_workflow_example():
    API_KEY = "your-api-key-here"
    automation = WorkflowAutomation(API_KEY)
    
    # 加载工作流
    workflow_name = automation.load_workflow('ml_workflow.yaml')
    
    # 执行工作流
    variables = {
        'dataset_url': 'https://raw.githubusercontent.com/datasets/iris/master/data/iris.csv',
        'model_name': 'iris_model',
        'epochs': 5
    }
    
    result = automation.execute_workflow(workflow_name, variables)
    
    if result and result['success']:
        print("🎉 工作流执行成功!")
        print("输出:")
        for name, output in result['outputs'].items():
            print(f"  {name}: {output}")
    else:
        print("❌ 工作流执行失败")

if __name__ == "__main__":
    run_workflow_example()
```

## 7. 常见问题解决

### 7.1 连接问题

```python
# troubleshooting.py
import requests
import time
from daytona_sdk import DaytonaConfig

def check_daytona_server(url="http://localhost:3000"):
    """检查 Daytona 服务器状态"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Daytona 服务器运行正常")
            return True
        else:
            print(f"⚠️ Daytona 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到 Daytona 服务器: {e}")
        return False

def validate_api_key(api_key, server_url="http://localhost:3000"):
    """验证 API Key"""
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(f"{server_url}/api/user", headers=headers, timeout=5)
        
        if response.status_code == 200:
            print("✅ API Key 有效")
            return True
        elif response.status_code == 401:
            print("❌ API Key 无效或已过期")
            return False
        else:
            print(f"⚠️ 验证 API Key 时出现异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 验证 API Key 时发生错误: {e}")
        return False

def diagnose_docker_issues():
    """诊断 Docker 问题"""
    import subprocess
    
    try:
        # 检查 Docker 是否运行
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker 已安装")
            print(f"版本: {result.stdout.strip()}")
        else:
            print("❌ Docker 未正确安装")
            return False
        
        # 检查 Docker 服务状态
        result = subprocess.run(['docker', 'info'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker 服务运行正常")
        else:
            print("❌ Docker 服务未运行")
            print("请启动 Docker 服务: sudo systemctl start docker")
            return False
        
        # 检查用户权限
        result = subprocess.run(['docker', 'ps'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Docker 权限正常")
        else:
            print("⚠️ Docker 权限问题")
            print("请将用户添加到 docker 组: sudo usermod -aG docker $USER")
            print("然后重新登录")
            
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Docker 命令执行超时")
        return False
    except FileNotFoundError:
        print("❌ Docker 未安装")
        return False

def system_diagnostics():
    """系统诊断"""
    print("🔍 开始系统诊断...")
    print("=" * 50)
    
    # 检查 Daytona 服务器
    print("1. 检查 Daytona 服务器状态:")
    server_ok = check_daytona_server()
    print()
    
    # 检查 Docker
    print("2. 检查 Docker 状态:")
    docker_ok = diagnose_docker_issues()
    print()
    
    # 检查 Python 环境
    print("3. 检查 Python 环境:")
    try:
        import daytona_sdk
        print("✅ Daytona SDK 已安装")
        print(f"版本: {daytona_sdk.__version__}")
    except ImportError:
        print("❌ Daytona SDK 未安装")
        print("请运行: pip install daytona-sdk")
    except AttributeError:
        print("✅ Daytona SDK 已安装（版本信息不可用）")
    print()
    
    # 总结
    print("诊断结果:")
    if server_ok and docker_ok:
        print("🎉 系统配置正常，可以开始使用 Daytona!")
    else:
        print("⚠️ 发现问题，请根据上述提示进行修复")

if __name__ == "__main__":
    system_diagnostics()
```

### 7.2 性能优化

```python
# performance_optimization.py
import psutil
import time
from daytona_sdk import Daytona, DaytonaConfig

class PerformanceOptimizer:
    def __init__(self, api_key):
        self.config = DaytonaConfig(api_key=api_key)
        self.client = Daytona(self.config)
    
    def optimize_sandbox_resources(self, sandbox, cpu_limit=None, memory_limit=None):
        """优化沙盒资源配置"""
        optimization_script = f"""
import os
import subprocess

# 设置 CPU 限制
if {cpu_limit is not None}:
    # 这里可以添加 CPU 限制逻辑
    print(f"设置 CPU 限制: {cpu_limit}")

# 设置内存限制  
if {memory_limit is not None}:
    # 这里可以添加内存限制逻辑
    print(f"设置内存限制: {memory_limit}")

# 清理不必要的进程
subprocess.run(['apt-get', 'clean'], check=False)
subprocess.run(['apt-get', 'autoremove', '-y'], check=False)

print("资源优化完成")
"""
        
        return sandbox.process.code_run(optimization_script)
    
    def monitor_performance(self, sandbox, duration=60):
        """监控性能指标"""
        monitoring_script = f"""
import psutil
import time
import json

def collect_metrics():
    return {{
        'timestamp': time.time(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory': dict(psutil.virtual_memory()._asdict()),
        'disk': dict(psutil.disk_usage('/')._asdict()),
        'network': dict(psutil.net_io_counters()._asdict()),
        'processes': len(psutil.pids())
    }}

metrics = []
start_time = time.time()

while time.time() - start_time < {duration}:
    metrics.append(collect_metrics())
    time.sleep(5)

# 计算平均值
if metrics:
    avg_cpu = sum(m['cpu_percent'] for m in metrics) / len(metrics)
    avg_memory = sum(m['memory']['percent'] for m in metrics) / len(metrics)
    
    print(f"平均 CPU 使用率: {{avg_cpu:.2f}}%")
    print(f"平均内存使用率: {{avg_memory:.2f}}%")
    print(f"采集了 {{len(metrics)}} 个数据点")
else:
    print("未采集到性能数据")
"""
        
        return sandbox.process.code_run(monitoring_script)
    
    def suggest_optimizations(self):
        """建议优化措施"""
        print("💡 性能优化建议:")
        print("1. 定期清理未使用的沙盒")
        print("2. 使用资源限制避免单个沙盒占用过多资源") 
        print("3. 监控系统资源使用情况")
        print("4. 使用 SSD 存储提高 I/O 性能")
        print("5. 增加内存可以提高容器启动速度")

# 使用示例
def optimize_performance():
    API_KEY = "your-api-key-here"
    optimizer = PerformanceOptimizer(API_KEY)
    
    # 显示优化建议
    optimizer.suggest_optimizations()

if __name__ == "__main__":
    optimize_performance()
```

## 总结

通过本教程，您已经学会了：

1. **Daytona 的基本概念和安装**
2. **Python SDK 的使用方法**
3. **Docker 容器的调度和管理**
4. **高级功能如批量管理、模板系统、工作流自动化**
5. **故障排除和性能优化**

### 下一步建议

1. **探索更多模板**：创建适合您项目的自定义环境模板
2. **集成 CI/CD**：将 Daytona 集成到您的持续集成流程中
3. **团队协作**：设置团队共享的开发环境
4. **监控和日志**：建立完善的监控和日志系统

### 有用的资源

- [Daytona 官方文档](https://docs.daytona.io)
- [Dev Container 规范](https://containers.dev)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)

祝您使用 Daytona 愉快！🚀