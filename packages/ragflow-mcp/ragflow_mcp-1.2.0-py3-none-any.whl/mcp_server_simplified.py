from mcp.server.fastmcp import FastMCP
from core.ragflow_api import (
    get_datasets, get_dataset_documents, create_dataset, create_chunk, 
    retrieve_chunks, create_empty_document, find_document_dataset, 
    download_document, upload_document, parse_documents
)
import sys
import argparse
import os
import json

mcp = FastMCP("ragflow_mcp")

# 全局配置变量
ADDRESS = None
API_KEY = None
DATASET_NAME = None
DATASET_ID = None

@mcp.tool(name="list_all_datasets", description="列出所有可用的数据集")
def list_all_datasets() -> str:
    """
    列出所有可用的数据集，返回简化的数据集信息。
    :return: 返回包含语言、名称、ID和chunk方法的数据集列表。
    例如：[{"language": "Chinese", "name": "第二大脑", "id": "c3303d4ee45611ef9b610242ac180003", "chunk_method": "qa"}]
    """
    raw = get_datasets(
        address=ADDRESS,
        api_key=API_KEY,
        page=1,
        page_size=20  # 获取更多数据集
    )
    
    # 解析返回的数据
    if raw and raw.get('code') == 0 and 'data' in raw:
        datasets = raw['data']
        # 提取指定的字段
        dataset_list = []
        for dataset in datasets:
            simplified_dataset = {
                "language": dataset.get('language', 'Unknown'),
                "name": dataset.get('name', 'Unknown'),
                "id": dataset.get('id', 'Unknown'),
                "chunk_method": dataset.get('chunk_method', 'Unknown')
            }
            dataset_list.append(simplified_dataset)
        return str(dataset_list)
    else:
        return "[]"  # 如果没有数据或请求失败，返回空列表

@mcp.tool(name="list_all_documents", description="列出所有数据下的文档")
def list_all_documents(dataset_id = DATASET_ID) -> str:
    """
    列出指定数据集下的所有文档。
    :param dataset_id: 数据集ID，如果未提供则使用默认数据集ID。通常情况下使用默认数据集ID。
    :return: 返回所有文档的名称和ID列表。
    例如：[{"id": "doc1", "name": "文档1"}, {"id": "doc2", "name": "文档2"}]
    """
    raw = get_dataset_documents(
        address=ADDRESS,
        api_key=API_KEY,
        dataset_id=dataset_id,
        page=1,
        page_size=100,  # 设置为100以获取更多文档
        keywords=None,  # 可选参数
        orderby="update_time"
    )
    
    # 解析返回的数据
    if raw and raw.get('code') == 0 and 'data' in raw:
        docs = raw['data'].get('docs', [])
        # 提取文档的ID和名称
        document_list = [{"id": doc['id'], "name": doc['name']} for doc in docs]
        return str(document_list)
    else:
        return "[]"  # 如果没有数据或请求失败，返回空列表

@mcp.tool(name="create_new_dataset", description="创建一个新的数据集")
def create_new_dataset(name: str, description: str = None, language: str = "Chinese", 
                      chunk_method: str = "naive", embedding_model: str = None) -> str:
    """
    创建一个新的数据集。
    
    :param name: 数据集名称，必需参数。只能包含英文字母、数字、下划线，以字母或下划线开头
    :param description: 数据集描述，可选参数
    :param language: 语言设置，可选参数。可选值: "Chinese" (默认), "English"
    :chunk_method: 分块方法，可选值:
            "naive": 通用 (默认)
            "manual": 手动
            "qa": 问答
            "table": 表格
            "paper": 论文
            "book": 书籍
            "laws": 法律
            "presentation": 演示文稿
            "picture": 图片
            "one": 单一
            "knowledge_graph": 知识图谱
            "email": 邮件
    :param embedding_model: 嵌入模型名称，可选参数。例如: "BAAI/bge-zh-v1.5"
    :return: 返回创建结果的状态信息
    """
    result = create_dataset(
        address=ADDRESS,
        api_key=API_KEY,
        name=name,
        description=description,
        language=language,
        chunk_method=chunk_method,
        embedding_model=embedding_model,
        permission="me"  # 固定为 "me"
    )
    
    if result and result.get('code') == 0:
        dataset_info = result.get('data', {})
        dataset_id = dataset_info.get('id', '未知ID')
        dataset_name = dataset_info.get('name', name)
        return f"成功创建数据集 '{dataset_name}'，ID: {dataset_id}"
    else:
        error_msg = result.get('message', '未知错误') if result else '请求失败'
        return f"创建数据集失败: {error_msg}"

