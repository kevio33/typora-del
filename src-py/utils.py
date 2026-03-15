"""
Typora-Del 工具函数模块
提供图片路径提取、文件扫描、删除等公共功能
支持路径智能识别功能
"""

import re
import os
from pathlib import Path
from typing import Set, Dict, List, Tuple, Optional


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.webp', '.gif', '.svg', '.tiff'}

IMAGE_PATTERN = re.compile(
    r'(!\[([^\]]*)\]\(([^)]+)\))|'
    r'(<img\s+[^>]*?>)',
    re.IGNORECASE | re.DOTALL
)

IMG_SRC_PATTERN = re.compile(
    r'src=["\']([^"\']+)["\']',
    re.IGNORECASE
)


def identify_path_type(path: str) -> str:
    """
    智能识别路径类型
    
    Args:
        path: 要识别的路径
    
    Returns:
        'file' - 如果是.md 文件
        'directory' - 如果是目录
    
    Raises:
        FileNotFoundError - 如果路径不存在
        ValueError - 如果路径不是.md 文件也不是目录
    """
    if not path:
        raise FileNotFoundError("路径不能为空")
    
    path_obj = Path(path)
    
    if not path_obj.exists():
        raise FileNotFoundError(f"路径不存在：{path}")
    
    if path_obj.is_file():
        if path_obj.suffix.lower() == '.md':
            return 'file'
        else:
            raise ValueError(f"不支持的文件类型：{path_obj.suffix}，仅支持.md 文件")
    
    if path_obj.is_dir():
        return 'directory'
    
    raise ValueError(f"无法识别的路径类型：{path}")


def get_md_files_from_path(path: str) -> List[Path]:
    """
    根据路径类型返回 MD 文件列表
    
    Args:
        path: 路径（可以是.md 文件或目录）
    
    Returns:
        MD 文件路径列表
    
    Raises:
        FileNotFoundError - 如果路径不存在
        ValueError - 如果路径不是.md 文件也不是目录
    """
    path_type = identify_path_type(path)
    path_obj = Path(path)
    
    if path_type == 'file':
        return [path_obj]
    
    elif path_type == 'directory':
        md_files = []
        for item in path_obj.rglob('*.md'):
            if item.is_file():
                md_files.append(item)
        return md_files
    
    return []


def extract_filename_from_path(path: str) -> str:
    """
    从路径中提取文件名，支持 Windows 和 Unix 路径
    
    Args:
        path: 图片路径（可能是 Windows 路径、Unix 路径、相对路径等）
    
    Returns:
        文件名
    """
    if not path:
        return ""
    
    path = path.replace('\\', '/')
    
    if path.startswith('./'):
        path = path[2:]
    
    if path.startswith('../'):
        parts = path.split('/')
        path = parts[-1] if parts else path
    
    last_slash = path.rfind('/')
    if last_slash >= 0 and last_slash < len(path) - 1:
        path = path[last_slash + 1:]
    
    return path


def extract_image_paths(content: str) -> Set[str]:
    """
    从 Markdown 内容中提取所有图片文件名
    
    Args:
        content: Markdown 文件内容
    
    Returns:
        图片文件名集合（小写）
    """
    image_files = set()
    
    for match in IMAGE_PATTERN.finditer(content):
        full_match = match.group(0)
        
        if full_match.startswith('!'):
            start_paren = full_match.find('(')
            end_paren = full_match.rfind(')')
            
            if start_paren != -1 and end_paren != -1 and end_paren > start_paren:
                path = full_match[start_paren + 1:end_paren].strip()
                
                if ' ' in path:
                    space_index = path.find(' ')
                    if space_index > 0:
                        potential_path = path[:space_index]
                        if potential_path.endswith('"') or potential_path.endswith("'"):
                            path = potential_path
                
                filename = extract_filename_from_path(path)
                if filename:
                    image_files.add(filename.lower())
        
        elif full_match.lower().startswith('<img'):
            src_match = IMG_SRC_PATTERN.search(full_match)
            if src_match:
                path = src_match.group(1)
                filename = extract_filename_from_path(path)
                if filename:
                    image_files.add(filename.lower())
    
    return image_files


def get_image_files(directory: Path) -> Dict[str, Path]:
    """
    扫描目录中的所有图片文件
    
    Args:
        directory: 要扫描的目录
    
    Returns:
        {小写文件名：完整路径} 的映射
    """
    images = {}
    
    if not directory.exists() or not directory.is_dir():
        return images
    
    try:
        for file in directory.iterdir():
            if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
                images[file.name.lower()] = file
    except PermissionError:
        print(f"警告：无法访问目录 {directory}")
    
    return images


def delete_unused_images(used_images: Set[str], image_files: Dict[str, Path]) -> Tuple[int, List[str]]:
    """
    删除未使用的图片文件
    
    Args:
        used_images: 正在使用的图片文件名集合（小写）
        image_files: 目录中所有图片文件的映射
    
    Returns:
        (删除的文件数量，删除的文件路径列表)
    """
    deleted_count = 0
    deleted_files = []
    
    for filename_lower, file_path in image_files.items():
        if filename_lower not in used_images:
            try:
                file_path.unlink()
                deleted_count += 1
                deleted_files.append(str(file_path))
                print(f"删除图片：{file_path}")
            except Exception as e:
                print(f"删除失败：{file_path} - {e}")
    
    return deleted_count, deleted_files


def clean_assets(md_file_path: Path, assets_dir: Path = None) -> Tuple[bool, int, str]:
    """
    清理 Markdown 文件的冗余图片
    
    Args:
        md_file_path: Markdown 文件路径
        assets_dir: 图片目录（可选，默认为 [文件名].assets）
    
    Returns:
        (是否成功，删除的文件数量，消息)
    """
    try:
        if not md_file_path.exists():
            return False, 0, f"Markdown 文件不存在：{md_file_path}"
        
        if not assets_dir:
            assets_dir = Path(md_file_path.parent) / f"{md_file_path.stem}.assets"
        
        if not assets_dir.exists() or not assets_dir.is_dir():
            return False, 0, f"图片目录不存在：{assets_dir}"
        
        print(f"文件路径：{md_file_path}")
        print(f"图片目录：{assets_dir}")
        
        content = md_file_path.read_text(encoding='utf-8')
        
        used_images = extract_image_paths(content)
        print(f"Markdown 中一共有：{len(used_images)}个图片文件")
        
        image_files = get_image_files(assets_dir)
        print(f"图片目录下一共有：{len(image_files)}个图片文件")
        
        deleted_count, _ = delete_unused_images(used_images, image_files)
        
        print(f"操作完成，共删除了{deleted_count}个图片文件！")
        return True, deleted_count, f"成功删除 {deleted_count} 个文件"
    
    except Exception as e:
        return False, 0, f"处理失败：{e}"
