import os
import asyncio
import argparse
import json
import sys
from typing import List, Dict, Any, TypedDict, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# LangGraph 和 LangChain 相关导入
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import logging

# 强制设置控制台编码
if sys.platform.startswith('win'):
    try:
        import locale
        locale.setlocale(locale.LC_ALL, 'C')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except:
        pass

# 配置日志 - 完全使用ASCII字符
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# 初始化MCP服务
mcp = FastMCP("DeepResearch")
USER_AGENT = "deepresearch-app/1.0"

# 全局变量
current_llm = None

def load_environment():
    """加载环境变量"""
    env_loaded = False
    env_paths = ["./.env", "../.env", ".env"]
    
    for env_path in env_paths:
        if os.path.exists(env_path):
            load_dotenv(env_path)
            env_loaded = True
            logger.info(f"Environment file loaded: {env_path}")
            break
    
    if not env_loaded:
        logger.warning("Warning: No .env file found")
    
    return env_loaded

def create_llm_instance(api_key: str) -> ChatOpenAI:
    """根据提供的API key创建LLM实例"""
    global current_llm
    current_llm = ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=4000,
        request_timeout=30
    )
    logger.info("LLM instance created successfully")
    return current_llm

def get_current_llm() -> ChatOpenAI:
    """获取当前LLM实例，如果没有则抛出异常"""
    if current_llm is None:
        raise ValueError("LLM instance not initialized, please call create_llm_instance() first")
    return current_llm

# 数据模型定义
class WebSearchItem(BaseModel):
    reason: str = Field(description="为什么这个搜索对查询很重要的原因")
    query: str = Field(description="用于网络搜索的搜索词")

class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem] = Field(description="执行的网络搜索列表")

class ReportData(BaseModel):
    short_summary: str = Field(description="研究结果的简短2-3句摘要")
    markdown_report: str = Field(description="最终报告")
    follow_up_questions: List[str] = Field(description="建议进一步研究的主题")

# 状态定义
class ResearchState(TypedDict):
    query: str
    search_plan: Optional[WebSearchPlan]
    search_results: List[str]
    final_report: Optional[ReportData]
    messages: List[BaseMessage]

# 工具定义
@tool
def web_search_tool(query: str) -> str:
    """执行网络搜索并返回结果"""
    search = DuckDuckGoSearchRun()
    try:
        result = search.run(query)
        return result
    except Exception as e:
        error_msg = f"Search failed: {str(e)}"
        logger.error(error_msg)
        return error_msg

def extract_json_from_response(content: str) -> dict:
    """从响应中提取JSON内容的辅助函数"""
    try:
        # 如果响应包含 ```json 代码块，提取其中的内容
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
        elif "{" in content and "}" in content:
            # 提取第一个完整的JSON对象
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
        else:
            raise ValueError("No JSON format data found")
        
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON parsing failed: {e}")
        raise

async def planning_node(state: ResearchState) -> Dict[str, Any]:
    """规划节点 - 生成搜索计划"""
    query = state["query"]
    logger.info(f"Planning search for query: {query}")
    
    system_prompt = """你是一个专业的研究助理。给定一个查询，制定一套网络搜索计划来最好地回答查询。
    请生成6-8个搜索项，每个搜索项包含搜索原因和查询词。
    搜索词应该多样化，涵盖不同角度和方面。
    请严格按照以下JSON格式返回：

    ```json
    {
        "searches": [
            {
                "reason": "搜索原因",
                "query": "搜索查询词"
            }
        ]
    }
    ```"""
    
    try:
        llm = get_current_llm()
        prompt = f"{system_prompt}\n\n请为以下查询制定搜索计划：{query}"
        
        response = await llm.ainvoke(prompt)
        content = response.content
        logger.info(f"Planning agent response length: {len(content)} characters")
        
        try:
            parsed_data = extract_json_from_response(content)
            search_items = []
            
            for item in parsed_data.get("searches", []):
                search_items.append(WebSearchItem(
                    reason=item.get("reason", "Search for relevant information"),
                    query=item.get("query", query)
                ))
                
            search_plan = WebSearchPlan(searches=search_items)
            logger.info(f"Successfully parsed search plan with {len(search_items)} items")
            
        except Exception:
            logger.warning("Using default search plan due to parsing error")
            
            # fallback 搜索计划
            search_terms = [
                f"{query} basics", f"{query} applications", f"{query} principles",
                f"{query} history", f"{query} trends", f"{query} examples",
                f"{query} advantages", f"{query} challenges"
            ]
            
            search_items = [
                WebSearchItem(reason=f"Understanding aspect {i+1} of {query}", query=term)
                for i, term in enumerate(search_terms)
            ]
            
            search_plan = WebSearchPlan(searches=search_items)
        
    except Exception as e:
        logger.error(f"Planning node error: {e}")
        # 创建最基本的搜索计划
        search_plan = WebSearchPlan(searches=[
            WebSearchItem(reason=f"Basic understanding of {query}", query=query)
        ])
    
    return {"search_plan": search_plan}

