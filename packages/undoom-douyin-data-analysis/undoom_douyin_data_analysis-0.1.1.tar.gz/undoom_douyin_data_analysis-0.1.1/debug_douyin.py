from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
import time

def debug_selectors():
    """调试新的选择器"""
    page = ChromiumPage()
    
    try:
        # 访问抖音搜索页面
        url = "https://www.douyin.com/search/测试?type=video"
        print(f"访问页面: {url}")
        page.get(url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 滚动页面以加载更多内容
        print("滚动页面...")
        for i in range(3):
            page.scroll.down(3)
            time.sleep(1)
        
        # 获取页面源码
        html_content = page.html
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 测试新的选择器
        print("\n=== 测试新的选择器 ===")
        
        # 1. 查找视频项目
        video_items = soup.select('li.SwZLHMKk')
        print(f"找到 {len(video_items)} 个 li.SwZLHMKk 元素")
        
        if len(video_items) == 0:
            # 如果没找到，尝试其他可能的选择器
            print("\n尝试其他选择器...")
            
            # 查找所有li元素
            all_li = soup.select('li')
            print(f"找到 {len(all_li)} 个 li 元素")
            
            # 查找前几个li元素的class
            for i, li in enumerate(all_li[:5]):
                classes = li.get('class', [])
                print(f"li[{i}] classes: {classes}")
                
                # 查看内容
                if classes:
                    title_elem = li.select_one('div.VDYK8Xd7')
                    if title_elem:
                        print(f"  - 找到标题: {title_elem.get_text(strip=True)[:50]}...")
                    
                    author_elem = li.select_one('span.MZNczJmS')
                    if author_elem:
                        print(f"  - 找到作者: {author_elem.get_text(strip=True)}")
                    
                    likes_elem = li.select_one('span.cIiU4Muu')
                    if likes_elem:
                        print(f"  - 找到点赞: {likes_elem.get_text(strip=True)}")
        
        else:
            # 如果找到了，测试数据提取
            print(f"\n测试前3个视频项目的数据提取:")
            for i, item in enumerate(video_items[:3]):
                print(f"\n--- 视频 {i+1} ---")
                
                # 测试标题
                title_elem = item.select_one('div.VDYK8Xd7')
                if title_elem:
                    print(f"标题: {title_elem.get_text(strip=True)}")
                else:
                    print("未找到标题")
                
                # 测试作者
                author_elem = item.select_one('span.MZNczJmS')
                if author_elem:
                    print(f"作者: {author_elem.get_text(strip=True)}")
                else:
                    print("未找到作者")
                
                # 测试点赞数
                likes_elem = item.select_one('span.cIiU4Muu')
                if likes_elem:
                    print(f"点赞: {likes_elem.get_text(strip=True)}")
                else:
                    print("未找到点赞数")
                
                # 测试链接
                link_elem = item.select_one('a.hY8lWHgA')
                if link_elem:
                    href = link_elem.get('href', '')
                    print(f"链接: {href[:50]}...")
                else:
                    print("未找到链接")
        
        # 保存当前页面内容用于进一步分析
        with open('current_page_debug.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print("\n页面内容已保存到 current_page_debug.html")
        
    except Exception as e:
        print(f"调试过程中出错: {e}")
    
    finally:
        page.quit()

if __name__ == "__main__":
    debug_selectors()