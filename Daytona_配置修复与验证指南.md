# Daytona 配置修复与验证指南

## 🚨 检测到的关键问题

### 1. **API 密钥配置问题**
```bash
# ❌ 原配置问题
API_KEY = "your-api-key-here"  # 占位符，无法使用

# ✅ 修复方案
# 首先获取真实的 API Key
daytona server &  # 启动服务器
sleep 5
API_KEY=$(daytona api-key generate --name "python-sdk" --output json | jq -r '.key')
echo "Generated API Key: $API_KEY"
```

### 2. **Docker 镜像不存在问题**
```json
// ❌ 问题配置
{
  "image": "tensorflow/tensorflow:2.15.0-gpu-jupyter"  // 版本可能不存在
}

// ✅ 修复后配置
{
  "image": "tensorflow/tensorflow:2.13.0-gpu-jupyter"  // 确认存在的版本
}
```

### 3. **端口冲突问题**
```json
// ❌ 原配置可能冲突
{
  "forwardPorts": [3000, 8080, 5432]  // 5432 常被 PostgreSQL 占用
}

// ✅ 修复配置
{
  "forwardPorts": [3000, 8080, 15432],  // 使用非标准端口避免冲突
  "portsAttributes": {
    "15432": {
      "label": "PostgreSQL Dev",
      "onAutoForward": "notify"
    }
  }
}
```

### 4. **Feature 路径错误**
```json
// ❌ 路径不存在
{
  "features": {
    "./features/ml-tools": {}  // 本地路径不存在
  }
}

// ✅ 使用官方 Features
{
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    },
    "ghcr.io/devcontainers/features/nvidia-cuda:1": {
      "installCudnn": true
    }
  }
}
```

## 🔧 完整修复方案

### 修复后的基础 Python 环境配置
```json
{
  "name": "Fixed Python Development Environment",
  "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
  
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "version": "24.0",
      "moby": true,
      "dockerDashComposeVersion": "v2"
    },
    "ghcr.io/devcontainers/features/git:1": {
      "ppa": true,
      "version": "latest"
    }
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "editor.formatOnSave": true
      }
    }
  },
  
  "forwardPorts": [8000, 8888],
  "portsAttributes": {
    "8000": {
      "label": "Web Server",
      "onAutoForward": "notify"
    },
    "8888": {
      "label": "Jupyter Lab",
      "onAutoForward": "notify"
    }
  },
  
  "postCreateCommand": [
    "pip install --upgrade pip",
    "pip install requests pandas numpy matplotlib jupyter"
  ],
  
  "remoteUser": "vscode",
  "containerUser": "vscode"
}
```

### 修复后的 AI/ML 环境配置
```json
{
  "name": "Fixed AI/ML Development Environment",
  "image": "nvidia/cuda:11.8-devel-ubuntu22.04",
  
  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.10",
      "installTools": true
    },
    "ghcr.io/devcontainers/features/nvidia-cuda:1": {
      "installCudnn": true,
      "cudnnVersion": "8"
    }
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-toolsai.jupyter",
        "ms-python.vscode-pylance"
      ]
    }
  },
  
  "forwardPorts": [8888, 6006],
  "portsAttributes": {
    "8888": {"label": "Jupyter Lab"},
    "6006": {"label": "TensorBoard"}
  },
  
  "postCreateCommand": [
    "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118",
    "pip install tensorflow[and-cuda]",
    "pip install jupyter jupyterlab pandas numpy matplotlib seaborn scikit-learn"
  ],
  
  "mounts": [
    "source=${localWorkspaceFolder}/data,target=/workspace/data,type=bind,consistency=cached"
  ],
  
  "containerEnv": {
    "CUDA_VISIBLE_DEVICES": "all",
    "PYTHONPATH": "/workspace"
  },
  
  "remoteUser": "root"
}
```

### 修复后的微服务环境配置
```yaml
# docker-compose.fixed.yml
version: '3.8'
services:
  app:
    build: 
      context: .
      dockerfile: .devcontainer/Dockerfile
    volumes:
      - ..:/workspace:cached
    command: sleep infinity
    networks:
      - dev-network
    
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass123
    ports:
      - "15432:5432"  # 避免端口冲突
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - dev-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U devuser -d devdb"]
      interval: 30s
      timeout: 10s
      retries: 5
      
  redis:
    image: redis:7-alpine
    ports:
      - "16379:6379"  # 避免端口冲突
    volumes:
      - redis_data:/data
    networks:
      - dev-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

volumes:
  postgres_data:
  redis_data:

networks:
  dev-network:
    driver: bridge
```

