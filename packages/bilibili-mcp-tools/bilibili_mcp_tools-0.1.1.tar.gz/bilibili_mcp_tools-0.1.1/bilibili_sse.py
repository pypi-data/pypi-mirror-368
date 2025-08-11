import os
import re
from collections import Counter
from typing import Any, Optional, Dict, List

from bilibili_api import search, sync, ass, video
from bilibili_api.search import SearchObjectType, OrderUser, OrderVideo
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Bilibili mcp server")

@mcp.tool()
def clean_travel_data(keyword: str) -> Dict[str, Any]:
    """
    清洗B站搜索结果，提取所有有效的description。

    Args:
        keyword: 搜索关键词

    Returns:
        包含有用description列表的字典
    """
    cleaned_data = {
        "keyword": keyword,
        "descriptions": [],
        "summary": {
            "total_videos": 0,
            "valid_descriptions": 0,
            "filtered_out": 0
        }
    }

    try:
        # 获取搜索结果
        raw_data = sync(search.search_by_type(
            keyword=keyword,
            search_type=SearchObjectType.VIDEO,
            page=1,
            page_size=20
        ))

        # 检查数据结构
        if not isinstance(raw_data, dict) or 'result' not in raw_data:
            cleaned_data["error"] = "无法获取搜索结果"
            return cleaned_data

        # 处理视频数据
        video_data = raw_data.get('result', [])
        cleaned_data["summary"]["total_videos"] = len(video_data)

        for video in video_data:
            description = video.get('description', '').strip()

            # 过滤条件：
            # 1. 不为空
            # 2. 不是 "-" 或其他无意义字符
            # 3. 长度大于等于10个字符
            if description and description != "-" and len(description) >= 10:
                cleaned_data["descriptions"].append(description)
                cleaned_data["summary"]["valid_descriptions"] += 1
            else:
                cleaned_data["summary"]["filtered_out"] += 1

    except Exception as e:
        cleaned_data["error"] = f"搜索失败: {str(e)}"

    return cleaned_data


@mcp.tool()
def general_search(keyword: str) -> dict[Any, Any]:
    """
    Search Bilibili API with the given keyword.

    Args:
        keyword: Search term to look for on Bilibili

    Returns:
        Dictionary containing the search results from Bilibili
    """
    return sync(search.search(keyword))


@mcp.tool()
def search_user(keyword: str, page: int = 1) -> dict[Any, Any]:
    """
    搜索哔哩哔哩用户信息。

    Args:
        keyword: 用户名关键词
        page: 页码，默认为1

    Returns:
        包含用户搜索结果的字典数据
    """
    return sync(search.search_by_type(
        keyword=keyword,
        search_type=SearchObjectType.USER,
        order_type=OrderUser.FANS,
        page=page
    ))


@mcp.tool()
def get_precise_results(keyword: str, search_type: str = "user") -> Dict[str, Any]:
    """
    获取精确的搜索结果，过滤掉不必要的信息。

    Args:
        keyword: 搜索关键词
        search_type: 搜索类型，默认为"user"(用户)，可选："video", "user", "live", "article"

    Returns:
        精简后的搜索结果，只返回完全匹配的结果
    """
    type_map = {
        "user": SearchObjectType.USER,
        "video": SearchObjectType.VIDEO,
        "live": SearchObjectType.LIVE,
        "article": SearchObjectType.ARTICLE
    }

    search_obj_type = type_map.get(search_type.lower(), SearchObjectType.USER)

    # 增加页面大小以提高匹配几率
    result = sync(search.search_by_type(
        keyword=keyword,
        search_type=search_obj_type,
        page=1,
        page_size=50
    ))

    # 提取关键信息，过滤掉不必要的字段
    if search_type.lower() == "user" and "result" in result:
        filtered_result = []
        exact_match_result = []

        for user in result.get("result", []):
            # 只保留关键信息
            filtered_user = {
                "uname": user.get("uname", ""),
                "mid": user.get("mid", 0),
                "face": user.get("upic", ""),
                "fans": user.get("fans", 0),
                "videos": user.get("videos", 0),
                "level": user.get("level", 0),
                "sign": user.get("usign", ""),
                "official": user.get("official_verify", {}).get("desc", "")
            }

            # 检查是否完全匹配
            if user.get("uname", "").lower() == keyword.lower():
                exact_match_result.append(filtered_user)
            else:
                filtered_result.append(filtered_user)

        # 如果有精确匹配结果，只返回精确匹配
        if exact_match_result:
            return {"users": exact_match_result, "exact_match": True}

        # 否则返回所有结果，但标记为非精确匹配
        return {"users": filtered_result, "exact_match": False}

    return result