async def search_node(state: ResearchState) -> Dict[str, Any]:
    """搜索节点 - 执行并行搜索"""
    search_plan = state["search_plan"]
    logger.info(f"Starting search with {len(search_plan.searches)} items")
    
    async def perform_single_search(search_item: WebSearchItem, index: int) -> str:
        """执行单个搜索"""
        logger.info(f"Executing search {index+1}/{len(search_plan.searches)}: {search_item.query}")
        
        try:
            # 直接调用搜索工具
            search_result = web_search_tool.run(search_item.query)
            
            # 如果搜索结果过长，使用LLM总结
            if len(search_result) > 1000:
                llm = get_current_llm()
                summary_prompt = f"""请为以下搜索结果生成简洁摘要：

搜索词：{search_item.query}
搜索原因：{search_item.reason}

搜索结果：
{search_result[:1500]}

请提供2-3段文字的摘要，少于300字，捕捉核心要点。只返回摘要内容。"""

                summary_response = await llm.ainvoke(summary_prompt)
                result_text = summary_response.content.strip()
            else:
                result_text = search_result
            
            logger.info(f"Search {index+1} completed successfully")
            return f"[{search_item.query}]\n{result_text}"
            
        except Exception as e:
            error_msg = f"Search {index+1} failed: {e}"
            logger.error(error_msg)
            return f"[{search_item.query}]\nSearch failed: {str(e)}"
    
    # 限制并发数量
    semaphore = asyncio.Semaphore(3)
    
    async def limited_search(search_item: WebSearchItem, index: int) -> str:
        async with semaphore:
            return await perform_single_search(search_item, index)
    
    # 执行并行搜索
    search_tasks = [limited_search(item, i) for i, item in enumerate(search_plan.searches)]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    
    # 过滤有效结果
    valid_results = []
    for i, result in enumerate(search_results):
        if isinstance(result, str):
            valid_results.append(result)
        else:
            logger.warning(f"Search {i+1} returned exception: {result}")
    
    logger.info(f"Search phase completed, got {len(valid_results)} valid results")
    return {"search_results": valid_results}

async def writing_node(state: ResearchState) -> Dict[str, Any]:
    """写作节点 - 生成最终报告"""
    query = state["query"]
    search_results = state["search_results"]
    logger.info(f"Starting report writing based on {len(search_results)} search results")
    
    # 组合搜索结果
    combined_results = "\n\n".join(search_results)
    
    system_prompt = """你是一名专业的研究报告撰写专家。
请基于提供的搜索结果撰写一份详细、结构化的研究报告。

报告要求：
1. 使用中文撰写
2. Markdown格式
3. 结构清晰，包含：标题、摘要、目录、正文各章节、结论
4. 内容详实，至少1500字
5. 基于搜索结果，不要编造信息
6. 包含适当的小标题和段落结构

请严格按照以下JSON格式返回：

```json
{
    "short_summary": "2-3句话的简短摘要",
    "markdown_report": "完整的markdown格式报告内容",
    "follow_up_questions": ["后续研究问题1", "后续研究问题2", "后续研究问题3"]
}
```"""
    
    try:
        llm = get_current_llm()
        prompt = f"""{system_prompt}

原始查询: {query}

搜索结果摘要:
{combined_results[:4000]}

请基于以上信息撰写详细的研究报告。"""
        
        response = await llm.ainvoke(prompt)
        content = response.content
        logger.info(f"Writing agent response length: {len(content)} characters")
        
        try:
            parsed_data = extract_json_from_response(content)
            
            report = ReportData(
                short_summary=parsed_data.get("short_summary", f"Research report on {query} completed"),
                markdown_report=parsed_data.get("markdown_report", content),
                follow_up_questions=parsed_data.get("follow_up_questions", [
                    f"Advanced applications of {query}",
                    f"Technical details of {query}", 
                    f"Future trends in {query}"
                ])
            )
            logger.info("Successfully parsed report JSON")
            
        except Exception:
            logger.warning("Using raw content as report due to parsing error")
            
            report = ReportData(
                short_summary=f"Research report on {query} completed based on {len(search_results)} search results",
                markdown_report=content,
                follow_up_questions=[
                    f"Advanced applications of {query}",
                    f"Technical details of {query}", 
                    f"Future trends in {query}"
                ]
            )
        
    except Exception as e:
        logger.error(f"Writing node error: {e}")
        report = ReportData(
            short_summary=f"Error occurred during research report generation for {query}",
            markdown_report=f"# {query} Research Report\n\nSorry, technical issues occurred during report generation. Error: {str(e)}",
            follow_up_questions=[]
        )
    
    logger.info("Report writing phase completed")
    return {"final_report": report}