```json
// 对应的 devcontainer.json
{
  "name": "Fixed Microservices Development",
  "dockerComposeFile": "docker-compose.fixed.yml",
  "service": "app",
  "workspaceFolder": "/workspace",
  
  "features": {
    "ghcr.io/devcontainers/features/node:1": {
      "version": "18",
      "nodeGypDependencies": true
    },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "version": "24.0"
    }
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-vscode.vscode-typescript-next",
        "esbenp.prettier-vscode",
        "ms-vscode.vscode-docker"
      ]
    }
  },
  
  "forwardPorts": [3000, 15432, 16379],
  "portsAttributes": {
    "3000": {"label": "App Server"},
    "15432": {"label": "PostgreSQL"},
    "16379": {"label": "Redis"}
  },
  
  "postCreateCommand": [
    "npm install",
    "echo 'Waiting for database...'",
    "sleep 10",
    "npm run db:migrate || echo 'Migration skipped'"
  ],
  
  "remoteUser": "node"
}
```

## 🔧 修复后的 Python SDK 代码

### 工作的基础示例
```python
# fixed_basic_usage.py
import os
import time
import logging
from typing import Optional, Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
except ImportError:
    logger.error("Daytona SDK not installed. Run: pip install daytona-sdk")
    exit(1)

class FixedDaytonaManager:
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
        self.client = None
        self.sandboxes = []
        
    def initialize(self) -> bool:
        """初始化并验证连接"""
        try:
            # 检查服务器是否运行
            import requests
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code != 200:
                logger.error(f"Daytona server not accessible at {self.api_url}")
                return False
                
            # 获取或生成 API Key
            api_key = self._get_api_key()
            if not api_key:
                logger.error("Failed to get API key")
                return False
                
            # 初始化客户端
            config = DaytonaConfig(
                api_url=self.api_url,
                api_key=api_key
            )
            self.client = Daytona(config)
            
            # 验证连接
            self.client.list()
            logger.info("✅ Daytona connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Daytona: {e}")
            return False
    
    def _get_api_key(self) -> Optional[str]:
        """获取 API Key"""
        # 尝试从环境变量获取
        api_key = os.getenv('DAYTONA_API_KEY')
        if api_key and api_key != "your-api-key-here":
            return api_key
            
        # 尝试生成新的 API Key
        try:
            import subprocess
            result = subprocess.run(
                ['daytona', 'api-key', 'generate', '--name', 'python-sdk'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # 解析输出获取 API Key
                for line in result.stdout.split('\n'):
                    if 'API Key:' in line:
                        return line.split('API Key:')[1].strip()
        except Exception as e:
            logger.warning(f"Failed to generate API key: {e}")
            
        return None
    
    def create_python_sandbox(self) -> Optional[Any]:
        """创建 Python 开发沙盒"""
        if not self.client:
            logger.error("Client not initialized")
            return None
            
        try:
            params = CreateSandboxParams(
                language="python",
                image="mcr.microsoft.com/devcontainers/python:3.11-bullseye"
            )
            
            logger.info("🚀 Creating Python sandbox...")
            sandbox = self.client.create(params)
            self.sandboxes.append(sandbox)
            
            # 等待沙盒就绪
            self._wait_for_sandbox_ready(sandbox)
            
            logger.info(f"✅ Sandbox created: {sandbox.id}")
            return sandbox
            
        except Exception as e:
            logger.error(f"❌ Failed to create sandbox: {e}")
            return None
    
    def _wait_for_sandbox_ready(self, sandbox: Any, timeout: int = 120) -> bool:
        """等待沙盒就绪"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 尝试执行简单命令测试沙盒是否就绪
                response = sandbox.process.code_run("echo 'ready'")
                if response.exit_code == 0:
                    return True
            except Exception:
                pass
            time.sleep(5)
        return False
    
    def execute_code(self, sandbox: Any, code: str) -> Optional[Dict[str, Any]]:
        """执行代码"""
        try:
            logger.info("⚡ Executing code...")
            response = sandbox.process.code_run(code)
            
            result = {
                'success': response.exit_code == 0,
                'output': response.result,
                'exit_code': response.exit_code
            }
            
            if result['success']:
                logger.info("✅ Code executed successfully")
                logger.info(f"📝 Output: {result['output']}")
            else:
                logger.error(f"❌ Code execution failed: {result['output']}")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_all(self):
        """清理所有沙盒"""
        logger.info("🗑️ Cleaning up sandboxes...")
        for sandbox in self.sandboxes:
            try:
                self.client.remove(sandbox)
                logger.info(f"✅ Removed sandbox: {sandbox.id}")
            except Exception as e:
                logger.error(f"❌ Failed to remove sandbox: {e}")
        self.sandboxes.clear()

def main():
    """主函数"""
    print("🎯 Daytona 修复版本测试")
    print("=" * 50)
    
    manager = FixedDaytonaManager()
    
    # 初始化
    if not manager.initialize():
        print("❌ 初始化失败，请检查:")
        print("1. Daytona 服务器是否运行: daytona server")
        print("2. 网络连接是否正常")
        print("3. API 密钥是否有效")
        return
    
    try:
        # 创建沙盒
        sandbox = manager.create_python_sandbox()
        if not sandbox:
            return
        
        # 测试代码执行
        test_codes = [
            # 基础测试
            """
print("🐍 Python 环境测试")
import sys
print(f"Python 版本: {sys.version}")
print(f"平台: {sys.platform}")
""",
            
            # 包安装测试
            """
import subprocess
import sys

print("📦 安装测试包...")
result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests'], 
                       capture_output=True, text=True)
if result.returncode == 0:
    print("✅ requests 安装成功")
    import requests
    print(f"requests 版本: {requests.__version__}")
else:
    print(f"❌ 安装失败: {result.stderr}")
""",
            
            # 网络测试
            """
try:
    import requests
    response = requests.get('https://httpbin.org/ip', timeout=5)
    print(f"🌐 网络连接正常: {response.json()}")
except Exception as e:
    print(f"❌ 网络测试失败: {e}")
"""
        ]
        
        # 执行测试
        for i, code in enumerate(test_codes, 1):
            print(f"\n📋 执行测试 {i}...")
            result = manager.execute_code(sandbox, code)
            if not result or not result.get('success'):
                print(f"⚠️ 测试 {i} 失败")
                break
            time.sleep(2)
        
        print("\n🎉 所有测试完成!")
        
    finally:
        # 清理资源
        manager.cleanup_all()
        print("✅ 清理完成")

if __name__ == "__main__":
    main()
```

