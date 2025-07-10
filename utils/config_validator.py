import os
import sys
from typing import Dict, Any
import app_conf

def validate_config() -> Dict[str, Any]:
    """
    验证配置文件的有效性
    返回验证结果字典
    """
    conf = app_conf.conf()
    issues = []
    warnings = []
    
    # 检查必需的配置项
    required_sections = {
        'server': ['port', 'host'],
        'user': ['username', 'password'],
        'database': ['path'],
        'file': ['inputdir', 'storedir', 'tmpdir'],
        'img': ['encode', 'miniSize', 'fullSize']
    }
    
    for section, keys in required_sections.items():
        if not conf.has_section(section):
            issues.append(f"缺少配置节: [{section}]")
            continue
        
        for key in keys:
            if not conf.has_option(section, key):
                issues.append(f"缺少配置项: [{section}].{key}")
    
    # 检查安全性问题
    if conf.has_section('user'):
        username = conf.get('user', 'username', fallback='')
        password = conf.get('user', 'password', fallback='')
        
        if username == 'admin' and password == 'admin':
            warnings.append("使用默认用户名和密码不安全，建议修改")
        
        if len(password) < 8:
            warnings.append("密码过于简单，建议使用8位以上的复杂密码")
    
    # 检查端口配置
    if conf.has_section('server'):
        try:
            port = conf.getint('server', 'port')
            if port < 1024 or port > 65535:
                warnings.append(f"端口号 {port} 可能不合适，建议使用1024-65535范围内的端口")
        except:
            issues.append("服务器端口配置无效")
    
    # 检查目录权限
    if conf.has_section('file'):
        directories = ['inputdir', 'storedir', 'tmpdir']
        for dir_key in directories:
            dir_path = conf.get('file', dir_key, fallback='')
            if dir_path:
                abs_path = os.path.abspath(dir_path)
                parent_dir = os.path.dirname(abs_path)
                
                if not os.path.exists(parent_dir):
                    issues.append(f"父目录不存在: {parent_dir} (配置: {dir_key})")
                elif not os.access(parent_dir, os.W_OK):
                    issues.append(f"没有写入权限: {parent_dir} (配置: {dir_key})")
    
    # 检查数据库路径
    if conf.has_section('database'):
        db_path = conf.get('database', 'path', fallback='')
        if db_path:
            db_dir = os.path.dirname(os.path.abspath(db_path))
            if not os.path.exists(db_dir):
                issues.append(f"数据库目录不存在: {db_dir}")
            elif not os.access(db_dir, os.W_OK):
                issues.append(f"数据库目录没有写入权限: {db_dir}")
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings
    }

def print_validation_results(results: Dict[str, Any]):
    """打印配置验证结果"""
    if results['valid']:
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
        print("\n严重问题:")
        for issue in results['issues']:
            print(f"  • {issue}")
    
    if results['warnings']:
        print("\n⚠️  警告:")
        for warning in results['warnings']:
            print(f"  • {warning}")

if __name__ == "__main__":
    # 当直接运行此文件时，执行配置验证
    results = validate_config()
    print_validation_results(results)
    
    if not results['valid']:
        sys.exit(1)
