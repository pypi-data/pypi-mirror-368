import asyncio
from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
import time

def extract_video_items(html):
    """提取视频数据"""
    video_data = []
    
    try:
        # 查找视频项目 - 更新为新的页面结构
        video_items = html.select('li.SwZLHMKk')
        print(f"找到 {len(video_items)} 个视频项目")
        
        for item in video_items:
            try:
                data = {
                    'title': '',
                    'author': '',
                    'video_link': '',
                    'publish_time': '',
                    'likes': '0',
                    'comments': '0',
                    'shares': '0'
                }
                
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
                
                # 查找点赞数 - 新的选择器
                likes_elem = item.select_one('span.cIiU4Muu')
                if likes_elem:
                    likes_text = likes_elem.get_text(strip=True)
                    data['likes'] = likes_text
                
                # 提取描述信息
                desc_elem = item.select_one('div.VDYK8Xd7')
                if desc_elem:
                    data['description'] = desc_elem.get_text(strip=True)
                else:
                    data['description'] = ''
                
                if data['title']:  # 只添加有标题的数据
                    video_data.append(data)
                    
            except Exception as e:
                print(f"提取单个视频数据失败: {e}")
                continue
    
    except Exception as e:
        print(f"提取视频数据失败: {e}")
    
    return video_data

def test_video_search():
    """测试更新后的视频搜索功能"""
    page = ChromiumPage()
    
    try:
        print("开始测试视频搜索...")
        
        # 访问抖音搜索页面
        url = "https://www.douyin.com/search/测试?type=video"
        print(f"访问页面: {url}")
        page.get(url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 滚动页面
        print("滚动页面...")
        for i in range(2):
            page.scroll.down(3)
            time.sleep(2)
        
        # 获取页面源码并解析
        page_source = page.html
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 提取视频数据
        video_data = extract_video_items(soup)
        
        print(f"\n=== 搜索结果 ===")
        print(f"成功采集到 {len(video_data)} 条视频数据")
        
        # 显示前几条数据
        if video_data:
            print("\n前5条视频数据:")
            for i, video in enumerate(video_data[:5]):
                print(f"{i+1}. 标题: {video.get('title', 'N/A')}")
                print(f"   作者: {video.get('author', 'N/A')}")
                print(f"   点赞: {video.get('likes', 'N/A')}")
                print(f"   链接: {video.get('video_link', 'N/A')[:50]}...")
                print()
        else:
            print("未采集到任何数据")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        page.quit()

if __name__ == "__main__":
    test_video_search()