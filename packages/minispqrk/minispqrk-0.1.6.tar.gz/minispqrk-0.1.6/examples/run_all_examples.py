"""
运行所有示例
"""

import os
import sys
import subprocess
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_example(example_name, example_path):
    """运行单个示例"""
    print(f"\n{'='*50}")
    print(f"运行 {example_name} 示例")
    print(f"{'='*50}")
    
    try:
        # 切换到示例目录并运行
        example_dir = os.path.dirname(example_path)
        example_file = os.path.basename(example_path)
        
        # 使用subprocess运行示例
        result = subprocess.run(
            [sys.executable, example_file],
            cwd=example_dir,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        if result.returncode == 0:
            print(f"✓ {example_name} 示例运行成功")
            # 只打印关键输出，避免日志过多
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '成功' in line or '完成' in line or '结果' in line or line.startswith('===') or '✓' in line or '🎉' in line or '❌' in line:
                    print(f"  {line}")
        else:
            print(f"✗ {example_name} 示例运行失败")
            print(f"  错误信息: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ {example_name} 示例运行超时")
        return False
    except Exception as e:
        print(f"✗ {example_name} 示例运行出错: {e}")
        return False
    
    return True

def main():
    """主函数"""
    print("开始运行所有示例...")
    
    # 获取所有示例目录
    examples_dir = os.path.dirname(__file__)
    example_dirs = [d for d in os.listdir(examples_dir) 
                   if os.path.isdir(os.path.join(examples_dir, d)) and d != '__pycache__']
    
    # 成功和失败计数
    success_count = 0
    fail_count = 0
    
    # 特别处理MySQL示例（运行我们新创建的测试示例）
    if 'mysql' in example_dirs:
        print("\n注意: MySQL示例需要特殊配置才能运行")
        print("将运行专门的MySQL测试示例")
        # 从示例列表中移除mysql，单独处理
        example_dirs.remove('mysql')
        
        # 运行MySQL测试示例
        mysql_example_path = os.path.join(examples_dir, 'mysql', 'test_mysql_example.py')
        if run_example("MySQL", mysql_example_path):
            success_count += 1
        else:
            fail_count += 1
    
    # 运行其他示例
    for example_dir in example_dirs:
        example_path = os.path.join(examples_dir, example_dir, 'example.py')
        if os.path.exists(example_path):
            if run_example(example_dir.upper(), example_path):
                success_count += 1
            else:
                fail_count += 1
        else:
            print(f"\n警告: {example_dir} 示例文件不存在")
            fail_count += 1
    
    # 输出总结
    print(f"\n{'='*50}")
    print("示例运行总结")
    print(f"{'='*50}")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"总计: {success_count + fail_count}")
    
    if fail_count == 0:
        print("\n🎉 所有示例运行成功!")
    else:
        print(f"\n⚠️  有 {fail_count} 个示例运行失败")

if __name__ == "__main__":
    main()