import os
import asyncio
import argparse
import json
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
import sys

# 配置日志 - 输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr,  # 重要：输出到stderr
    encoding='utf-8'    # 添加编码设置
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
            logger.info(f"✅ 加载环境变量文件: {env_path}")
            break
    
    if not env_loaded:
        logger.warning("❌ 警告: 未找到 .env 文件")
    
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
    logger.info("✅ LLM实例创建成功")
    return current_llm

def get_current_llm() -> ChatOpenAI:
    """获取当前LLM实例，如果没有则抛出异常"""
    if current_llm is None:
        raise ValueError("LLM实例未初始化，请先调用create_llm_instance()")
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
        logger.error(f"搜索失败: {str(e)}")
        return f"搜索失败: {str(e)}"

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
            raise ValueError("未找到JSON格式数据")
        
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"JSON解析失败: {e}")
        raise

async def planning_node(state: ResearchState) -> Dict[str, Any]:
    """规划节点 - 生成搜索计划"""
    query = state["query"]
    logger.info(f"📋 开始规划搜索: {query}")
    
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
        logger.info(f"📋 规划 Agent 响应长度: {len(content)} 字符")
        
        try:
            parsed_data = extract_json_from_response(content)
            search_items = []
            
            for item in parsed_data.get("searches", []):
                search_items.append(WebSearchItem(
                    reason=item.get("reason", "搜索相关信息"),
                    query=item.get("query", query)
                ))
                
            search_plan = WebSearchPlan(searches=search_items)
            logger.info(f"✅ 成功解析搜索计划，共 {len(search_items)} 项")
            
        except Exception:
            logger.warning("⚠️ 使用默认搜索计划...")
            
            # fallback 搜索计划
            search_terms = [
                f"{query} 基础概念", f"{query} 应用场景", f"{query} 技术原理",
                f"{query} 发展历史", f"{query} 未来趋势", f"{query} 实际案例",
                f"{query} 优势特点", f"{query} 挑战问题"
            ]
            
            search_items = [
                WebSearchItem(reason=f"了解{query}的第{i+1}个方面", query=term)
                for i, term in enumerate(search_terms)
            ]
            
            search_plan = WebSearchPlan(searches=search_items)
        
    except Exception as e:
        logger.error(f"❌ 规划节点出错: {e}")
        # 创建最基本的搜索计划
        search_plan = WebSearchPlan(searches=[
            WebSearchItem(reason=f"基础了解{query}", query=query)
        ])
    
    return {"search_plan": search_plan}

async def search_node(state: ResearchState) -> Dict[str, Any]:
    """搜索节点 - 执行并行搜索"""
    search_plan = state["search_plan"]
    logger.info(f"🔍 开始搜索，共 {len(search_plan.searches)} 项")
    
    async def perform_single_search(search_item: WebSearchItem, index: int) -> str:
        """执行单个搜索"""
        logger.info(f"  搜索 {index+1}/{len(search_plan.searches)}: {search_item.query}")
        
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
            
            logger.info(f"  ✅ 搜索 {index+1} 完成")
            return f"【{search_item.query}】\n{result_text}"
            
        except Exception as e:
            logger.error(f"  ❌ 搜索 {index+1} 失败: {e}")
            return f"【{search_item.query}】\n搜索失败: {str(e)}"
    
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
            logger.warning(f"  ⚠️ 搜索 {i+1} 异常: {result}")
    
    logger.info(f"✅ 搜索完成，获得 {len(valid_results)} 个有效结果")
    return {"search_results": valid_results}

async def writing_node(state: ResearchState) -> Dict[str, Any]:
    """写作节点 - 生成最终报告"""
    query = state["query"]
    search_results = state["search_results"]
    logger.info(f"✍️ 开始写作报告，基于 {len(search_results)} 个搜索结果")
    
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
        logger.info(f"✍️ 写作 Agent 响应长度: {len(content)} 字符")
        
        try:
            parsed_data = extract_json_from_response(content)
            
            report = ReportData(
                short_summary=parsed_data.get("short_summary", f"关于{query}的研究报告"),
                markdown_report=parsed_data.get("markdown_report", content),
                follow_up_questions=parsed_data.get("follow_up_questions", [
                    f"{query}的深入应用",
                    f"{query}的技术细节", 
                    f"{query}的未来发展"
                ])
            )
            logger.info("✅ 成功解析报告JSON")
            
        except Exception:
            logger.warning("⚠️ 使用原始内容作为报告...")
            
            report = ReportData(
                short_summary=f"关于{query}的研究报告已完成，基于{len(search_results)}个搜索结果生成。",
                markdown_report=content,
                follow_up_questions=[
                    f"{query}的深入应用",
                    f"{query}的技术细节", 
                    f"{query}的未来发展"
                ]
            )
        
    except Exception as e:
        logger.error(f"❌ 写作节点出错: {e}")
        report = ReportData(
            short_summary=f"关于{query}的研究报告生成过程中遇到问题",
            markdown_report=f"# {query} 研究报告\n\n抱歉，报告生成过程中遇到技术问题。错误信息：{str(e)}",
            follow_up_questions=[]
        )
    
    logger.info("✅ 报告写作完成")
    return {"final_report": report}

