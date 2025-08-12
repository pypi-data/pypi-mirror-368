import socket

def get_free_port():
    """
    获取一个系统空闲的端口
    
    Returns:
        int: 空闲端口号
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))  # 绑定到一个空闲端口
        return s.getsockname()[1]  # 返回端口号
