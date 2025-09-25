#!/bin/bash

echo "🚀 MCP服务器安装脚本"
echo "===================="

# 添加uv到PATH
export PATH="$HOME/.local/bin:$PATH"

# 安装Qdrant向量数据库（用于code-search）
echo "📦 安装Qdrant向量数据库..."
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker未安装，跳过Qdrant安装"
    echo "建议安装Docker后运行: docker run -p 6333:6333 qdrant/qdrant"
else
    echo "启动Qdrant容器..."
    docker run -d --name qdrant -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant 2>/dev/null || echo "Qdrant已在运行"
fi

# 测试MCP服务器
echo ""
echo "🧪 测试MCP服务器..."
echo "===================="

# 测试sequential-thinking
echo "1. 测试sequential-thinking..."
timeout 5 npx -y @modelcontextprotocol/server-sequential-thinking <<< '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null && echo "✅ sequential-thinking可用" || echo "❌ sequential-thinking不可用"

# 测试memory
echo "2. 测试memory服务器..."
timeout 5 npx -y @modelcontextprotocol/server-memory <<< '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null && echo "✅ memory可用" || echo "❌ memory不可用"

# 测试filesystem
echo "3. 测试filesystem服务器..."
timeout 5 npx -y @modelcontextprotocol/server-filesystem /tmp <<< '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null && echo "✅ filesystem可用" || echo "❌ filesystem不可用"

# 测试duckduckgo
echo "4. 测试duckduckgo-search..."
timeout 5 uvx duckduckgo-mcp-server <<< '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null && echo "✅ duckduckgo-search可用" || echo "❌ duckduckgo-search不可用"

# 测试fetch
echo "5. 测试fetch服务器..."
timeout 5 uvx mcp-server-fetch <<< '{"jsonrpc":"2.0","method":"tools/list","id":1}' 2>/dev/null && echo "✅ fetch可用" || echo "❌ fetch不可用"

echo ""
echo "📋 配置文件位置："
echo "  - MCP配置: $(pwd)/mcp-config.json"
echo ""
echo "🔧 环境变量设置："
echo "  将以下内容添加到 ~/.bashrc 或 ~/.zshrc："
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "💡 使用方法："
echo "  1. 将mcp-config.json复制到Claude Desktop配置目录"
echo "  2. Windows: %APPDATA%/Claude/claude_desktop_config.json"
echo "  3. macOS: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo "  4. Linux: ~/.config/Claude/claude_desktop_config.json"