@mcp.tool(name="create_empty_document", description="在数据集中创建一个新的空白文档")
def create_empty_document_tool(document_name: str, dataset_id: str = DATASET_ID) -> str:
    """
    在指定数据集中创建一个新的空白文档。
    
    :param document_name: 文档名称，必需参数
    :param dataset_id: 数据集ID，如果未提供则使用默认数据集ID
    :return: 返回创建结果的状态信息，包含新文档的ID
    """
    result = create_empty_document(
        address=ADDRESS,
        api_key=API_KEY,
        dataset_id=dataset_id,
        document_name=document_name
    )
    
    if result and result.get('code') == 0:
        # 处理 API 返回的数据结构（可能是字典或列表）
        data = result.get('data', {})
        
        # 根据实际返回结构调整
        if isinstance(data, list) and len(data) > 0:
            doc_info = data[0]  # 如果是列表，取第一个元素
        elif isinstance(data, dict):
            doc_info = data
        else:
            return f"创建空白文档成功，但返回数据格式异常: {data}"
            
        doc_id = doc_info.get('id', '未知ID')
        doc_name = doc_info.get('name', document_name)
        return f"✅ 成功创建空白文档 '{doc_name}'，ID: {doc_id}。现在可以使用此ID添加chunks。"
    else:
        error_msg = result.get('message', '未知错误') if result else '请求失败'
        return f"❌ 创建空白文档失败: {error_msg}"

@mcp.tool(name="create_chunk_to_document", description="在指定文档中创建新的文本块")
def create_chunk_to_document(document_id: str, content: str, important_keywords: list = None, dataset_id: str = None) -> str:
    """
    在指定的文档中创建新的文本块(chunk)。
    
    :param document_id: 文档ID，必需参数
    :param content: chunk的文本内容，必需参数
    :param important_keywords: 与chunk相关的关键词列表，可选参数
    :param dataset_id: 数据集ID，如果未提供则自动查找文档所属的数据集
    :return: 返回创建结果的状态信息
    """
    # 如果没有提供数据集ID，尝试自动查找
    if not dataset_id:
        print(f"未提供数据集ID，正在查找文档 {document_id} 所属的数据集...")
        dataset_id = find_document_dataset(
            address=ADDRESS,
            api_key=API_KEY,
            document_id=document_id
        )
        
        if not dataset_id:
            return f"❌ 无法找到文档 {document_id} 所属的数据集，请手动指定 dataset_id 参数"
    
    result = create_chunk(
        address=ADDRESS,
        api_key=API_KEY,
        dataset_id=dataset_id,
        document_id=document_id,
        content=content,
        important_keywords=important_keywords
    )
    
    if result and result.get('code') == 0:
        return f"✅ 成功创建chunk到文档 {document_id}。chunk内容: {content[:50]}..."
    else:
        error_msg = result.get('message', '未知错误') if result else '请求失败'
        return f"❌ 创建chunk失败: {error_msg}"

def get_all_dataset_ids():
    """
    获取所有数据集的ID列表
    
    :return: 数据集ID列表，如果失败则返回空列表
    """
    result = get_datasets(
        address=ADDRESS,
        api_key=API_KEY,
        page=1,
        page_size=100  # 假设不会超过100个数据集
    )
    
    if result and result.get('code') == 0:
        datasets = result.get('data', {})
        # 处理数据集数据的不同格式
        if isinstance(datasets, list):
            # 如果data是列表
            return [ds.get('id') for ds in datasets if ds.get('id')]
        elif isinstance(datasets, dict) and 'datasets' in datasets:
            # 如果data是字典且包含datasets字段
            datasets_list = datasets.get('datasets', [])
            return [ds.get('id') for ds in datasets_list if ds.get('id')]
        else:
            print(f"未知的数据集数据格式: {datasets}")
            return []
    else:
        print(f"获取数据集列表失败: {result}")
        return []

