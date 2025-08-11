import argparse

def new_numpy02(a, b, c):
    """计算a - b + c的值"""
    return f"a - b + c = {a - b + c}"

def main():
    # 设置命令行参数解析器
    parser = argparse.ArgumentParser(description="计算三位数的结果")
    parser.add_argument('--a', required=True, help="运算变量a")
    parser.add_argument('--b', required=True, help="运算变量b")
    parser.add_argument('--c', required=True, help="运算变量c")
    
    args = parser.parse_args()
    
    # 调用核心功能
    result = new_numpy02(int(args.a), int(args.b), int(args.c))
    print(result)

if __name__ == "__main__":
    main()