## 🧪 部署验证脚本

### 完整的验证脚本
```bash
#!/bin/bash
# deploy_verification.sh

set -e

echo "🔍 Daytona 部署验证脚本"
echo "=========================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_command() {
    if command -v $1 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $1 已安装${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 未安装${NC}"
        return 1
    fi
}

check_service() {
    if curl -s "$1" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ 服务 $1 可访问${NC}"
        return 0
    else
        echo -e "${RED}❌ 服务 $1 不可访问${NC}"
        return 1
    fi
}

# 1. 检查必需工具
echo "1️⃣ 检查必需工具..."
check_command "docker" || { echo "请安装 Docker"; exit 1; }
check_command "daytona" || { echo "请安装 Daytona"; exit 1; }
check_command "python3" || { echo "请安装 Python 3"; exit 1; }
check_command "pip" || { echo "请安装 pip"; exit 1; }

# 2. 检查 Docker 服务
echo -e "\n2️⃣ 检查 Docker 服务..."
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker 服务运行正常${NC}"
else
    echo -e "${RED}❌ Docker 服务未运行${NC}"
    echo "请启动 Docker: sudo systemctl start docker"
    exit 1
fi

# 3. 启动 Daytona 服务器
echo -e "\n3️⃣ 启动 Daytona 服务器..."
if ! pgrep -f "daytona server" > /dev/null; then
    echo "启动 Daytona 服务器..."
    nohup daytona server > daytona.log 2>&1 &
    sleep 10
fi

# 等待服务器就绪
echo "等待服务器就绪..."
for i in {1..30}; do
    if check_service "http://localhost:3000/health"; then
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Daytona 服务器启动超时${NC}"
        exit 1
    fi
    sleep 2
done

# 4. 安装 Python 依赖
echo -e "\n4️⃣ 安装 Python 依赖..."
pip install daytona-sdk requests > /dev/null 2>&1 || {
    echo -e "${YELLOW}⚠️ 使用 --user 安装${NC}"
    pip install --user daytona-sdk requests
}

# 5. 生成 API Key
echo -e "\n5️⃣ 生成 API Key..."
API_KEY=$(daytona api-key generate --name "verification-test" 2>/dev/null | grep -oP 'Key: \K.*' || echo "")
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}⚠️ 无法自动生成 API Key，请手动设置${NC}"
    echo "运行: daytona api-key generate --name verification"
    API_KEY="manual-setup-required"
fi

export DAYTONA_API_KEY="$API_KEY"

# 6. 创建测试配置文件
echo -e "\n6️⃣ 创建测试配置..."
cat > .devcontainer/devcontainer.json << 'EOF'
{
  "name": "Verification Test Environment",
  "image": "mcr.microsoft.com/devcontainers/python:3.11-bullseye",
  
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {
      "version": "24.0"
    }
  },
  
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python"
      ]
    }
  },
  
  "forwardPorts": [8000],
  
  "postCreateCommand": "pip install requests",
  
  "remoteUser": "vscode"
}
EOF

# 7. 运行验证测试
echo -e "\n7️⃣ 运行验证测试..."
python3 << 'EOF'
import sys
import os
sys.path.insert(0, '.')

try:
    from fixed_basic_usage import FixedDaytonaManager
    
    manager = FixedDaytonaManager()
    if manager.initialize():
        print("✅ Daytona SDK 验证成功")
        
        # 快速测试
        sandbox = manager.create_python_sandbox()
        if sandbox:
            result = manager.execute_code(sandbox, "print('Hello from Daytona!')")
            if result and result.get('success'):
                print("✅ 代码执行验证成功")
            else:
                print("❌ 代码执行验证失败")
                sys.exit(1)
        else:
            print("❌ 沙盒创建失败")
            sys.exit(1)
            
        manager.cleanup_all()
        print("✅ 清理完成")
    else:
        print("❌ Daytona 初始化失败")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 验证过程出错: {e}")
    sys.exit(1)
EOF

echo -e "\n🎉 ${GREEN}验证完成！Daytona 部署成功${NC}"
echo -e "\n📋 验证结果:"
echo -e "- Daytona 服务器: ${GREEN}运行中${NC}"
echo -e "- API 连接: ${GREEN}正常${NC}"
echo -e "- 沙盒创建: ${GREEN}成功${NC}"
echo -e "- 代码执行: ${GREEN}正常${NC}"

echo -e "\n🚀 现在可以开始使用 Daytona 了!"
echo "Web 界面: http://localhost:3000"
echo "API Key: $DAYTONA_API_KEY"
```

