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
        count: 返回视频数量

    Returns:
        包含视频列表的字典
    """
    try:
        # 搜索视频，按播放量排序
        result = sync(search.search_by_type(
            keyword=keyword,
            search_type=SearchObjectType.VIDEO,
            order_type=OrderVideo.CLICK,  # 按播放量排序
            page=1,
            page_size=min(count, 20)  # 最多获取20个结果
        ))

        videos = []
        if isinstance(result, dict) and 'result' in result:
            for video_item in result['result'][:count]:
                video_info = {
                    "title": video_item.get('title', ''),
                    "bv_id": video_item.get('bvid', ''),
                    "view": video_item.get('play', 0),
                    "danmaku": video_item.get('video_review', 0),
                    "duration": video_item.get('duration', ''),
                    "author": video_item.get('author', ''),
                    "description": video_item.get('description', '')
                }
                videos.append(video_info)

        return {"videos": videos}

    except Exception as e:
        return {"error": f"搜索视频失败: {str(e)}", "videos": []}


def _parse_danmaku_content(danmaku_content: str) -> List[str]:
    """
    解析弹幕内容，提取弹幕文本。

    Args:
        danmaku_content: ASS格式的弹幕内容

    Returns:
        弹幕文本列表
    """
    danmakus = []

    # ASS文件中弹幕文本通常在Dialogue行中
    lines = danmaku_content.split('\n')

    for line in lines:
        if line.startswith('Dialogue:'):
            # 提取弹幕文本（通常是最后一个逗号后的内容）
            parts = line.split(',')
            if len(parts) > 9:
                danmaku_text = ','.join(parts[9:])  # 弹幕文本可能包含逗号
                # 清理ASS格式标签
                danmaku_text = re.sub(r'\{[^}]*\}', '', danmaku_text)
                danmaku_text = danmaku_text.strip()

                if danmaku_text and len(danmaku_text) > 1:  # 过滤过短的弹幕
                    danmakus.append(danmaku_text)

    return danmakus


def _extract_danmaku_keywords(danmakus: List[str], top_n: int = 15) -> List[Dict[str, Any]]:
    """
    提取弹幕中的关键词。

    Args:
        danmakus: 弹幕列表
        top_n: 返回前N个关键词

    Returns:
        关键词统计结果
    """
    # 简单的关键词提取（按字符分割并统计频率）
    words = []
    for danmaku in danmakus:
        # 过滤掉标点符号和空格，只保留中文字符和数字
        clean_text = re.sub(r'[^\u4e00-\u9fa5\w]', ' ', danmaku)
        words.extend(clean_text.split())

    # 过滤掉长度小于2的词和纯数字
    filtered_words = [word for word in words if len(word) >= 2 and not word.isdigit()]

    # 统计词频
    word_count = Counter(filtered_words)

    # 返回前N个关键词及其频次
    return [{"keyword": word, "count": count} for word, count in word_count.most_common(top_n)]


def _analyze_all_danmakus(all_danmakus: List[str]) -> Dict[str, Any]:
    """
    分析所有弹幕的综合数据。

    Args:
        all_danmakus: 所有弹幕文本列表

    Returns:
        综合分析结果
    """
    stats = {
        "total_danmaku_count": len(all_danmakus),
        "average_length": sum(len(d) for d in all_danmakus) / len(all_danmakus) if all_danmakus else 0,
        "top_keywords": _extract_danmaku_keywords(all_danmakus, 15),
        "emotion_analysis": _analyze_emotions(all_danmakus),
        "length_distribution": _analyze_length_distribution(all_danmakus)
    }

    return stats


def _analyze_emotions(danmakus: List[str]) -> Dict[str, int]:
    """
    简单的情感分析。

    Args:
        danmakus: 弹幕列表

    Returns:
        情感统计
    """
    positive_words = ['好', '棒', '赞', '爱了', '太好了', '厉害', '牛', '优秀', '完美', '6666', '666']
    negative_words = ['差', '烂', '垃圾', '无聊', '难看', '不好', '失望']
    neutral_words = ['哈哈', '呵呵', '嗯', '哦', '额', '嘛']

    emotions = {"positive": 0, "negative": 0, "neutral": 0, "other": 0}

    for danmaku in danmakus:
        found_emotion = False

        for word in positive_words:
            if word in danmaku:
                emotions["positive"] += 1
                found_emotion = True
                break

        if not found_emotion:
            for word in negative_words:
                if word in danmaku:
                    emotions["negative"] += 1
                    found_emotion = True
                    break

        if not found_emotion:
            for word in neutral_words:
                if word in danmaku:
                    emotions["neutral"] += 1
                    found_emotion = True
                    break

        if not found_emotion:
            emotions["other"] += 1

    return emotions


def _analyze_length_distribution(danmakus: List[str]) -> Dict[str, int]:
    """
    分析弹幕长度分布。

    Args:
        danmakus: 弹幕列表

    Returns:
        长度分布统计
    """
    distribution = {"short": 0, "medium": 0, "long": 0}  # 短(1-5字)、中(6-15字)、长(>15字)

    for danmaku in danmakus:
        length = len(danmaku)
        if length <= 5:
            distribution["short"] += 1
        elif length <= 15:
            distribution["medium"] += 1
        else:
            distribution["long"] += 1

    return distribution


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
        video_results = _search_popular_videos(keyword, video_count)

        if not video_results.get('videos'):
            return {
                "error": "未找到相关视频",
                "keyword": keyword,
                "videos_found": 0
            }

        # 提取弹幕结果
        results = {
            "keyword": keyword,
            "videos_processed": 0,
            "total_danmaku_count": 0,
            "video_danmakus": []
        }

        for video_info in video_results['videos'][:video_count]:
            bv_id = video_info.get('bv_id')
            if not bv_id:
                continue

            try:
                # 获取弹幕内容
                danmaku_content = get_video_danmaku(bv_id)
                danmaku_list = _parse_danmaku_content(danmaku_content)

                video_danmaku = {
                    "title": video_info.get('title', ''),
                    "bv_id": bv_id,
                    "author": video_info.get('author', ''),
                    "view_count": video_info.get('view', 0),
                    "danmaku_count": len(danmaku_list),
                    "danmakus": danmaku_list
                }

                results["video_danmakus"].append(video_danmaku)
                results["total_danmaku_count"] += len(danmaku_list)
                results["videos_processed"] += 1

            except Exception as e:
                print(f"提取视频 {bv_id} 弹幕时出错: {str(e)}")
                continue

        return results

    except Exception as e:
        return {
            "error": f"提取过程中出错: {str(e)}",
            "keyword": keyword,
            "videos_processed": 0
        }


def main():
    """Main entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
