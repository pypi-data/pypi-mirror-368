from .算子运行器 import 为所有算子创建函数
import argparse

def 创建算子库():
    parser = argparse.ArgumentParser(
        description="为所有算子创建函数：生成算子代码并支持跳过自定义算子"
    )
    
    # 添加位置参数：目标目录（必填）
    parser.add_argument(
        "目标目录",
        type=str,
        help="指定生成算子的目标目录路径（例如：'./operators/'）"
    )
    
    # 添加可选布尔参数：跳过自定义算子（默认为False）
    parser.add_argument(
        "--跳过自定义算子",
        "-s",
        action="store_true",
        default=False,
        help="若启用，跳过自定义算子生成（默认不跳过）"
    )
    
    args = parser.parse_args()
    
    # 调用函数并传递解析后的参数
    为所有算子创建函数(
        目标目录=args.目标目录,
        跳过自定义算子=args.跳过自定义算子
    )