def create_deepresearch_workflow():
    """创建深度研究工作流"""
    logger.info("🔧 构建工作流...")
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
    
    logger.info("✅ 工作流构建完成")
    return app

@mcp.tool()
async def deepresearch(query: str, api_key: str) -> dict:
    """
    输入一个研究主题，自动完成搜索规划、搜索、写报告。
    返回包含研究报告的字典
    
    Args:
        query: 研究主题
        api_key: OpenAI API Key
    
    Returns:
        dict: 包含摘要、完整报告和后续问题的字典
    """
    logger.info(f"🚀 开始深度研究: {query}")
    
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
        config = {"configurable": {"thread_id": f"deepresearch-{abs(hash(query)) % 10000}"}}
        final_state = await app.ainvoke(initial_state, config)
        
        report = final_state["final_report"]
        logger.info("🎉 深度研究完成!")
        
        # 返回字典格式，便于MCP Inspector显示
        return {
            "success": True,
            "short_summary": report.short_summary,
            "markdown_report": report.markdown_report,
            "follow_up_questions": report.follow_up_questions
        }
        
    except Exception as e:
        logger.error(f"❌ 深度研究失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "short_summary": f"关于{query}的研究过程中遇到错误",
            "markdown_report": f"# {query} 研究报告\n\n研究过程中遇到技术问题: {str(e)}",
            "follow_up_questions": []
        }

async def test_connection(api_key: str) -> bool:
    """测试LLM连接"""
    try:
        create_llm_instance(api_key)
        llm = get_current_llm()
        response = await llm.ainvoke("Hello, please reply briefly to confirm connection.")
        logger.info("✅ LLM连接测试成功!")
        return True
    except Exception as e:
        logger.error(f"❌ LLM连接测试失败: {e}")
        return False

def run_server(api_key: str):
    """运行MCP服务器 - 同步版本"""
    logger.info("🚀 启动DeepResearch MCP服务器...")
    logger.info("等待客户端连接...")
    
    # 设置全局API Key（如果需要默认值）
    global current_llm
    try:
        create_llm_instance(api_key)
        logger.info("✅ 默认LLM实例已创建")
    except Exception as e:
        logger.warning(f"⚠️ 默认LLM实例创建失败: {e}")
    
    # 运行MCP服务器
    mcp.run()

async def run_test(api_key: str):
    """运行测试"""
    logger.info("🧪 开始测试...")
    
    # 测试连接
    if not await test_connection(api_key):
        return
    
    # 测试研究功能
    query = "人工智能在教育领域的应用"
    result = await deepresearch(query, api_key)
    
    # 输出结果
    print("\n" + "="*50, file=sys.stderr)
    print("=== 测试结果 ===", file=sys.stderr)
    print(f"成功: {result.get('success')}", file=sys.stderr)
    print(f"摘要: {result.get('short_summary', '')}", file=sys.stderr)
    
    if result.get('success'):
        print("\n=== 完整报告 ===", file=sys.stderr)
        print(result.get('markdown_report', '')[:500] + "...", file=sys.stderr)
        
        print("\n=== 后续研究建议 ===", file=sys.stderr)
        for i, question in enumerate(result.get('follow_up_questions', []), 1):
            print(f"{i}. {question}", file=sys.stderr)
    
    logger.info("🎉 测试完成!")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DeepResearch MCP Server")
    parser.add_argument("--api_key", type=str, required=True, help="OpenAI API Key")
    parser.add_argument("--test", action="store_true", help="运行测试")
    args = parser.parse_args()
    
    # 加载环境变量
    load_environment()
    
    try:
        if args.test:
            # 运行测试（异步）
            asyncio.run(run_test(args.api_key))
        else:
            # 启动MCP服务器（同步）
            run_server(args.api_key)
            
    except Exception as e:
        logger.error(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 检查是否已经在运行的事件循环中
    try:
        # 如果已经在事件循环中，直接运行
        loop = asyncio.get_running_loop()
        logger.warning("⚠️ 检测到正在运行的事件循环，使用同步模式")
        main()
    except RuntimeError:
        # 没有事件循环，正常启动
        main()