def create_deepresearch_workflow():
    """创建深度研究工作流"""
    logger.info("Building research workflow...")
    workflow = StateGraph(ResearchState)
    
    # 添加节点
    workflow.add_node("planning", planning_node)
    workflow.add_node("search", search_node) 
    workflow.add_node("writing", writing_node)
    
    # 定义边
    workflow.add_edge("planning", "search")
    workflow.add_edge("search", "writing")
    workflow.add_edge("writing", END)
    
    # 设置入口点
    workflow.set_entry_point("planning")
    
    # 编译工作流
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    logger.info("Research workflow building completed")
    return app

@mcp.tool()
async def deepresearch(query: str, api_key: str) -> ReportData:
    """
    输入一个研究主题，自动完成搜索规划、搜索、写报告。
    返回最终的 ReportData 对象，就是一个markdown格式的完整的研究报告文档
    
    Args:
        query: 研究主题
        api_key: OpenAI API Key
    
    Returns:
        ReportData: 包含摘要、完整报告和后续问题的研究报告
    """
    logger.info(f"Starting deep research for query: {query}")
    
    try:
        # 创建LLM实例
        create_llm_instance(api_key)
        
        # 创建工作流
        app = create_deepresearch_workflow()
        
        # 初始状态
        initial_state = {
            "query": query,
            "search_plan": None,
            "search_results": [],
            "final_report": None,
            "messages": []
        }
        
        # 执行工作流
        config = {"configurable": {"thread_id": f"deepresearch-{hash(query) % 10000}"}}
        final_state = await app.ainvoke(initial_state, config)
        
        logger.info("Deep research process completed successfully!")
        return final_state["final_report"]
        
    except Exception as e:
        logger.error(f"Deep research failed with error: {e}")
        return ReportData(
            short_summary=f"Error occurred during research process for query: {query}",
            markdown_report=f"# {query} Research Report\n\nTechnical error occurred during research: {str(e)}",
            follow_up_questions=[]
        )

async def test_connection(api_key: str) -> bool:
    """测试LLM连接"""
    try:
        create_llm_instance(api_key)
        llm = get_current_llm()
        response = await llm.ainvoke("Hello, please reply briefly to confirm connection.")
        logger.info("LLM connection test successful!")
        return True
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return False

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DeepResearch MCP Server")
    parser.add_argument("--api_key", type=str, help="OpenAI API Key")
    parser.add_argument("--test", action="store_true", help="Run test")
    args = parser.parse_args()
    
    # 加载环境变量
    load_environment()
    
    # 获取API Key
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Error: API Key is required")
        logger.error("Use --api_key parameter or set OPENAI_API_KEY environment variable")
        return
    
    try:
        if args.test:
            # 运行测试
            logger.info("Starting test mode...")
            
            # 测试连接
            if not await test_connection(api_key):
                return
            
            # 测试研究功能
            query = "artificial intelligence in education"
            report = await deepresearch(query, api_key)
            
            # 输出结果
            print("\n" + "="*50)
            print("=== Research Summary ===")
            print(report.short_summary)
            
            print("\n=== Full Report ===")
            print(report.markdown_report)
            
            print("\n=== Follow-up Questions ===")
            for i, question in enumerate(report.follow_up_questions, 1):
                print(f"{i}. {question}")
                
            logger.info("Test completed successfully!")
        else:
            # 启动MCP服务器
            logger.info("Starting DeepResearch MCP Server...")
            logger.info("Waiting for client connections...")
            await mcp.run()
            
    except Exception as e:
        logger.error(f"Program execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())