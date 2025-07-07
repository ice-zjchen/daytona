#!/bin/bash
# -*- coding: utf-8 -*-
# Daytona 部署验证脚本 v1.0.0
# 作者: AI Assistant
# 功能: 自动检查并修复 Daytona 部署问题

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# 打印横幅
print_banner() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               Daytona 部署验证脚本 v1.0.0                   ║"
    echo "║              自动检查并修复部署问题                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 检查函数
check_command() {
    if command -v "$1" >/dev/null 2>&1; then
        log_success "$1 已安装"
        return 0
    else
        log_error "$1 未安装"
        return 1
    fi
}

check_service() {
    if curl -s "$1" >/dev/null 2>&1; then
        log_success "服务 $1 可访问"
        return 0
    else
        log_error "服务 $1 不可访问"
        return 1
    fi
}

# 检查端口是否被占用
check_port() {
    local port=$1
    if ss -tuln | grep -q ":$port "; then
        log_warning "端口 $port 被占用"
        return 1
    else
        log_success "端口 $port 可用"
        return 0
    fi
}

# 安装缺失的工具
install_missing_tools() {
    log_step "检查并安装缺失工具..."
    
    # 检查包管理器
    if command -v apt-get >/dev/null 2>&1; then
        PKG_MANAGER="apt-get"
        UPDATE_CMD="sudo apt-get update"
        INSTALL_CMD="sudo apt-get install -y"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MANAGER="yum"
        UPDATE_CMD="sudo yum check-update"
        INSTALL_CMD="sudo yum install -y"
    elif command -v brew >/dev/null 2>&1; then
        PKG_MANAGER="brew"
        UPDATE_CMD="brew update"
        INSTALL_CMD="brew install"
    else
        log_error "未找到支持的包管理器"
        return 1
    fi
    
    # 检查必需工具
    tools_needed=()
    
    if ! check_command "curl"; then
        tools_needed+=("curl")
    fi
    
    if ! check_command "jq"; then
        tools_needed+=("jq")
    fi
    
    if ! check_command "docker"; then
        tools_needed+=("docker.io")
    fi
    
    # 安装缺失工具
    if [ ${#tools_needed[@]} -gt 0 ]; then
        log_info "需要安装: ${tools_needed[*]}"
        $UPDATE_CMD
        for tool in "${tools_needed[@]}"; do
            $INSTALL_CMD "$tool"
        done
    else
        log_success "所有必需工具已安装"
    fi
}

# 检查 Docker 状态
check_docker_status() {
    log_step "检查 Docker 状态..."
    
    if ! check_command "docker"; then
        log_error "Docker 未安装"
        return 1
    fi
    
    # 检查 Docker 服务状态
    if ! docker info >/dev/null 2>&1; then
        log_warning "Docker 服务未运行，尝试启动..."
        
        # 尝试启动 Docker
        if command -v systemctl >/dev/null 2>&1; then
            sudo systemctl start docker
            sudo systemctl enable docker
        elif command -v service >/dev/null 2>&1; then
            sudo service docker start
        else
            log_error "无法启动 Docker 服务"
            return 1
        fi
        
        # 等待服务启动
        sleep 5
        
        if docker info >/dev/null 2>&1; then
            log_success "Docker 服务启动成功"
        else
            log_error "Docker 服务启动失败"
            return 1
        fi
    else
        log_success "Docker 服务运行正常"
    fi
    
    # 检查 Docker 权限
    if ! docker ps >/dev/null 2>&1; then
        log_warning "当前用户无 Docker 权限，尝试添加..."
        sudo usermod -aG docker "$USER"
        log_warning "请重新登录或运行 'newgrp docker' 来应用权限变更"
    fi
    
    return 0
}

# 检查 Daytona 安装
check_daytona_installation() {
    log_step "检查 Daytona 安装..."
    
    if ! check_command "daytona"; then
        log_info "Daytona 未安装，开始安装..."
        
        # 下载并安装 Daytona
        case "$(uname -s)" in
            Linux*)
                curl -sfL https://download.daytona.io/daytona/install.sh | sudo bash
                ;;
            Darwin*)
                brew install daytona-io/tap/daytona
                ;;
            *)
                log_error "不支持的操作系统"
                return 1
                ;;
        esac
        
        # 验证安装
        if check_command "daytona"; then
            log_success "Daytona 安装成功"
        else
            log_error "Daytona 安装失败"
            return 1
        fi
    else
        log_success "Daytona 已安装"
    fi
    
    # 显示版本信息
    daytona_version=$(daytona version 2>/dev/null || echo "未知版本")
    log_info "Daytona 版本: $daytona_version"
    
    return 0
}