@mcp.tool()
def get_video_danmaku(bv_id: str) -> str:
    """
    获取视频的弹幕数据。

    Args:
        bv_id: 视频的BV号

    Returns:
        弹幕数据
    """
    # 定义video对象
    v = video.Video(bv_id)
    # 生成弹幕文件
    output_filepath = "protobuf.ass"
    sync(ass.make_ass_file_danmakus_protobuf(
        obj=v, # 生成弹幕文件的对象
        page=0, # 哪一个分 P (从 0 开始)
        out=output_filepath # 输出文件地址
    ))
    # 读取弹幕文件
    with open(output_filepath, 'r') as f:
        content = f.read()
    # 删除弹幕文件
    os.remove(output_filepath)

    return content


def _search_popular_videos(keyword: str, count: int = 5) -> Dict[str, Any]:
    """
    搜索热门视频。

    Args:
        keyword: 搜索关键词
        count: 返回视频数量，默认5个

    Returns:
        包含视频信息的字典
    """
    try:
        result = sync(search.search_by_type(
            keyword=keyword,
            search_type=SearchObjectType.VIDEO,
            order_type=OrderVideo.VIEW,  # 按播放量排序
            page=1,
            page_size=count
        ))

        if "result" in result:
            videos = []
            for video_info in result["result"]:
                video_data = {
                    "title": video_info.get("title", ""),
                    "bv_id": video_info.get("bvid", ""),
                    "author": video_info.get("author", ""),
                    "description": video_info.get("description", ""),
                    "view_count": video_info.get("view", 0),
                    "duration": video_info.get("duration", ""),
                    "pubdate": video_info.get("pubdate", 0)
                }
                videos.append(video_data)

            return {"videos": videos, "count": len(videos)}

        return {"videos": [], "count": 0, "error": "无法获取搜索结果"}

    except Exception as e:
        return {"videos": [], "count": 0, "error": f"搜索失败: {str(e)}"}


@mcp.tool()
def extract_video_danmaku(keyword: str, video_count: int = 5) -> Dict[str, Any]:
    """
    根据关键词搜索热门视频并提取弹幕内容。

    Args:
        keyword: 搜索关键词
        video_count: 提取弹幕的视频数量，默认为5

    Returns:
        包含视频信息和弹幕内容的字典
    """
    try:
        # 搜索热门视频
        video_search_result = _search_popular_videos(keyword, video_count)

        if "error" in video_search_result:
            return video_search_result

        videos = video_search_result.get("videos", [])

        results = {
            "keyword": keyword,
            "video_danmakus": [],
            "total_danmaku_count": 0,
            "videos_processed": 0,
            "errors": []
        }

        for video_info in videos:
            bv_id = video_info.get("bv_id", "")
            if not bv_id:
                continue

            try:
                # 获取弹幕
                danmaku_content = get_video_danmaku(bv_id)

                # 解析弹幕文本 (从ASS文件格式中提取)
                danmaku_list = []
                if danmaku_content:
                    lines = danmaku_content.split('\n')
                    for line in lines:
                        if line.startswith('Dialogue:'):
                            # ASS格式的弹幕行
                            parts = line.split(',', 9)
                            if len(parts) >= 10:
                                danmaku_text = parts[9].strip()
                                # 清理格式标记
                                danmaku_text = re.sub(r'\{[^}]*\}', '', danmaku_text)
                                if danmaku_text and len(danmaku_text.strip()) > 0:
                                    danmaku_list.append(danmaku_text.strip())

                video_danmaku = {
                    "bv_id": bv_id,
                    "title": video_info.get('title', ''),
                    "author": video_info.get('author', ''),
                    "view_count": video_info.get('view', 0),
                    "danmaku_count": len(danmaku_list),
                    "danmakus": danmaku_list
                }

                results["video_danmakus"].append(video_danmaku)
                results["total_danmaku_count"] += len(danmaku_list)
                results["videos_processed"] += 1

            except Exception as e:
                error_msg = f"提取视频 {bv_id} 弹幕时出错: {str(e)}"
                results["errors"].append(error_msg)
                print(error_msg)
                continue

        return results

    except Exception as e:
        return {
            "error": f"提取过程中出错: {str(e)}",
            "keyword": keyword,
            "videos_processed": 0
        }


def main():
    """Main entry point for the MCP server with SSE transport."""
    import argparse

    parser = argparse.ArgumentParser(description='Bilibili MCP Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')

    args = parser.parse_args()

    print(f"Starting Bilibili MCP Server with SSE transport on {args.host}:{args.port}")
    mcp.run(transport='sse', host=args.host, port=args.port)

if __name__ == "__main__":
    main()
