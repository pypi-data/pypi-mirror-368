import asyncio
from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
import time
from typing import Dict, List

class TestDouyinMCPServer:
    def __init__(self):
        self.page = None
        self.collected_data = {
            'videos': [],
            'users': []
        }
    
    async def _init_browser(self) -> bool:
        """初始化浏览器"""
        try:
            if self.page is None:
                self.page = ChromiumPage()
                await asyncio.sleep(2)  # 等待浏览器启动
            return True
        except Exception as e:
            print(f"浏览器初始化失败: {e}")
            return False
    
    async def _cleanup_browser(self):
        """清理浏览器资源"""
        try:
            if self.page:
                self.page.quit()
                self.page = None
        except Exception as e:
            print(f"清理浏览器失败: {e}")
    
    def _extract_video_items(self, html) -> List[Dict]:
        """提取视频数据"""
        video_data = []
        
        try:
            # 查找视频项目 - 更新为新的页面结构
            video_items = html.select('li.SwZLHMKk')
            print(f"找到 {len(video_items)} 个视频项目")
            
            for item in video_items:
                try:
                    data = self._extract_basic_info(item)
                    self._extract_stats_info(item, data)
                    self._extract_description(item, data)
                    
                    # 清理和格式化数据
                    data = self._clean_and_format_data(data)
                    
                    if data['title']:  # 只添加有标题的数据
                        video_data.append(data)
                        
                except Exception as e:
                    print(f"提取单个视频数据失败: {e}")
                    continue
        
        except Exception as e:
            print(f"提取视频数据失败: {e}")
        
        return video_data
    
    def _extract_basic_info(self, item) -> Dict:
        """提取基本信息"""
        data = {
            'title': '',
            'author': '',
            'video_link': '',
            'publish_time': '',
            'likes': '0',
            'comments': '0',
            'shares': '0'
        }
        
        try:
            # 提取标题 - 新的选择器
            title_elem = item.select_one('div.VDYK8Xd7')
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
            
            # 提取作者 - 新的选择器
            author_elem = item.select_one('span.MZNczJmS')
            if author_elem:
                data['author'] = author_elem.get_text(strip=True)
            
            # 提取视频链接 - 新的选择器
            link_elem = item.select_one('a.hY8lWHgA')
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('//'):
                    data['video_link'] = 'https:' + href
                else:
                    data['video_link'] = href
            
            # 提取发布时间
            time_elem = item.select_one('span.faDtinfi')
            if time_elem:
                data['publish_time'] = time_elem.get_text(strip=True)
        
        except Exception as e:
            print(f"提取基本信息失败: {e}")
        
        return data
    
    def _extract_stats_info(self, item, data: Dict):
        """提取统计信息"""
        try:
            # 查找点赞数 - 新的选择器
            likes_elem = item.select_one('span.cIiU4Muu')
            if likes_elem:
                likes_text = likes_elem.get_text(strip=True)
                data['likes'] = likes_text
        
        except Exception as e:
            print(f"提取统计信息失败: {e}")
    
    def _extract_description(self, item, data: Dict):
        """提取描述信息"""
        try:
            # 尝试从标题元素中获取描述，或者查找其他可能的描述元素
            desc_elem = item.select_one('div.VDYK8Xd7')
            if desc_elem:
                # 如果标题元素包含描述信息，使用它
                data['description'] = desc_elem.get_text(strip=True)
            else:
                # 否则保持为空
                data['description'] = ''
        
        except Exception as e:
            print(f"提取描述信息失败: {e}")
    
    def _clean_and_format_data(self, data: Dict) -> Dict:
        """清理和格式化数据"""
        # 清理文本
        for key in ['title', 'author', 'description']:
            if key in data:
                data[key] = self._clean_text(data[key])
        
        # 格式化数字
        for key in ['likes', 'comments', 'shares']:
            if key in data:
                data[key] = self._format_number(data[key])
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ''
        return text.strip().replace('\n', ' ').replace('\r', ' ')
    
    def _format_number(self, num_str: str) -> str:
        """格式化数字"""
        if not num_str:
            return '0'
        return num_str.strip()
    
    async def _scroll_and_collect(self, scroll_count: int, delay: float, data_type: str) -> List[Dict]:
        """滚动页面并收集数据"""
        collected = []
        
        try:
            last_height = self.page.run_js("return document.body.scrollHeight")
            
            for i in range(scroll_count):
                # 滚动页面
                self.page.run_js("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(delay)
                
                # 检查是否到达底部
                new_height = self.page.run_js("return document.body.scrollHeight")
                if new_height == last_height:
                    print("已到达页面底部")
                    break
                last_height = new_height
                
                # 获取页面源码并解析
                page_source = self.page.html
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # 根据数据类型选择不同的提取方法
                if data_type == 'user':
                    new_data = []  # 暂时不实现用户数据提取
                else:
                    # 直接传递整个soup对象给视频提取方法
                    new_data = self._extract_video_items(soup)
                    print(f"本次滚动提取到 {len(new_data)} 条视频数据")
                
                # 添加新数据（去重）
                for data in new_data:
                    if data not in collected:
                        collected.append(data)
                
                print(f"滚动 {i+1}/{scroll_count}，当前采集 {len(collected)} 条数据")
        
        except Exception as e:
            print(f"滚动采集失败: {e}")
        
        return collected
    
    async def search_douyin_videos(self, keyword: str, scroll_count: int = 10, delay: float = 2.0):
        """搜索抖音视频"""
        try:
            # 初始化浏览器
            if not await self._init_browser():
                return "浏览器初始化失败"
            
            # 构建搜索URL
            from urllib.parse import quote
            search_url = f"https://www.douyin.com/search/{quote(keyword)}?source=normal_search&type=video"
            print(f"访问搜索页面: {search_url}")
            
            # 访问页面
            self.page.get(search_url)
            await asyncio.sleep(3)  # 等待页面加载
            
            # 滚动并收集数据
            new_data = await self._scroll_and_collect(scroll_count, delay, 'video')
            
            # 添加到总数据中
            for data in new_data:
                if data not in self.collected_data['videos']:
                    self.collected_data['videos'].append(data)
            
            result_text = f"成功采集到 {len(new_data)} 条视频数据\n"
            result_text += f"当前总共有 {len(self.collected_data['videos'])} 条视频数据\n\n"
            
            # 显示前5条数据作为预览
            if new_data:
                result_text += "最新采集的视频数据预览:\n"
                for i, data in enumerate(new_data[:5]):
                    result_text += f"{i+1}. {data.get('title', 'N/A')} - {data.get('author', 'N/A')} - {data.get('likes', 'N/A')}赞\n"
            
            return result_text
            
        except Exception as e:
            print(f"搜索视频失败: {e}")
            import traceback
            traceback.print_exc()
            return f"搜索失败: {str(e)}"
        finally:
            await self._cleanup_browser()

async def test_mcp_server():
    """测试MCP服务器功能"""
    server = TestDouyinMCPServer()
    
    print("=== 开始测试MCP服务器模拟 ===")
    result = await server.search_douyin_videos("猫", scroll_count=2, delay=2)
    print("\n=== 测试结果 ===")
    print(result)
    
    print("\n=== 详细数据 ===")
    for i, video in enumerate(server.collected_data['videos'][:3]):
        print(f"{i+1}. 标题: {video.get('title', 'N/A')}")
        print(f"   作者: {video.get('author', 'N/A')}")
        print(f"   点赞: {video.get('likes', 'N/A')}")
        print(f"   链接: {video.get('video_link', 'N/A')[:50]}...")
        print()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())