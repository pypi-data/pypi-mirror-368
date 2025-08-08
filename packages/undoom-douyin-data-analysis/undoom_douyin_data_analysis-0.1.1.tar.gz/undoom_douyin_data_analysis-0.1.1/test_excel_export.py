import pandas as pd
import json
from datetime import datetime

# 模拟视频数据
test_data = [
    {
        "title": "测试视频1",
        "author": "测试作者1",
        "likes": "1.2万",
        "comments": "500",
        "shares": "100"
    },
    {
        "title": "测试视频2",
        "author": "测试作者2",
        "likes": "5000",
        "comments": "200",
        "shares": "50"
    }
]

# 测试Excel导出
try:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_excel_export_{timestamp}.xlsx"
    
    # 使用openpyxl引擎导出Excel
    df = pd.DataFrame(test_data)
    df.to_excel(filename, index=False, engine='openpyxl')
    
    print(f"Excel导出成功: {filename}")
    print(f"导出了 {len(test_data)} 条数据")
    
except Exception as e:
    print(f"Excel导出失败: {e}")
    import traceback
    traceback.print_exc()