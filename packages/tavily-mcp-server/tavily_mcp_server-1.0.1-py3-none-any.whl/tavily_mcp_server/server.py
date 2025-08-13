import json
import logging
import os
import sys
from functools import lru_cache
from typing import Annotated, Dict, List, Literal, Optional, Union

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator
from tavily import InvalidAPIKeyError, TavilyClient, UsageLimitExceededError

VERSION = "1.0.0"

# API密钥验证
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 初始化FastMCP和FastAPI
mcp = FastMCP(
    name="Tavily Search 🚀",
    version=VERSION
)
app = FastAPI(
    title="Tavily MCP API",
    description="Tavily搜索MCP服务API - 为AI智能体提供强大的网络搜索能力",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "MCP Team",
        "email": "support@mcp.dev",
        "url": "https://github.com/mcp-team/tavily-mcp-server"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 缓存客户端实例
@lru_cache()
def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is required")
    return TavilyClient(api_key=api_key)

# API密钥验证依赖
async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not api_key or api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": VERSION}

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )

class SearchBase(BaseModel):
    """Base parameters for Tavily search."""
    query: Annotated[str, Field(description="Search query")]
    max_results: Annotated[
        int,
        Field(
            default=5,
            description="Maximum number of results to return",
            gt=0,
            lt=20,
        ),
    ]
    include_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically include in the search results",
        ),
    ]
    exclude_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically exclude from the search results",
        ),
    ]
    days: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of days back to search (default is 3)",
            gt=0,
            le=365,
        ),
    ]
    country: Annotated[
        str | None,
        Field(
            default=None,
            description="Country to search in (e.g. 'US', 'UK', 'AU')",
        ),
    ]
    time_range : Annotated[
        str | None,
        Field(
            default=None,
            description="Time range to search in (e.g. 'month', 'year')",
        ),
    ]

    @field_validator('include_domains', 'exclude_domains', mode='before')
    @classmethod
    def parse_domains_list(cls, v):
        """Parse domain lists from various input formats."""
        if v is None:
            return []
        if isinstance(v, list):
            return [domain.strip() for domain in v if domain.strip()]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [domain.strip() for domain in parsed if domain.strip()]
                return [parsed.strip()]
            except json.JSONDecodeError:
                if ',' in v:
                    return [domain.strip() for domain in v.split(',') if domain.strip()]
                return [v]
        return []

class GeneralSearch(SearchBase):
    """Parameters for general web search."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="basic",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]

class AnswerSearch(SearchBase):
    """Parameters for search with answer."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="advanced",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]

class NewsSearch(SearchBase):
    """Parameters for news search."""
    days: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of days back to search (default is 3)",
            gt=0,
            le=365,
        ),
    ]

class SearchResponse(BaseModel):
    """标准化的搜索响应格式"""
    query: str
    answer: Optional[str] = None
    results: List[Dict[str, str]] = Field(default_factory=list)
    included_domains: List[str] = Field(default_factory=list)
    excluded_domains: List[str] = Field(default_factory=list)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "人工智能的最新发展",
                "answer": "人工智能领域最近取得了重大突破，包括大型语言模型和多模态AI系统的发展。",
                "results": [
                    {"title": "AI研究进展", "url": "https://example.com/ai-research", "content": "关于AI最新研究的详细内容..."},
                    {"title": "机器学习新方法", "url": "https://example.com/ml-methods", "content": "机器学习领域的创新方法..."}
                ],
                "included_domains": ["research.org", "science.edu"],
                "excluded_domains": ["spam.com"]
            }
        }

