import os
import pkgutil

def binary_to_gif(binary_str: str, output_path: str):
    """将二进制字符串转换为GIF文件"""
    data = bytes(
        int(binary_str[i:i+8], 2) 
        for i in range(0, len(binary_str), 8)
    )
    with open(output_path, 'wb') as f:
        f.write(data)

def get_binary_data(name: str) -> str:
    """根据配置名称获取预置的二进制数据"""
    config = {
        "魔丸4*4": "output_4x4.txt",
        "魔丸2*2": "output_2x2.txt",
        "魔丸1*1": "output_1x1.txt"
    }
    
    filename = config.get(name)
    if not filename:
        raise ValueError(f"未知名称: {name}，可用选项: {list(config.keys())}")
    
    # 从包内data目录读取二进制文件
    data = pkgutil.get_data('nezha2', filename)
    if data is None:
        raise FileNotFoundError(f"未找到内置数据文件: {filename}")
    
    return data.decode('utf-8').strip()

def restore_gif(name: str, output_path: str = None):
    """主接口：恢复指定名称的GIF文件"""
    if output_path is None:
        output_path = f"{name.replace('*', 'x')}.gif"
    
    binary_str = get_binary_data(name)
    binary_to_gif(binary_str, output_path)
    return os.path.abspath(output_path)