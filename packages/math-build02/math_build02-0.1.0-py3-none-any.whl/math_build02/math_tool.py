import argparse

def new_numpy(a, b):
    """计算a + b的值"""
    return f"a + b = {a + b}"

def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="创建示例NumPy数组并保存为文本文件")
    parser.add_argument('--a', required=True, help="运算变量a")
    parser.add_argument('--b', required=True, help="运算变量b")
    
    args = parser.parse_args()
    
    # 调用核心功能
    result = new_numpy(args.a, args.b)
    print(result)

if __name__ == "__main__":
    main()