@mcp.tool(name="search_chunks", description="从数据集中检索相关的文本块")
def search_chunks(question: str, dataset_id: str = None, page_size: int = 5, similarity_threshold: float = 0.1) -> str:
    """
    从指定数据集中检索与问题相关的文本块。
    
    :param question: 要搜索的问题或关键词，必需参数
    :param dataset_id: 数据集ID，如果未提供则在所有数据集中搜索
    :param page_size: 返回的最大结果数量，默认为5
    :param similarity_threshold: 相似度阈值，默认为0.1
    :return: 返回检索结果的格式化字符串
    """
    # 确定要搜索的数据集ID列表
    if dataset_id:
        dataset_ids = [dataset_id]
        search_scope = f"数据集 {dataset_id}"
    else:
        # 获取所有数据集ID
        dataset_ids = get_all_dataset_ids()
        if not dataset_ids:
            return "❌ 无法获取数据集列表，无法进行搜索"
        search_scope = f"所有数据集（共{len(dataset_ids)}个）"
    
    result = retrieve_chunks(
        address=ADDRESS,
        api_key=API_KEY,
        question=question,
        dataset_ids=dataset_ids,
        page=1,
        page_size=page_size,
        similarity_threshold=similarity_threshold,
        vector_similarity_weight=0.5,
        top_k=50,
        keyword=False,  # 启用关键词匹配
        highlight=False  # 启用高亮显示
    )
    
    if result and result.get('code') == 0:
        chunks = result.get('data', {}).get('chunks', [])
        total_count = result.get('data', {}).get('total', len(chunks))
        
        if not chunks:
            return f"在{search_scope}中未找到与 '{question}' 相关的内容"
        
        # 格式化返回结果
        formatted_results = []
        for i, chunk in enumerate(chunks[:page_size], 1):
            # 优先使用高亮内容，如果没有则使用原始内容
            content = chunk.get('highlight', chunk.get('content', ''))
            similarity = chunk.get('similarity', 0)
            # 修正文档名称字段
            doc_name = chunk.get('document_keyword', chunk.get('document_name', '未知文档'))
            # 获取关键词信息
            keywords = chunk.get('important_keywords', [])
            keywords_str = ', '.join(keywords) if keywords else ''
            
            # 构建结果字符串
            result_str = f"{i}. 【{doc_name}】(相似度: {similarity:.3f})"
            if keywords_str:
                result_str += f"\n关键词: {keywords_str}"
            result_str += f"\n{content[:500]}{'...' if len(content) > 500 else ''}"
            
            formatted_results.append(result_str)
        
        return f"在{search_scope}中找到 {total_count} 个相关结果（显示前{len(chunks)}个）：\n\n" + "\n\n".join(formatted_results)
    else:
        error_msg = result.get('message', '未知错误') if result else '请求失败'
        return f"检索失败: {error_msg}"

@mcp.tool(name="download_document", description="从数据集中下载指定的文档")
def download_document_tool(document_id: str, output_path: str = None, dataset_id: str = None) -> str:
    """
    从指定数据集中下载文档到本地。
    
    :param document_id: 文档ID，必需参数
    :param output_path: 输出文件路径，可选参数。如果未提供，将保存到当前目录下以document_id命名的文件
    :param dataset_id: 数据集ID，如果未提供则自动查找文档所属的数据集
    :return: 返回下载结果的状态信息
    """
    # 如果没有提供数据集ID，尝试自动查找
    if not dataset_id:
        print(f"未提供数据集ID，正在查找文档 {document_id} 所属的数据集...")
        dataset_id = find_document_dataset(
            address=ADDRESS,
            api_key=API_KEY,
            document_id=document_id
        )
        
        if not dataset_id:
            return f"❌ 无法找到文档 {document_id} 所属的数据集，请手动指定 dataset_id 参数"
    
    # 调用下载函数
    result_path = download_document(
        address=ADDRESS,
        api_key=API_KEY,
        dataset_id=dataset_id,
        document_id=document_id,
        output_path=output_path
    )
    
    if result_path:
        return f"✅ 文档下载成功！文件已保存到: {result_path}"
    else:
        return f"❌ 文档下载失败，请检查文档ID和权限设置"