# 检查并解决端口冲突
check_port_conflicts() {
    log_step "检查端口冲突..."
    
    # 检查常用端口
    ports=(3000 8080 5432 6379)
    conflicts=()
    
    for port in "${ports[@]}"; do
        if ! check_port "$port"; then
            conflicts+=("$port")
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        log_warning "发现端口冲突: ${conflicts[*]}"
        log_info "建议使用非标准端口或停止冲突服务"
        
        # 显示占用端口的进程
        for port in "${conflicts[@]}"; do
            log_info "端口 $port 被以下进程占用:"
            sudo netstat -tulpn | grep ":$port " || true
        done
    else
        log_success "没有端口冲突"
    fi
}

# 启动 Daytona 服务器
start_daytona_server() {
    log_step "启动 Daytona 服务器..."
    
    # 检查服务器是否已经运行
    if check_service "http://localhost:3000/health"; then
        log_success "Daytona 服务器已经运行"
        return 0
    fi
    
    # 启动服务器
    log_info "启动 Daytona 服务器..."
    nohup daytona server > daytona.log 2>&1 &
    
    # 等待服务器启动
    log_info "等待服务器启动..."
    max_attempts=30
    for i in $(seq 1 $max_attempts); do
        if check_service "http://localhost:3000/health"; then
            log_success "Daytona 服务器启动成功"
            return 0
        fi
        
        if [ $((i % 5)) -eq 0 ]; then
            log_info "启动中... ($i/$max_attempts)"
        fi
        
        sleep 2
    done
    
    log_error "Daytona 服务器启动超时"
    log_info "请检查日志文件: daytona.log"
    return 1
}

# 生成 API Key
generate_api_key() {
    log_step "生成 API Key..."
    
    # 检查环境变量
    if [ -n "$DAYTONA_API_KEY" ] && [ "$DAYTONA_API_KEY" != "your-api-key-here" ]; then
        log_success "从环境变量获取 API Key"
        return 0
    fi
    
    # 生成新的 API Key
    log_info "生成新的 API Key..."
    api_key_output=$(daytona api-key generate --name "verification-$(date +%s)" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        # 解析 API Key
        api_key=$(echo "$api_key_output" | grep -oE '[a-zA-Z0-9]{40,}' | head -1)
        
        if [ -n "$api_key" ]; then
            export DAYTONA_API_KEY="$api_key"
            log_success "API Key 生成成功"
            log_info "API Key: ${api_key:0:10}..."
            
            # 保存到文件
            echo "export DAYTONA_API_KEY=\"$api_key\"" > .env
            log_info "API Key 已保存到 .env 文件"
        else
            log_error "无法解析 API Key"
            return 1
        fi
    else
        log_error "API Key 生成失败"
        return 1
    fi
    
    return 0
}

# 安装 Python 依赖
install_python_deps() {
    log_step "安装 Python 依赖..."
    
    # 检查 Python
    if ! check_command "python3"; then
        log_error "Python 3 未安装"
        return 1
    fi
    
    # 检查 pip
    if ! check_command "pip3"; then
        log_error "pip 未安装"
        return 1
    fi
    
    # 创建 requirements.txt
    cat > requirements.txt << 'EOF'
daytona-sdk>=0.21.0
requests>=2.31.0
psutil>=5.9.0
pyyaml>=6.0
EOF
    
    # 安装依赖
    log_info "安装 Python 包..."
    pip3 install -r requirements.txt --user || pip3 install -r requirements.txt
    
    log_success "Python 依赖安装完成"
}

# 创建测试配置文件
create_test_configs() {
    log_step "创建测试配置文件..."
    
    # 创建 .devcontainer 目录
    mkdir -p .devcontainer
    
    # 创建基础 devcontainer.json
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
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
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
  
  "postCreateCommand": "pip install requests pandas numpy",
  
  "remoteUser": "vscode"
}
EOF
    
    # 创建 docker-compose 配置
    cat > .devcontainer/docker-compose.yml << 'EOF'
version: '3.8'
services:
  app:
    build: 
      context: .
      dockerfile: Dockerfile
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
      - "15432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - dev-network
    
  redis:
    image: redis:7-alpine
    ports:
      - "16379:6379"
    volumes:
      - redis_data:/data
    networks:
      - dev-network

volumes:
  postgres_data:
  redis_data:

networks:
  dev-network:
    driver: bridge
EOF
    
    # 创建 Dockerfile
    cat > .devcontainer/Dockerfile << 'EOF'
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# 安装额外工具
RUN apt-get update && apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 包
RUN pip install --upgrade pip
RUN pip install requests pandas numpy matplotlib jupyter

# 设置工作目录
WORKDIR /workspace

# 设置用户
USER vscode
EOF
    
    log_success "测试配置文件创建完成"
}

