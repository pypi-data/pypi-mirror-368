def extract_token_from_user_workspace_creation_log(log_file_path):
    """
    从用户工作空间创建日志中提取token
    
    Args:
        log_file_path: 日志文件路径
        
    Returns:
        str: 提取的token，如果未找到则返回None
    """
    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                # 假设token在类似"token: xxxxx"的行中
                if 'token:' in line:
                    return line.split('token:')[1].strip()
        return None
    except Exception as e:
        print(f"Error extracting token from log: {e}")
        return None
