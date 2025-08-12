#!/usr/bin/env python

"""
命令行工具，用于检查环境变量和依赖项是否正确设置。
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

from your_mcp_server import __version__

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """检查环境变量是否正确设置"""
    load_dotenv()
    
    # 检查API密钥
    api_key = os.getenv("API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key and not tavily_api_key:
        logger.warning("⚠️ 未设置API_KEY或TAVILY_API_KEY环境变量")
        logger.info("请设置以下环境变量之一：")
        logger.info("  - API_KEY: 通用API密钥")
        logger.info("  - TAVILY_API_KEY: Tavily API密钥")
        return False
    
    if api_key:
        logger.info("✅ API_KEY已设置")
    
    if tavily_api_key:
        logger.info("✅ TAVILY_API_KEY已设置")
    
    # 检查端口
    port = os.getenv("PORT")
    if not port:
        logger.info("⚠️ 未设置PORT环境变量，将使用默认端口")
    else:
        logger.info(f"✅ PORT已设置为{port}")
    
    return True

def check_dependencies():
    """检查依赖项是否已安装"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        
        logger.info("✅ 所有基本依赖项已安装")
        
        try:
            import fastmcp
            logger.info("✅ FastMCP已安装")
        except ImportError:
            logger.warning("⚠️ FastMCP未安装，某些功能可能不可用")
        
        try:
            import tavily
            logger.info("✅ Tavily已安装")
        except ImportError:
            logger.warning("⚠️ Tavily未安装，Tavily搜索功能将不可用")
            
        return True
    except ImportError as e:
        logger.error(f"❌ 缺少依赖项: {e}")
        logger.info("请运行: pip install -e .")
        return False

def main():
    """主入口点"""
    parser = argparse.ArgumentParser(description="your-mcp-server命令行工具")
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"your-mcp-server {__version__}"
    )
    parser.add_argument(
        "--check", 
        action="store_true",
        help="检查环境变量和依赖项"
    )
    
    args = parser.parse_args()
    
    if args.check:
        logger.info("检查环境变量...")
        env_ok = check_environment()
        
        logger.info("\n检查依赖项...")
        deps_ok = check_dependencies()
        
        if env_ok and deps_ok:
            logger.info("\n✅ 所有检查通过！你可以运行以下命令启动服务器:")
            logger.info("  your-mcp-server")
            logger.info("  tavily-mcp-server")
            return 0
        else:
            logger.error("\n❌ 检查未通过，请解决上述问题")
            return 1
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())