def format_results(response: dict, format_type: str = "text") -> dict:
    """格式化Tavily搜索结果
    
    Args:
        response: Tavily API响应
        format_type: 输出格式类型 (text, json, markdown)
        
    Returns:
        dict: 包含格式化文本和原始数据的字典
    """
    logger.debug(f"Formatting Tavily Search Results with format: {format_type}")
    
    # 创建标准化响应对象
    search_response = SearchResponse(
        query=response.get("query", ""),
        answer=response.get("answer"),
        results=response.get("results", []),
        included_domains=response.get("included_domains", []),
        excluded_domains=response.get("excluded_domains", [])
    )
    
    # 如果请求JSON格式，直接返回模型数据
    if format_type == "json":
        return {"text": "", "data": search_response.model_dump()}
    
    # 构建格式化输出
    output = []
    
    # 添加过滤器信息
    if search_response.included_domains or search_response.excluded_domains:
        filters = []
        if search_response.included_domains:
            filters.append(f"Including domains: {', '.join(search_response.included_domains)}")
        if search_response.excluded_domains:
            filters.append(f"Excluding domains: {', '.join(search_response.excluded_domains)}")
        output.append("Search Filters:")
        output.extend(filters)
        output.append("")

    # 添加答案和来源信息
    if search_response.answer:
        if format_type == "markdown":
            output.append(f"### Answer\n{search_response.answer}")
            output.append("\n### Sources")
        else:
            output.append(f"Answer: {search_response.answer}")
            output.append("\nSources:")
        
        # 添加来源列表
        output.extend([f"- {result['title']}: {result['url']}" for result in search_response.results])
        output.append("")

    # 添加详细结果标题
    output.append("### Detailed Results" if format_type == "markdown" else "Detailed Results:")
    
    # 添加每个结果的详细信息
    for result in search_response.results:
        output.append(f"\nTitle: {result['title']}")
        output.append(f"URL: {result['url']}")
        if result.get("published_date"):
            output.append(f"Published: {result['published_date']}")
        if result.get("content") and format_type == "markdown":
            output.append(f"\nContent Preview: {result['content'][:200]}..." if len(result.get('content', '')) > 200 else f"\nContent: {result['content']}")

    # 返回格式化文本和原始数据
    return {"text": "\n".join(output), "data": search_response.model_dump()}

class SearchResult(BaseModel):
    """搜索结果响应模型"""
    text: str
    data: dict