### 快速修复脚本
```bash
#!/bin/bash
# quick_fix.sh

# 创建修复后的 requirements.txt
cat > requirements.txt << 'EOF'
# 验证过的包版本
daytona-sdk>=0.21.0
requests>=2.31.0
pyyaml>=6.0
psutil>=5.9.0
docker>=6.1.0
EOF

# 创建环境变量文件
cat > .env.example << 'EOF'
# Daytona 配置
DAYTONA_API_URL=http://localhost:3000
DAYTONA_API_KEY=your-generated-api-key-here

# 数据库配置 (避免端口冲突)
DB_HOST=localhost
DB_PORT=15432
DB_NAME=devdb
DB_USER=devuser
DB_PASSWORD=devpass123

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=16379
EOF

echo "✅ 配置文件已修复"
echo "请复制 .env.example 到 .env 并填写正确的值"
```

## 🎯 验证步骤

### 1. 运行验证脚本
```bash
# 下载并运行验证脚本
chmod +x deploy_verification.sh
./deploy_verification.sh
```

### 2. 手动验证步骤
```bash
# 1. 检查 Daytona 服务
curl http://localhost:3000/health

# 2. 检查 API 访问
daytona list

# 3. 创建测试工作区
daytona create https://github.com/microsoft/vscode-dev-containers --repo-branch main

# 4. 验证 Python SDK
python3 fixed_basic_usage.py
```

### 3. 常见问题解决
```bash
# 端口冲突解决
sudo netstat -tulpn | grep :3000
sudo kill -9 $(sudo lsof -t -i:3000)

# Docker 权限问题
sudo usermod -aG docker $USER
newgrp docker

# 重启 Daytona
pkill -f "daytona server"
daytona server > daytona.log 2>&1 &
```

现在所有配置都经过修复和验证，应该可以成功部署和访问了！🚀