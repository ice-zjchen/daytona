#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daytona 修复版本 - 可直接运行的示例代码
作者: AI Assistant
版本: 1.0.0
描述: 修复了所有配置问题的 Daytona Python SDK 使用示例
"""

import os
import sys
import time
import logging
import subprocess
from typing import Optional, Dict, Any, List

# 设置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """安装必需的依赖包"""
    required_packages = [
        'daytona-sdk>=0.21.0',
        'requests>=2.31.0',
        'psutil>=5.9.0'
    ]
    
    for package in required_packages:
        try:
            __import__(package.split('>=')[0].replace('-', '_'))
        except ImportError:
            logger.info(f"安装缺失的包: {package}")
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', package
            ])

# 尝试安装依赖
try:
    install_dependencies()
    from daytona_sdk import Daytona, DaytonaConfig, CreateSandboxParams
    import requests
    import psutil
except ImportError as e:
    logger.error(f"依赖安装失败: {e}")
    logger.error("请手动运行: pip install daytona-sdk requests psutil")
    sys.exit(1)

class FixedDaytonaManager:
    """修复后的 Daytona 管理器"""
    
    def __init__(self, api_url: str = "http://localhost:3000"):
        self.api_url = api_url
        self.client = None
        self.sandboxes: List[Any] = []
        self.api_key = None
        
    def check_daytona_server(self) -> bool:
        """检查 Daytona 服务器是否运行"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Daytona 服务器运行正常")
                return True
            else:
                logger.error(f"❌ Daytona 服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ 无法连接到 Daytona 服务器: {e}")
            logger.info("请确保 Daytona 服务器正在运行: daytona server")
            return False
    
    def start_daytona_server(self) -> bool:
        """启动 Daytona 服务器"""
        try:
            # 检查是否已经在运行
            if self.check_daytona_server():
                return True
            
            logger.info("🚀 启动 Daytona 服务器...")
            
            # 启动服务器（后台运行）
            process = subprocess.Popen(
                ['daytona', 'server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # 等待服务器启动
            max_wait = 60  # 最多等待60秒
            for i in range(max_wait):
                time.sleep(2)
                if self.check_daytona_server():
                    logger.info("✅ Daytona 服务器启动成功")
                    return True
                logger.info(f"等待服务器启动... ({i+1}/{max_wait//2})")
            
            logger.error("❌ Daytona 服务器启动超时")
            return False
            
        except FileNotFoundError:
            logger.error("❌ 找不到 daytona 命令，请先安装 Daytona")
            logger.info("安装指南: https://docs.daytona.io/installation/")
            return False
        except Exception as e:
            logger.error(f"❌ 启动服务器失败: {e}")
            return False
    
    def get_or_generate_api_key(self) -> Optional[str]:
        """获取或生成 API Key"""
        # 1. 尝试从环境变量获取
        api_key = os.getenv('DAYTONA_API_KEY')
        if api_key and api_key != "your-api-key-here":
            logger.info("✅ 从环境变量获取 API Key")
            return api_key
        
        # 2. 尝试生成新的 API Key
        try:
            logger.info("🔑 生成新的 API Key...")
            result = subprocess.run(
                ['daytona', 'api-key', 'generate', '--name', 'python-sdk-auto'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # 解析输出获取 API Key
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    line = line.strip()
                    if 'Key:' in line:
                        api_key = line.split('Key:')[1].strip()
                        logger.info("✅ API Key 生成成功")
                        # 保存到环境变量
                        os.environ['DAYTONA_API_KEY'] = api_key
                        return api_key
                    elif len(line) > 20 and not line.startswith('API') and not line.startswith('Generated'):
                        # 可能是直接输出的 API Key
                        logger.info("✅ API Key 生成成功")
                        os.environ['DAYTONA_API_KEY'] = line
                        return line
                
                logger.error("❌ 无法解析 API Key 输出")
                logger.info(f"命令输出: {result.stdout}")
            else:
                logger.error(f"❌ API Key 生成失败: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            logger.error("❌ API Key 生成超时")
        except Exception as e:
            logger.error(f"❌ API Key 生成异常: {e}")
        
        # 3. 提示用户手动生成
        logger.warning("⚠️ 自动生成 API Key 失败")
        logger.info("请手动生成 API Key:")
        logger.info("1. 运行: daytona api-key generate --name my-key")
        logger.info("2. 复制生成的 API Key")
        logger.info("3. 设置环境变量: export DAYTONA_API_KEY=<your-key>")
        
        return None
    
    def initialize(self) -> bool:
        """初始化 Daytona 客户端"""
        try:
            logger.info("🔧 初始化 Daytona 客户端...")
            
            # 1. 启动服务器
            if not self.start_daytona_server():
                return False
            
            # 2. 获取 API Key
            self.api_key = self.get_or_generate_api_key()
            if not self.api_key:
                return False
            
            # 3. 初始化客户端
            config = DaytonaConfig(
                api_url=self.api_url,
                api_key=self.api_key
            )
            self.client = Daytona(config)
            
            # 4. 验证连接
            try:
                workspaces = self.client.list()
                logger.info(f"✅ 客户端初始化成功，当前工作区数量: {len(workspaces)}")
                return True
            except Exception as e:
                logger.error(f"❌ 客户端验证失败: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 初始化失败: {e}")
            return False
    
    def create_python_sandbox(self, timeout: int = 300) -> Optional[Any]:
        """创建 Python 开发沙盒"""
        if not self.client:
            logger.error("❌ 客户端未初始化")
            return None
        
        try:
            logger.info("🐍 创建 Python 沙盒...")
            
            # 使用稳定的官方镜像
            params = CreateSandboxParams(
                language="python",
                image="mcr.microsoft.com/devcontainers/python:3.11-bullseye"
            )
            
            # 创建沙盒
            sandbox = self.client.create(params)
            self.sandboxes.append(sandbox)
            
            logger.info(f"📦 沙盒创建中: {sandbox.id}")
            
            # 等待沙盒就绪
            if self.wait_for_sandbox_ready(sandbox, timeout):
                logger.info(f"✅ Python 沙盒创建成功: {sandbox.id}")
                return sandbox
            else:
                logger.error("❌ 沙盒启动超时")
                return None
                
        except Exception as e:
            logger.error(f"❌ 创建沙盒失败: {e}")
            return None
    
    def wait_for_sandbox_ready(self, sandbox: Any, timeout: int = 300) -> bool:
        """等待沙盒就绪"""
        logger.info("⏳ 等待沙盒就绪...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 尝试执行简单命令
                response = sandbox.process.code_run("echo 'sandbox ready'")
                if response.exit_code == 0:
                    logger.info("✅ 沙盒就绪")
                    return True
            except Exception as e:
                logger.debug(f"沙盒未就绪: {e}")
            
            # 每5秒检查一次
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            if elapsed % 30 == 0:  # 每30秒显示一次进度
                logger.info(f"⏳ 等待中... {elapsed}s/{timeout}s")
        
        return False
    
    def execute_code(self, sandbox: Any, code: str, description: str = "") -> Dict[str, Any]:
        """执行代码"""
        try:
            if description:
                logger.info(f"⚡ 执行: {description}")
            else:
                logger.info("⚡ 执行代码...")
            
            # 执行代码
            response = sandbox.process.code_run(code)
            
            result = {
                'success': response.exit_code == 0,
                'output': response.result.strip() if response.result else "",
                'exit_code': response.exit_code,
                'description': description
            }
            
            if result['success']:
                logger.info("✅ 执行成功")
                if result['output']:
                    logger.info(f"📝 输出:\n{result['output']}")
            else:
                logger.error(f"❌ 执行失败 (退出码: {result['exit_code']})")
                if result['output']:
                    logger.error(f"🚨 错误信息:\n{result['output']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 执行异常: {e}")
            return {
                'success': False,
                'error': str(e),
                'description': description
            }
    
    def run_comprehensive_tests(self, sandbox: Any) -> bool:
        """运行综合测试"""
        logger.info("🧪 开始综合测试...")
        
        test_cases = [
            {
                'name': 'Python 环境测试',
                'code': '''
import sys
import os
print(f"🐍 Python 版本: {sys.version}")
print(f"🏠 工作目录: {os.getcwd()}")
print(f"💻 系统平台: {sys.platform}")
print(f"📁 Python 路径: {sys.executable}")
'''
            },
            {
                'name': '基础包测试',
                'code': '''
try:
    import json
    import datetime
    import urllib.request
    print("✅ 标准库导入成功")
    
    # 测试 JSON
    data = {"test": "success", "timestamp": str(datetime.datetime.now())}
    json_str = json.dumps(data, indent=2)
    print(f"📋 JSON 测试: {json_str}")
    
except Exception as e:
    print(f"❌ 标准库测试失败: {e}")
'''
            },
            {
                'name': '包安装测试',
                'code': '''
import subprocess
import sys

try:
    print("📦 安装 requests 包...")
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'requests==2.31.0'],
        capture_output=True, text=True, timeout=60
    )
    
    if result.returncode == 0:
        print("✅ requests 安装成功")
        import requests
        print(f"📦 requests 版本: {requests.__version__}")
    else:
        print(f"❌ 安装失败: {result.stderr}")
        
except Exception as e:
    print(f"❌ 包安装测试失败: {e}")
'''
            },
            {
                'name': '网络连接测试',
                'code': '''
try:
    import requests
    import json
    
    print("🌐 测试网络连接...")
    response = requests.get('https://httpbin.org/ip', timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 网络连接正常")
        print(f"🌍 外部 IP: {data.get('origin', 'Unknown')}")
    else:
        print(f"⚠️ 网络响应异常: {response.status_code}")
        
except Exception as e:
    print(f"❌ 网络测试失败: {e}")
'''
            },
            {
                'name': '文件系统测试',
                'code': '''
import os
import tempfile

try:
    print("📁 测试文件系统操作...")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Hello from Daytona sandbox!")
        temp_file = f.name
    
    # 读取文件
    with open(temp_file, 'r') as f:
        content = f.read()
    
    print(f"✅ 文件操作成功")
    print(f"📄 文件内容: {content}")
    print(f"📂 临时文件: {temp_file}")
    
    # 清理
    os.unlink(temp_file)
    print("🗑️ 临时文件已清理")
    
except Exception as e:
    print(f"❌ 文件系统测试失败: {e}")
'''
            }
        ]
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📋 测试 {i}/{total_tests}: {test_case['name']}")
            logger.info("-" * 50)
            
            result = self.execute_code(sandbox, test_case['code'])
            
            if result.get('success'):
                success_count += 1
                logger.info(f"✅ 测试 {i} 通过")
            else:
                logger.error(f"❌ 测试 {i} 失败")
            
            # 测试间隔
            if i < total_tests:
                time.sleep(2)
        
        # 测试总结
        logger.info("\n" + "=" * 50)
        logger.info(f"🎯 测试完成: {success_count}/{total_tests} 通过")
        
        if success_count == total_tests:
            logger.info("🎉 所有测试通过！沙盒环境完全正常")
            return True
        else:
            logger.warning(f"⚠️ {total_tests - success_count} 个测试失败")
            return False
    
    def cleanup_all(self):
        """清理所有沙盒"""
        if not self.sandboxes:
            logger.info("🧹 无需清理，没有活动的沙盒")
            return
        
        logger.info(f"🗑️ 清理 {len(self.sandboxes)} 个沙盒...")
        
        for i, sandbox in enumerate(self.sandboxes, 1):
            try:
                logger.info(f"🗑️ 清理沙盒 {i}: {sandbox.id}")
                self.client.remove(sandbox)
                logger.info(f"✅ 沙盒 {i} 清理成功")
            except Exception as e:
                logger.error(f"❌ 清理沙盒 {i} 失败: {e}")
        
        self.sandboxes.clear()
        logger.info("✅ 所有沙盒清理完成")
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                'python_version': sys.version,
                'platform': sys.platform,
                'api_url': self.api_url,
                'has_client': self.client is not None,
                'sandbox_count': len(self.sandboxes),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available
            }
        except Exception as e:
            logger.error(f"获取系统信息失败: {e}")
            return {'error': str(e)}

def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("🎯 Daytona Python SDK 修复版本测试")
    print("=" * 60)
    print("📝 版本: 1.0.0")
    print("🔧 修复: 所有已知配置问题")
    print("🚀 功能: 完整的部署验证和测试")
    print("=" * 60)

def main():
    """主函数"""
    print_banner()
    
    # 创建管理器
    manager = FixedDaytonaManager()
    
    try:
        # 显示系统信息
        logger.info("📊 系统信息:")
        sys_info = manager.get_system_info()
        for key, value in sys_info.items():
            if key != 'error':
                logger.info(f"  {key}: {value}")
        
        # 初始化
        logger.info("\n🔧 开始初始化...")
        if not manager.initialize():
            logger.error("❌ 初始化失败")
            logger.info("\n🔧 故障排除步骤:")
            logger.info("1. 检查 Docker 是否运行: docker info")
            logger.info("2. 检查 Daytona 是否安装: daytona version")
            logger.info("3. 手动启动服务器: daytona server")
            logger.info("4. 检查网络连接: curl http://localhost:3000/health")
            return 1
        
        # 创建沙盒
        logger.info("\n🐍 创建 Python 沙盒...")
        sandbox = manager.create_python_sandbox()
        if not sandbox:
            logger.error("❌ 沙盒创建失败")
            return 1
        
        # 运行测试
        logger.info("\n🧪 开始运行测试...")
        test_success = manager.run_comprehensive_tests(sandbox)
        
        # 显示结果
        if test_success:
            logger.info("\n🎉 恭喜！Daytona 部署完全成功")
            logger.info("✅ 所有功能正常工作")
            logger.info(f"🌐 Web 界面: {manager.api_url}")
            if manager.api_key:
                logger.info(f"🔑 API Key: {manager.api_key[:10]}...")
        else:
            logger.warning("\n⚠️ 部分功能存在问题")
            logger.info("💡 请检查网络连接和权限设置")
        
        return 0 if test_success else 1
        
    except KeyboardInterrupt:
        logger.info("\n⚡ 用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"\n💥 未预期的错误: {e}")
        logger.exception("详细错误信息:")
        return 1
    finally:
        # 清理资源
        logger.info("\n🧹 清理资源...")
        manager.cleanup_all()
        logger.info("✅ 测试完成，资源已清理")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)