# 运行验证测试
run_verification_test() {
    log_step "运行验证测试..."
    
    # 检查 Python 脚本是否存在
    if [ ! -f "fixed_basic_usage.py" ]; then
        log_error "验证脚本 fixed_basic_usage.py 不存在"
        return 1
    fi
    
    # 运行验证脚本
    log_info "执行验证脚本..."
    python3 fixed_basic_usage.py
    
    if [ $? -eq 0 ]; then
        log_success "验证测试通过"
        return 0
    else
        log_error "验证测试失败"
        return 1
    fi
}

# 显示最终结果
show_final_results() {
    log_step "显示最终结果..."
    
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                     部署验证完成                             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # 显示服务状态
    echo "📊 服务状态:"
    if check_service "http://localhost:3000/health"; then
        echo -e "  • Daytona 服务器: ${GREEN}运行中${NC}"
    else
        echo -e "  • Daytona 服务器: ${RED}未运行${NC}"
    fi
    
    if docker info >/dev/null 2>&1; then
        echo -e "  • Docker 服务: ${GREEN}运行中${NC}"
    else
        echo -e "  • Docker 服务: ${RED}未运行${NC}"
    fi
    
    # 显示访问信息
    echo ""
    echo "🔗 访问信息:"
    echo "  • Web 界面: http://localhost:3000"
    echo "  • API 地址: http://localhost:3000/api"
    
    if [ -n "$DAYTONA_API_KEY" ]; then
        echo "  • API Key: ${DAYTONA_API_KEY:0:10}..."
    fi
    
    # 显示有用的命令
    echo ""
    echo "💡 有用的命令:"
    echo "  • 查看工作区: daytona list"
    echo "  • 创建工作区: daytona create"
    echo "  • 查看日志: tail -f daytona.log"
    echo "  • 重启服务: pkill -f 'daytona server' && daytona server"
    
    echo ""
    echo "📚 文档链接:"
    echo "  • 官方文档: https://docs.daytona.io/"
    echo "  • 源代码: https://github.com/daytonaio/daytona"
    echo "  • 社区: https://discord.gg/daytona"
}

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 这里可以添加清理逻辑
}

# 主函数
main() {
    # 设置清理陷阱
    trap cleanup EXIT
    
    print_banner
    
    # 检查系统信息
    log_info "系统信息:"
    echo "  • 操作系统: $(uname -s)"
    echo "  • 架构: $(uname -m)"
    echo "  • 内核版本: $(uname -r)"
    echo "  • 用户: $(whoami)"
    echo ""
    
    # 执行验证步骤
    local steps=(
        "install_missing_tools"
        "check_docker_status"
        "check_daytona_installation"
        "check_port_conflicts"
        "start_daytona_server"
        "generate_api_key"
        "install_python_deps"
        "create_test_configs"
        "run_verification_test"
    )
    
    local failed_steps=()
    
    for step in "${steps[@]}"; do
        if ! $step; then
            failed_steps+=("$step")
        fi
        echo ""
    done
    
    # 显示结果
    show_final_results
    
    # 检查是否有失败的步骤
    if [ ${#failed_steps[@]} -gt 0 ]; then
        echo ""
        log_error "以下步骤失败:"
        for step in "${failed_steps[@]}"; do
            echo "  • $step"
        done
        echo ""
        log_info "故障排除建议:"
        echo "  1. 检查网络连接"
        echo "  2. 确认有 sudo 权限"
        echo "  3. 检查防火墙设置"
        echo "  4. 查看日志文件"
        echo "  5. 重新运行脚本"
        
        exit 1
    else
        echo ""
        log_success "🎉 所有验证步骤都成功完成！"
        log_success "Daytona 已成功部署并可以使用"
        exit 0
    fi
}

# 运行主函数
main "$@"