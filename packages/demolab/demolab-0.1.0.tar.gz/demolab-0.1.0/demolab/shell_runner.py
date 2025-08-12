import subprocess

def run_shell_script(script_path, *args):
    """
    运行shell脚本并返回状态码和输出
    
    Args:
        script_path: 脚本路径
        *args: 传递给脚本的参数
        
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    try:
        # 构建命令
        command = ['sh', script_path] + list(args)
        
        # 执行命令
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, str(e), str(e)
