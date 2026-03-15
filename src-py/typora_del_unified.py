"""
Typora-Del 统一入口版本（唯一入口）
整合所有增强功能的 Typora Markdown 冗余图片清理工具

功能特性：
- 智能路径识别：自动判断输入是文件还是目录
- 统计预览：处理前显示详细统计信息
- 用户确认：处理前询问用户确认
- 进度条显示：使用 tqdm 显示处理进度
- 彩色输出：使用 colorama 显示成功/警告/错误信息
- 日志系统：记录所有操作到 log 目录
- 详细报告：显示处理文件列表、删除统计、跳过的文件等

使用方式：
1. 命令行参数：python typora_del_unified.py <path>
2. 交互模式：python typora_del_unified.py（提示输入路径）
3. 拖拽文件：交互模式下拖拽文件到命令行

注意：这是推荐的唯一入口文件，其他入口文件（typora_del.py, typora_del_multi.py）
      仅为向后兼容保留，建议使用 typora_del_unified.py
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

from colorama import init, Fore, Style
from tqdm import tqdm

from logger import (
    setup_logger,
    log_operation_start,
    log_operation_end,
    log_input_path,
    log_processing_detail,
    log_deleted_files,
    log_statistics
)
from utils import (
    identify_path_type,
    get_md_files_from_path,
    clean_assets,
    extract_image_paths,
    IMAGE_EXTENSIONS
)


init(autoreset=True)


class TyporaDelUnified:
    """Typora-Del 统一入口类"""
    
    def __init__(self):
        self.logger = None
        self.start_time = None
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'skipped_files': 0,
            'total_deleted': 0,
            'errors': 0
        }
        self.processed_files_list = []
        self.skipped_files_list = []
        self.deleted_files_details = []
        self.errors_list = []
    
    def setup(self, input_path: str) -> None:
        """初始化日志系统"""
        self.logger = setup_logger()
        self.start_time = time.time()
        
        log_operation_start("Typora-Del 统一版本")
        log_input_path(input_path, "输入路径")
    
    def print_colored(self, message: str, color: str = Fore.WHITE) -> None:
        """彩色输出"""
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def print_success(self, message: str) -> None:
        """成功信息"""
        self.print_colored(f"✓ {message}", Fore.GREEN)
    
    def print_warning(self, message: str) -> None:
        """警告信息"""
        self.print_colored(f"⚠ {message}", Fore.YELLOW)
    
    def print_error(self, message: str) -> None:
        """错误信息"""
        self.print_colored(f"✗ {message}", Fore.RED)
    
    def print_info(self, message: str) -> None:
        """普通信息"""
        self.print_colored(message, Fore.CYAN)
    
    def process_single_file(self, md_file: Path) -> Tuple[bool, int]:
        """
        处理单个 Markdown 文件
        
        Args:
            md_file: Markdown 文件路径
        
        Returns:
            (是否成功，删除的文件数量)
        """
        try:
            success, deleted_count, message = clean_assets(md_file)
            
            if success:
                self.stats['total_deleted'] += deleted_count
                if deleted_count > 0:
                    self.deleted_files_details.append({
                        'file': str(md_file),
                        'deleted_count': deleted_count
                    })
                self.stats['processed_files'] += 1
                self.processed_files_list.append(str(md_file))
            else:
                self.stats['skipped_files'] += 1
                self.skipped_files_list.append({
                    'file': str(md_file),
                    'reason': message
                })
                self.errors_list.append(f"跳过 {md_file.name}: {message}")
            
            return success, deleted_count
        
        except Exception as e:
            self.stats['errors'] += 1
            error_msg = f"处理 {md_file} 时出错：{e}"
            self.errors_list.append(error_msg)
            self.print_error(error_msg)
            return False, 0
    
    def scan_and_preview(self, md_files: List[Path]) -> Dict:
        """
        扫描并显示统计预览信息（增强版：只显示需要处理的文件）
        
        Args:
            md_files: Markdown 文件列表
        
        Returns:
            统计信息字典
        """
        preview_stats = {
            'total_md_files': len(md_files),
            'files_need_process': 0,
            'files_no_need_process': 0,
            'total_images_to_delete': 0,
            'files_list': []
        }
        
        self.print_info("正在扫描文件...")
        print()
        
        for md_file in md_files:
            assets_dir = md_file.parent / f"{md_file.stem}.assets"
            has_assets = assets_dir.exists() and assets_dir.is_dir()
            
            if not has_assets:
                preview_stats['files_no_need_process'] += 1
                continue
            
            try:
                all_images = [
                    f.name for f in assets_dir.iterdir()
                    if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
                ]
                
                content = md_file.read_text(encoding='utf-8')
                used_images = extract_image_paths(content)
                
                unused_images = [
                    img for img in all_images
                    if img.lower() not in used_images
                ]
                
                if unused_images:
                    file_info = {
                        'file': md_file,
                        'assets_dir_name': f"{md_file.stem}.assets",
                        'unused_images': unused_images,
                        'delete_count': len(unused_images)
                    }
                    preview_stats['files_list'].append(file_info)
                    preview_stats['files_need_process'] += 1
                    preview_stats['total_images_to_delete'] += len(unused_images)
                else:
                    preview_stats['files_no_need_process'] += 1
                    
            except Exception as e:
                self.print_warning(f"读取 {md_file.name} 失败：{e}")
                preview_stats['files_no_need_process'] += 1
        
        return preview_stats
    
    def print_preview(self, preview_stats: Dict) -> None:
        """打印统计预览信息（增强版：只显示需要处理的文件）"""
        self.print_colored("=" * 70, Fore.CYAN)
        self.print_colored("扫描统计预览", Fore.CYAN)
        self.print_colored("=" * 70, Fore.CYAN)
        print()
        
        self.print_colored(f"📊 发现 {preview_stats['total_md_files']} 个 Markdown 文件", Fore.CYAN)
        self.print_colored(f"   需要处理：{preview_stats['files_need_process']} 个文件", Fore.GREEN)
        self.print_colored(f"   已过滤：{preview_stats['files_no_need_process']} 个文件（无需删除）", Fore.YELLOW)
        print()
        
        if preview_stats['files_need_process'] == 0:
            self.print_success("所有文件都无需处理，没有待删除的图片")
            print()
            self.print_colored("=" * 70, Fore.CYAN)
            print()
            return
        
        self.print_colored(f"� 需要处理的文件 ({preview_stats['files_need_process']} 个):", Fore.CYAN)
        print()
        
        for i, item in enumerate(preview_stats['files_list'], 1):
            file_name = Path(item['file']).name
            
            self.print_colored(f"  {i}. ✓ {file_name}", Fore.GREEN)
            self.print_colored(f"     📁 assets 目录：{item['assets_dir_name']}", Fore.CYAN)
            self.print_colored(f"     🗑️ 待删除：{item['delete_count']} 个图片", Fore.RED)
            
            for img in item['unused_images']:
                self.print_colored(f"       - {img}", Fore.RED)
            
            print()
        
        self.print_colored("汇总统计:", Fore.CYAN)
        self.print_colored(
            f"  - 需要处理的文件：{preview_stats['files_need_process']} 个", 
            Fore.GREEN
        )
        self.print_colored(
            f"  - 待删除图片：{preview_stats['total_images_to_delete']} 个", 
            Fore.RED
        )
        print()
        
        self.print_colored("=" * 70, Fore.CYAN)
        print()
    
    def ask_confirmation(self) -> bool:
        """
        询问用户是否确认处理
        
        Returns:
            用户是否确认（True/False）
        """
        while True:
            choice = input(f"{Fore.CYAN}是否处理以上文件？(y/n): {Style.RESET_ALL}").strip().lower()
            
            if choice == 'y':
                return True
            elif choice == 'n':
                self.print_info("已取消操作")
                return False
            else:
                self.print_warning("请输入 y 或 n")
    
    def process_directory(self, md_files: List[Path]) -> None:
        """
        批量处理多个 Markdown 文件
        
        Args:
            md_files: Markdown 文件列表
        """
        self.stats['total_files'] = len(md_files)
        
        if not md_files:
            self.print_warning("未找到任何 Markdown 文件")
            return
        
        with tqdm(md_files, desc="处理进度", unit="文件", colour='green') as pbar:
            for md_file in pbar:
                pbar.set_postfix_str(md_file.name[:30])
                
                success, deleted_count = self.process_single_file(md_file)
                
                if success and deleted_count > 0:
                    pbar.write(f"{Fore.GREEN}✓ {md_file.name}: 删除 {deleted_count} 个文件{Style.RESET_ALL}")
                elif success:
                    pbar.write(f"{Fore.YELLOW}⚠ {md_file.name}: 无需删除{Style.RESET_ALL}")
                else:
                    pbar.write(f"{Fore.RED}✗ {md_file.name}: 处理失败{Style.RESET_ALL}")
        
        print()
    
    def print_report(self) -> None:
        """打印详细的操作报告"""
        duration = time.time() - self.start_time
        
        print()
        self.print_colored("=" * 70, Fore.CYAN)
        self.print_colored("操作报告", Fore.CYAN)
        self.print_colored("=" * 70, Fore.CYAN)
        print()
        
        self.print_colored("📊 统计信息:", Fore.CYAN)
        self.print_colored(f"  总文件数：    {self.stats['total_files']}", Fore.WHITE)
        self.print_colored(f"  处理成功：    {self.stats['processed_files']}", Fore.GREEN)
        self.print_colored(f"  跳过文件：    {self.stats['skipped_files']}", Fore.YELLOW)
        self.print_colored(f"  删除图片：    {self.stats['total_deleted']}", Fore.GREEN)
        self.print_colored(f"  错误数量：    {self.stats['errors']}", Fore.RED)
        self.print_colored(f"  总耗时：      {duration:.2f} 秒", Fore.CYAN)
        print()
        
        if self.processed_files_list:
            self.print_colored("📝 处理的文件列表:", Fore.GREEN)
            for i, file_path in enumerate(self.processed_files_list, 1):
                deleted_info = ""
                for detail in self.deleted_files_details:
                    if detail['file'] == file_path:
                        deleted_info = f" (删除 {detail['deleted_count']} 个图片)"
                        break
                self.print_colored(f"  {i}. {file_path}{deleted_info}", Fore.WHITE)
            print()
        
        if self.skipped_files_list:
            self.print_colored("⚠ 跳过的文件:", Fore.YELLOW)
            for item in self.skipped_files_list:
                self.print_colored(f"  - {Path(item['file']).name}: {item['reason']}", Fore.YELLOW)
            print()
        
        if self.errors_list:
            self.print_colored("✗ 错误信息:", Fore.RED)
            for error in self.errors_list:
                self.print_colored(f"  - {error}", Fore.RED)
            print()
        
        if self.deleted_files_details:
            self.print_colored("🗑️ 删除详情:", Fore.GREEN)
            for detail in self.deleted_files_details:
                self.print_colored(f"  - {Path(detail['file']).name}: 删除 {detail['deleted_count']} 个图片", Fore.GREEN)
            print()
        
        self.print_colored("=" * 70, Fore.CYAN)
        
        log_statistics(self.stats)
        log_operation_end("Typora-Del 统一版本", duration)
        
        self.print_success(f"处理完成！日志已保存到 log 目录")
    
    def run(self, input_path: str) -> None:
        """
        主运行流程（带预览和确认）
        
        Args:
            input_path: 输入路径（文件或目录）
        """
        try:
            self.setup(input_path)
            
            self.print_colored("╔" + "═" * 68 + "╗", Fore.CYAN)
            self.print_colored("║" + " " * 20 + "Typora-Del 统一版本" + " " * 25 + "║", Fore.CYAN)
            self.print_colored("║" + " " * 15 + "Markdown 冗余图片清理工具" + " " * 24 + "║", Fore.CYAN)
            self.print_colored("╚" + "═" * 68 + "╝", Fore.CYAN)
            print()
            
            path_type = identify_path_type(input_path)
            
            if path_type == 'file':
                self.print_info(f"检测到输入是文件：{input_path}")
                md_files = [Path(input_path)]
            else:
                self.print_info(f"检测到输入是目录：{input_path}")
                md_files = get_md_files_from_path(input_path)
            
            print()
            
            # 扫描并显示预览
            preview_stats = self.scan_and_preview(md_files)
            self.print_preview(preview_stats)
            
            # 询问确认
            if not self.ask_confirmation():
                return
            
            print()
            self.print_info("开始处理...")
            print()
            
            # 处理文件
            self.process_directory(md_files)
            self.print_report()
            
        except FileNotFoundError as e:
            self.print_error(str(e))
            self.print_info("请检查路径是否正确")
        
        except ValueError as e:
            self.print_error(str(e))
            self.print_info("请确保输入的是 .md 文件或包含 .md 文件的目录")
        
        except KeyboardInterrupt:
            print()
            self.print_warning("程序已中断")
            if self.start_time:
                duration = time.time() - self.start_time
                log_operation_end("Typora-Del 统一版本 (中断)", duration)
        
        except Exception as e:
            self.print_error(f"发生未知错误：{e}")
            if self.logger:
                self.logger.exception("未知错误")
            import traceback
            traceback.print_exc()


def get_path_from_input(prompt: str) -> str:
    """
    获取用户输入的路径，支持拖拽
    
    Args:
        prompt: 提示语
    
    Returns:
        清理后的路径字符串
    """
    try:
        path = input(prompt).strip()
        
        if not path:
            return ""
        
        path = path.strip('"').strip("'")
        
        if path.startswith("file:///"):
            path = path[8:]
        
        return path
    
    except EOFError:
        return ""


def print_usage():
    """打印使用说明"""
    print()
    print(f"{Fore.CYAN}使用说明:{Style.RESET_ALL}")
    print(f"  1. 命令行参数：python typora_del_unified.py <路径>")
    print(f"  2. 交互模式：python typora_del_unified.py")
    print(f"  3. 拖拽文件：运行后拖拽文件或目录到命令行窗口")
    print()


def main():
    """主函数"""
    app = TyporaDelUnified()
    
    if len(sys.argv) > 1:
        input_path = " ".join(sys.argv[1:])
        input_path = input_path.strip('"').strip("'")
        
        if not input_path:
            app.print_error("路径不能为空")
            print_usage()
            return
        
        app.run(input_path)
    
    else:
        print()
        app.print_colored("╔" + "═" * 68 + "╗", Fore.CYAN)
        app.print_colored("║" + " " * 20 + "欢迎使用 Typora-Del" + " " * 25 + "║", Fore.CYAN)
        app.print_colored("╚" + "═" * 68 + "╝", Fore.CYAN)
        print()
        
        print_usage()
        
        while True:
            path = get_path_from_input(f"{Fore.CYAN}请输入路径 (输入 q 退出): {Style.RESET_ALL}")
            
            if path.lower() == 'q':
                app.print_info("程序退出")
                break
            
            if not path:
                app.print_error("路径不能为空，请重新输入")
                continue
            
            app.run(path)
            
            print()
            continue_choice = input(f"{Fore.CYAN}是否继续处理其他文件？(y/n): {Style.RESET_ALL}").strip().lower()
            if continue_choice != 'y':
                app.print_info("程序退出")
                break
            print()


if __name__ == "__main__":
    main()
