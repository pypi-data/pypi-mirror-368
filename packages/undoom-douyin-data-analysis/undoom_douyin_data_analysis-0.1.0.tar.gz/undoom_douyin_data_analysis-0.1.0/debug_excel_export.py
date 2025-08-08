import pandas as pd
import traceback
from datetime import datetime

# 模拟视频数据
test_data = [
    {
        "title": "测试视频1",
        "author": "测试作者1",
        "likes": "1.2万",
        "comments": "500",
        "shares": "100"
    }
]

print(f"pandas版本: {pd.__version__}")

# 测试不同的Excel导出方式
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 方式1: 直接指定engine
try:
    filename1 = f"test1_{timestamp}.xlsx"
    df = pd.DataFrame(test_data)
    df.to_excel(filename1, index=False, engine='openpyxl')
    print(f"方式1成功: {filename1}")
except Exception as e:
    print(f"方式1失败: {e}")
    traceback.print_exc()

# 方式2: 使用ExcelWriter
try:
    filename2 = f"test2_{timestamp}.xlsx"
    df = pd.DataFrame(test_data)
    with pd.ExcelWriter(filename2, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    print(f"方式2成功: {filename2}")
except Exception as e:
    print(f"方式2失败: {e}")
    traceback.print_exc()

# 方式3: 检查可用的引擎
try:
    print("\n可用的Excel引擎:")
    from pandas.io.excel._base import get_writer
    engines = ['openpyxl', 'xlsxwriter', 'xlwt']
    for engine in engines:
        try:
            get_writer(engine)
            print(f"  {engine}: 可用")
        except Exception as e:
            print(f"  {engine}: 不可用 - {e}")
except Exception as e:
    print(f"检查引擎失败: {e}")