@mcp.tool(name="upload_documents", description="上传单个或多个文档到RagFlow")
def upload_documents_tool(file_paths: list = None, dataset_id: str = None) -> str:
    """
    简化的文档上传工具，支持单个或多个文件上传。
    
    特点：
    - 接受单个文件路径(字符串)或多个文件路径(列表)
    - 自动使用原始文件名，不允许自定义名称
    - 让API处理文件类型验证
    - 简化的错误处理
    
    :param file_paths: 文件路径，可以是字符串(单个文件)或列表(多个文件)
    :param dataset_id: 数据集ID，如果未提供则使用默认数据集
    :return: JSON格式的上传结果
    """
    try:
        # 如果没有提供数据集ID，获取默认数据集
        if not dataset_id:
            datasets_raw = get_datasets(
                address=ADDRESS,
                api_key=API_KEY,
                page=1,
                page_size=1
            )
            if not datasets_raw or datasets_raw.get('code') != 0:
                return json.dumps({
                    "error": "No datasets available. Please create a dataset first."
                }, ensure_ascii=False, indent=2)
            
            # 获取第一个数据集
            datasets = datasets_raw.get('data', [])
            if not datasets:
                return json.dumps({
                    "error": "No datasets found."
                }, ensure_ascii=False, indent=2)
                
            dataset_id = datasets[0]['id']
            
        # 如果file_paths是字符串，转换为列表
        if isinstance(file_paths, str):
            file_paths = [file_paths]
            
        if not file_paths:
            return json.dumps({
                "error": "No file paths provided"
            }, ensure_ascii=False, indent=2)
            
        results = []
        
        # 逐个上传文件
        for file_path in file_paths:
            try:
                # 检查文件是否存在
                if not os.path.exists(file_path):
                    results.append({
                        "file_path": file_path,
                        "error": "File not found"
                    })
                    continue
                
                # 使用原始文件名
                filename = os.path.basename(file_path)
                
                # 上传文件
                result = upload_document(
                    address=ADDRESS,
                    api_key=API_KEY,
                    dataset_id=dataset_id,
                    file_path=file_path,
                    document_name=filename
                )
                
                results.append({
                    "file_path": file_path,
                    "filename": filename,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "file_path": file_path,
                    "error": str(e)
                })
        
        return json.dumps({
            "dataset_id": dataset_id,
            "upload_results": results
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Upload failed: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool(name="parse_documents", description="解析指定数据集中的文档，生成chunks")
def parse_documents_tool(document_ids: list = None, dataset_id: str = None) -> str:
    """
    解析指定数据集中的文档，生成文本块(chunks)。
    
    特点：
    - 接受单个文档ID(字符串)或多个文档ID(列表)
    - 触发RagFlow对文档进行解析和分块处理
    - 简化的错误处理
    
    :param document_ids: 文档ID，可以是字符串(单个文档)或列表(多个文档)
    :param dataset_id: 数据集ID，如果未提供则使用默认数据集
    :return: JSON格式的解析结果
    """
    try:
        # 如果没有提供数据集ID，获取默认数据集
        if not dataset_id:
            datasets_raw = get_datasets(
                address=ADDRESS,
                api_key=API_KEY,
                page=1,
                page_size=1
            )
            if not datasets_raw or datasets_raw.get('code') != 0:
                return json.dumps({
                    "error": "No datasets available. Please create a dataset first."
                }, ensure_ascii=False, indent=2)
            
            # 获取第一个数据集
            datasets = datasets_raw.get('data', [])
            if not datasets:
                return json.dumps({
                    "error": "No datasets found."
                }, ensure_ascii=False, indent=2)
                
            dataset_id = datasets[0]['id']
            
        # 如果document_ids是字符串，转换为列表
        if isinstance(document_ids, str):
            document_ids = [document_ids]
            
        if not document_ids:
            return json.dumps({
                "error": "No document IDs provided"
            }, ensure_ascii=False, indent=2)
            
        # 调用解析文档API
        result = parse_documents(
            address=ADDRESS,
            api_key=API_KEY,
            dataset_id=dataset_id,
            document_ids=document_ids
        )
        
        if result and result.get('code') == 0:
            return json.dumps({
                "success": True,
                "dataset_id": dataset_id,
                "document_ids": document_ids,
                "message": f"Successfully started parsing {len(document_ids)} documents",
                "result": result
            }, ensure_ascii=False, indent=2)
        else:
            error_msg = result.get('message', '未知错误') if result else '请求失败'
            return json.dumps({
                "error": f"Parse documents failed: {error_msg}",
                "dataset_id": dataset_id,
                "document_ids": document_ids
            }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Parse documents failed: {str(e)}"
        }, ensure_ascii=False, indent=2)

def main():
    """
    主函数，解析命令行参数并启动MCP服务器
    """
    global ADDRESS, API_KEY, DATASET_ID, DATASET_NAME
    
    parser = argparse.ArgumentParser(description='RagFlow MCP 服务器 (简化版)')
    parser.add_argument('--address', required=True, help='RagFlow服务器地址 (例如: ragflow.example.com)')
    parser.add_argument('--api-key', required=True, help='RagFlow API密钥')
    parser.add_argument('--dataset-id', help='默认数据集ID')
    parser.add_argument('--dataset-name', default='第二大脑', help='默认数据集名称')
    
    args = parser.parse_args()
    
    # 设置全局配置
    ADDRESS = args.address
    API_KEY = args.api_key
    DATASET_ID = args.dataset_id
    DATASET_NAME = args.dataset_name
    
    # 启动前验证连接
    print(f"🔧 RagFlow MCP 服务器配置 (简化版):", file=sys.stderr)
    print(f"   服务器地址: {ADDRESS}", file=sys.stderr)
    print(f"   API密钥: {'✅ 已配置' if API_KEY else '❌ 未配置'}", file=sys.stderr)
    print(f"   默认数据集: {DATASET_NAME} ({DATASET_ID if DATASET_ID else '未指定'})", file=sys.stderr)
    
    # 验证连接
    try:
        result = get_datasets(address=ADDRESS, api_key=API_KEY, page=1, page_size=1)
        if result and result.get('code') == 0:
            print("✅ RagFlow连接验证成功", file=sys.stderr)
        else:
            print("❌ RagFlow连接验证失败，请检查地址和API密钥", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"❌ RagFlow连接验证失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    # 启动MCP服务器
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