@mcp.tool(
    name="tavily_web_search",
    description="Execute comprehensive web search using Tavily AI search engine. Perfect for finding current information, research, and general web content across multiple sources."
)
async def tavily_web_search(
    query: Annotated[str, Field(description="The search query to execute. Be specific for better results.")],
    max_results: Annotated[int, Field(default=5, description="Maximum number of search results to return (1-20)", ge=1, le=20)] = 5,
    search_depth: Annotated[Literal["basic", "advanced"], Field(default="basic", description="Search depth: 'basic' for quick results, 'advanced' for comprehensive analysis")] = "basic",
    include_domains: Annotated[list[str] | None, Field(default=None, description="List of specific domains to include (e.g., ['wikipedia.org', 'github.com'])")] = None,
    exclude_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to exclude from results")] = None,
    format_type: Annotated[Literal["text", "json", "markdown"], Field(default="text", description="Output format: 'text' for readable format, 'json' for structured data, 'markdown' for formatted text")] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """Execute comprehensive web search using Tavily AI search engine
    
    This tool provides powerful web search capabilities with advanced filtering options.
    Use this for general research, finding current information, and exploring web content.
    
    Examples:
    - tavily_web_search("latest AI developments 2024")
    - tavily_web_search("Python FastAPI tutorial", include_domains=["docs.python.org"])
    - tavily_web_search("climate change research", search_depth="advanced", max_results=10)
    """
    logger.info(f"Tavily Web Search: {query}")
    
    try:
        args = GeneralSearch(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        client = get_tavily_client()
        response = await client.search(
            query=args.query,
            max_results=args.max_results,
            search_depth=args.search_depth,
            include_domains=args.include_domains or [],
            exclude_domains=args.exclude_domains or []
        )
        
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        response["query"] = query
        
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@mcp.tool(
    name="tavily_answer_search",
    description="Execute AI-powered search with direct answer generation. Best for questions that need specific, synthesized answers from multiple sources."
)
async def tavily_answer_search(
    query: Annotated[str, Field(description="The question or query to get a direct answer for. Frame as a specific question for best results.")],
    max_results: Annotated[int, Field(default=5, description="Maximum number of sources to analyze for the answer (1-20)", ge=1, le=20)] = 5,
    search_depth: Annotated[Literal["basic", "advanced"], Field(default="advanced", description="Search depth: 'advanced' recommended for better answer quality")] = "advanced",
    include_domains: Annotated[list[str] | None, Field(default=None, description="List of trusted domains to prioritize for answers")] = None,
    exclude_domains: Annotated[list[str] | None, Field(default=None, description="List of domains to exclude from answer generation")] = None,
    format_type: Annotated[Literal["text", "json", "markdown"], Field(default="text", description="Output format for the answer and sources")] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """Execute AI-powered search with direct answer generation
    
    This tool searches the web and generates a synthesized answer from multiple sources.
    Perfect for getting direct answers to specific questions with source citations.
    
    Examples:
    - tavily_answer_search("What are the benefits of using FastAPI over Flask?")
    - tavily_answer_search("How does machine learning work?", search_depth="advanced")
    - tavily_answer_search("Best practices for API security", include_domains=["owasp.org"])
    """
    logger.info(f"Tavily Answer Search: {query}")
    
    try:
        args = AnswerSearch(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        client = get_tavily_client()
        response = await client.search(
            query=args.query,
            max_results=args.max_results,
            search_depth=args.search_depth,
            include_answer=True,
            include_domains=args.include_domains or [],
            exclude_domains=args.exclude_domains or []
        )
        
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        response["query"] = query
        
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@mcp.tool(
    name="tavily_news_search",
    description="Search for recent news articles and current events. Specialized for finding the latest news, breaking stories, and recent developments."
)
async def tavily_news_search(
    query: Annotated[str, Field(description="News search query. Include keywords related to current events, people, or topics in the news.")],
    max_results: Annotated[int, Field(default=5, description="Maximum number of news articles to return (1-20)", ge=1, le=20)] = 5,
    days: Annotated[int | None, Field(default=None, description="Number of days back to search for news (1-365). Default is 3 days for recent news.", ge=1, le=365)] = None,
    include_domains: Annotated[list[str] | None, Field(default=None, description="List of news sources to prioritize (e.g., ['bbc.com', 'reuters.com'])")] = None,
    exclude_domains: Annotated[list[str] | None, Field(default=None, description="List of news sources to exclude")] = None,
    format_type: Annotated[Literal["text", "json", "markdown"], Field(default="text", description="Output format for news results")] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """Search for recent news articles and current events
    
    This tool specializes in finding recent news, breaking stories, and current developments.
    Results are filtered to show only news content from reliable sources.
    
    Examples:
    - tavily_news_search("artificial intelligence regulation")
    - tavily_news_search("climate summit 2024", days=7)
    - tavily_news_search("tech industry layoffs", include_domains=["techcrunch.com", "wired.com"])
    """
    logger.info(f"Tavily News Search: {query}")
    
    try:
        args = NewsSearch(
            query=query,
            max_results=max_results,
            days=days,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        
        client = get_tavily_client()
        response = await client.search(
            query=args.query,
            max_results=args.max_results,
            topic="news",
            days=args.days if args.days is not None else 3,
            include_domains=args.include_domains or [],
            exclude_domains=args.exclude_domains or []
        )
        
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        response["query"] = query
        
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

def main(host: str = "0.0.0.0", port: int = 8083, log_level: str = "info", reload: bool = False):
    """启动Tavily MCP服务器
    
    Args:
        host: 服务器主机地址
        port: 服务器端口
        log_level: 日志级别
        reload: 是否启用热重载
    """
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
    
    try:
        # 加载环境变量
        load_dotenv()
        
        # 验证必要的环境变量
        required_env_vars = ["TAVILY_API_KEY", "MCP_API_KEY"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            logger.info("Please create a .env file with the required variables or set them in your environment.")
            logger.info("Example .env file:\n\nTAVILY_API_KEY=your_tavily_api_key\nMCP_API_KEY=your_mcp_api_key")
            sys.exit(1)
        
        # 配置FastAPI应用
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 启动服务器
        logger.info(f"Starting Tavily MCP server on {host}:{port}...")
        logger.info(f"API documentation available at http://{host if host != '0.0.0.0' else 'localhost'}:{port}/docs")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            reload=reload
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()