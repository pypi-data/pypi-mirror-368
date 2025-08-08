#!/usr/bin/env python3

import pandas as pd
import traceback
from datetime import datetime

# 模拟MCP服务器中的Excel导出逻辑
def test_excel_export():
    try:
        # 模拟数据
        data_to_export = [
            {
                "title": "测试视频1",
                "author": "测试作者1",
                "likes": "1.2万",
                "comments": "500",
                "shares": "100"
            }
        ]
        
        # 生成文件名（模拟MCP服务器中的逻辑）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format = "excel"  # 这是传入的参数
        filename = "test_excel_debug"
        
        # 原始的文件扩展名逻辑
        file_extension = "xlsx" if format == "excel" else format
        full_filename = f"{filename}_{timestamp}.{file_extension}"
        
        print(f"格式: {format}")
        print(f"文件扩展名: {file_extension}")
        print(f"完整文件名: {full_filename}")
        
        # 测试Excel导出
        print("\n开始Excel导出测试...")
        df = pd.DataFrame(data_to_export)
        
        # 方式1: 直接使用to_excel
        try:
            df.to_excel(full_filename, index=False, engine='openpyxl')
            print(f"方式1成功: {full_filename}")
        except Exception as e:
            print(f"方式1失败: {e}")
            print(f"详细错误: {traceback.format_exc()}")
        
        # 方式2: 使用ExcelWriter
        try:
            full_filename2 = f"{filename}_{timestamp}_writer.{file_extension}"
            with pd.ExcelWriter(full_filename2, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            print(f"方式2成功: {full_filename2}")
        except Exception as e:
            print(f"方式2失败: {e}")
            print(f"详细错误: {traceback.format_exc()}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    print(f"pandas版本: {pd.__version__}")
    test_excel_export()