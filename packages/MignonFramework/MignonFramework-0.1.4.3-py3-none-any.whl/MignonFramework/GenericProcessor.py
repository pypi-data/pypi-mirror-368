"""
一个高度通用的文件到数据库ETL（提取、转换、加载）工具。它通过一个统一的 run() 方法，
可以智能处理单个文件或整个目录，支持“整文件JSON”和“逐行JSON”两种模式，并提供了断点续传、
可视化进度条和事件回调等高级功能。
"""
import json as std_json
import os
import ast
import sys
import io
import re
from abc import ABC, abstractmethod
from contextlib import redirect_stdout
from datetime import datetime
from typing import Dict, Callable, List, Optional, Any

from MignonFramework.MySQLManager import MysqlManager
from MignonFramework.CountLinesInFolder import count_lines_in_single_file
from MignonFramework.ConfigReader import ConfigManager
from MignonFramework.BaseWriter import BaseWriter


class Rename:
    """一个辅助类，在modifier_function中用于明确表示重命名操作。"""

    def __init__(self, new_key_name: str):
        self.new_key_name = new_key_name


class GenericFileProcessor:
    """
    一个通用的、可定制的JSON文件处理器，用于将文件内容批量写入指定目标。
    支持零配置启动，会自动引导用户创建配置文件。
    """

    def __init__(self,
                 writer: Optional[BaseWriter] = None,
                 table_name: Optional[str] = None,
                 mode: str = 'line',
                 modifier_function: Optional[Callable[[Dict], Dict]] = None,
                 filter_function: Optional[Callable[[Dict, int], bool]] = None,
                 exclude_keys: Optional[List[str]] = None,
                 default_values: Optional[Dict[str, Any]] = None,
                 batch_size: int = 1000,
                 callBack: Optional[Callable[[bool, List[Dict], str, Optional[int]], None]] = None,
                 print_mapping_table: bool = True,
                 on_error: str = 'stop'):
        """
        初始化处理器。

        Args:
            writer (BaseWriter, optional): 数据写入器实例。如果为None，将尝试从配置文件加载。
            table_name (str, optional): 目标表名。如果为None，将尝试从配置文件加载。
            mode (str): 文件处理模式。可选值为 'line' (默认) 或 'file'。
            modifier_function (Callable, optional): 自定义修改函数。
            filter_function (Callable[[Dict, int], bool], optional): 数据过滤函数，接收数据和行号，返回False则跳过。
            exclude_keys (List[str], optional): 需要排除的源JSON键列表。
            default_values (Dict[str, Any], optional): 为缺失或为None的键提供默认值。
            batch_size (int): 每批提交的记录数。
            callBack (Callable, optional): 批处理完成后的回调函数。
            print_mapping_table (bool): 是否在运行前打印字段映射对照表。
            on_error (str): 错误处理策略 ('continue', 'stop', 'log_to_file')。
        """
        self.is_ready = True
        self.config_manager = ConfigManager(filename='./resources/config/generic.ini', section='GenericProcessor')
        self.path_from_config = None
        self.test = False  # 初始化test属性

        # 优先使用代码中传入的 writer 和 table_name
        self.writer = writer
        self.table_name = table_name

        # 如果代码中未提供，则尝试从配置文件加载
        if self.writer is None or self.table_name is None:
            self._init_from_config()

        if not self.is_ready:
            return

        if not isinstance(self.writer, BaseWriter):
            raise TypeError("writer 必须是 BaseWriter 的一个实例。")
        if mode not in ['file', 'line']:
            raise ValueError("mode 参数必须是 'file' 或 'line'。")

        self.modifier_function = modifier_function
        self.filter_function = filter_function
        self.exclude_keys = set(exclude_keys) if exclude_keys else set()
        self.default_values = default_values if default_values else {}
        self.mode = mode
        self.batch_size = batch_size
        self.callBack = callBack
        self.print_mapping_table = print_mapping_table
        self.on_error = on_error

    def _init_from_config(self):
        """从配置文件初始化处理器。如果配置不完整，则引导用户创建。"""
        config_data = self.config_manager.get_all_fields()

        # 仅在代码未提供 writer 时才尝试从配置创建
        if self.writer is None:
            db_keys = ['host', 'user', 'password', 'database']
            if config_data and all(config_data.get(k) and 'YOUR_' not in str(config_data.get(k)) for k in db_keys):
                db_config = {k: config_data[k] for k in db_keys}
                self.writer = MysqlManager(**db_config)
                if not self.writer.is_connected():
                    print(f"[ERROR] 使用 generic.ini 中的配置连接数据库失败。")
                    self.is_ready = False
                    return
            else:
                self._guide_user_to_config()
                return

        # 仅在代码未提供 table_name 时才尝试从配置获取
        if self.table_name is None:
            if config_data and config_data.get('table_name') and 'YOUR_' not in str(config_data.get('table_name')):
                self.table_name = config_data['table_name']
            else:
                self._guide_user_to_config()
                return

        # 尝试获取路径作为备用
        if config_data and config_data.get('path') and 'YOUR_' not in str(config_data.get('path')):
            self.path_from_config = config_data['path']

    def _guide_user_to_config(self):
        """引导用户填写配置文件。"""
        print("\n" + "=" * 60)
        print("🚀 欢迎使用 GenericFileProcessor 零配置向导！")
        print("处理器检测到配置不完整，将为您创建或更新配置文件。")
        print(f"配置文件路径: {os.path.abspath('./resources/config/generic.ini')}")
        print("请在该文件中填写您的数据库信息和要处理的文件路径。")
        print("=" * 60 + "\n")

        placeholders = {
            'host': 'YOUR_DATABASE_HOST', 'user': 'YOUR_USERNAME', 'password': 'YOUR_PASSWORD',
            'database': 'YOUR_DATABASE_NAME', 'table_name': 'YOUR_TARGET_TABLE',
            'path': 'PATH_TO_YOUR_FILE_OR_DIRECTORY'
        }
        for key, value in placeholders.items():
            if not self.config_manager.get_field(key) or 'YOUR_' in str(self.config_manager.get_field(key)):
                self.config_manager.update_field(key, value)

        self.is_ready = False

    def _to_snake_case(self, name: str) -> str:
        if not isinstance(name, str) or not name:
            return ""
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _safe_json_load(self, text: str) -> Optional[Dict]:
        try:
            return std_json.loads(text)
        except std_json.JSONDecodeError:
            try:
                return ast.literal_eval(text)
            except (ValueError, SyntaxError, MemoryError, TypeError):
                return None

    def _finalize_types(self, data_dict: dict) -> dict:
        final_data = {}
        for key, value in data_dict.items():
            if value is None:
                final_data[key] = ''
            elif isinstance(value, (dict, list)):
                final_data[key] = std_json.dumps(value, ensure_ascii=False)
            else:
                final_data[key] = value
        return final_data

    def _process_single_item(self, json_data: dict, temp_exclude_keys=None, temp_default_values=None) -> Optional[Dict]:
        # 合并初始配置和临时配置
        current_excludes = self.exclude_keys.union(temp_exclude_keys or set())
        current_defaults = {**self.default_values, **(temp_default_values or {})}

        data_with_defaults = {}
        all_original_keys = set(json_data.keys()) | set(current_defaults.keys())
        for key in all_original_keys:
            value = json_data.get(key)
            if (value is None or value == '') and key in current_defaults:
                data_with_defaults[key] = current_defaults[key]
            else:
                data_with_defaults[key] = value

        parsed_data = {}
        for original_key, final_value in data_with_defaults.items():
            if original_key in current_excludes:
                continue
            new_key = self._to_snake_case(original_key)
            parsed_data[new_key] = final_value

        if self.modifier_function:
            patch_dict = self.modifier_function(data_with_defaults)
            for original_key, instruction in patch_dict.items():
                auto_key = self._to_snake_case(original_key)
                if isinstance(instruction, Rename):
                    if auto_key in parsed_data:
                        parsed_data[instruction.new_key_name] = parsed_data.pop(auto_key)
                elif isinstance(instruction, tuple) and len(instruction) == 2:
                    if auto_key in parsed_data:
                        del parsed_data[auto_key]
                    parsed_data[instruction[0]] = instruction[1]
                else:
                    parsed_data[auto_key] = instruction

        return self._finalize_types(parsed_data)

    def _execute_batch(self, json_list: List[Dict], filename: str, line_num: Optional[int] = None):
        if not json_list:
            return
        f = io.StringIO()
        status = False
        with redirect_stdout(f):
            status = self.writer.upsert_batch(json_list, self.table_name, test=self.test)
        captured_output = f.getvalue().strip()
        if self.callBack:
            try:
                self.callBack(status, json_list, filename, line_num)
            except Exception as cb_e:
                print(f"\n[ERROR] 回调函数执行失败: {cb_e}")
        if not status:
            raise Exception(f"数据写入失败。详细信息: {captured_output}")

    def _generate_and_print_mapping(self, sample_json: Dict[str, Any]):
        print("\n" + "=" * 102)
        print("--- 字段映射对照表 (Field Mapping Table) ---")
        col_widths = (30, 30, 30)
        header = "| {:{w1}} | {:{w2}} | {:{w3}} |".format(
            "源字段", "目标字段", "示例值/默认值", w1=col_widths[0], w2=col_widths[1], w3=col_widths[2]
        )
        print(header)
        print("-" * (sum(col_widths) + 7))

        sample_with_defaults = {}
        all_sample_keys = set(sample_json.keys()) | set(self.default_values.keys())
        for key in all_sample_keys:
            value = sample_json.get(key)
            if (value is None or value == '') and key in self.default_values:
                sample_with_defaults[key] = self.default_values[key]
            else:
                sample_with_defaults[key] = value

        patch = self.modifier_function(sample_with_defaults) if self.modifier_function else {}
        all_keys = sorted(list(set(sample_with_defaults.keys()) | set(patch.keys())))

        for key in all_keys:
            if key in self.exclude_keys:
                mapped_key, value_str = "SKIPPED", "N/A"
            else:
                instruction = patch.get(key)
                if isinstance(instruction, Rename):
                    mapped_key = instruction.new_key_name
                elif isinstance(instruction, tuple):
                    mapped_key = instruction[0]
                else:
                    mapped_key = self._to_snake_case(key)

                if instruction is not None:
                    if isinstance(instruction, tuple):
                        value_str = f"(mod) {instruction[1]}"
                    elif not isinstance(instruction, Rename):
                        value_str = f"(mod) {instruction}"
                    else:
                        value_str = str(sample_with_defaults.get(key, 'N/A'))
                elif key in sample_with_defaults and sample_with_defaults[key] is not None:
                    value_str = str(sample_with_defaults[key])
                else:
                    value_str = "N/A"

            value_str = (value_str[:25] + '...') if len(value_str) > 25 else value_str

            padding = [w - self._get_display_width(s) for w, s in zip(col_widths, [key, mapped_key, value_str])]
            print(f"| {key}{' ' * padding[0]} | {mapped_key}{' ' * padding[1]} | {value_str}{' ' * padding[2]} |")

        print("=" * 102 + "\n")

    def _get_display_width(self, s: str) -> int:
        return sum(2 if '\u4e00' <= char <= '\u9fff' else 1 for char in s)

    def _find_original_key(self, snake_key: str, sample_json: dict) -> Optional[str]:
        """根据snake_case键反查原始键。"""
        for key in sample_json.keys():
            if self._to_snake_case(key) == snake_key:
                return key
        return None

    def _run_test_mode(self, file_path: str):
        """执行测试模式，自动诊断并建议修复方案。"""
        print("\n--- 启动测试模式 ---")
        print(f"将使用文件 '{os.path.basename(file_path)}' 的第一批数据进行测试...")

        raw_json_batch = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(raw_json_batch) >= self.batch_size:
                        break
                    if line.strip():
                        if json_data := self._safe_json_load(line):
                            raw_json_batch.append(json_data)
        except Exception as e:
            print(f"[ERROR] 读取测试文件时失败: {e}")
            return

        if not raw_json_batch:
            print("[ERROR] 未能在文件中找到有效的JSON数据进行测试。")
            return

        suggested_excludes = set()
        suggested_defaults = {}
        error_counts = {}
        MAX_ATTEMPTS = 5

        for attempt in range(1, MAX_ATTEMPTS + 1):
            print(f"\n--- 第 {attempt} 次尝试 ---")
            try:
                processed_batch = [self._process_single_item(item, suggested_excludes, suggested_defaults) for item in
                                   raw_json_batch]
                processed_batch = [item for item in processed_batch if item is not None]

                self._execute_batch(processed_batch, os.path.basename(file_path))

                print("  [成功] 当前配置有效，测试通过！")
                break
            except Exception as e:
                error_code = e.args[0] if isinstance(e.args, tuple) and len(e.args) > 0 else 0
                error_message = str(e)

                if error_code == 1054:
                    match = re.search(r"Unknown column '(.+?)'", error_message)
                    if match:
                        col = match.group(1)
                        original_key = self._find_original_key(col, raw_json_batch[0])
                        if original_key:
                            print(f"  [诊断] 发现未知列 '{col}'，对应源字段 '{original_key}'。")
                            suggested_excludes.add(original_key)
                            print(f"  [操作] 将 '{original_key}' 加入建议排除列表。")
                            continue

                if error_code == 1292:
                    match = re.search(r"Incorrect date value: '.+?' for column '(.+?)'", error_message)
                    if match:
                        col = match.group(1)
                        original_key = self._find_original_key(col, raw_json_batch[0])
                        if original_key:
                            error_counts[original_key] = error_counts.get(original_key, 0) + 1
                            if error_counts[original_key] > 3:
                                print(f"  [失败] 字段 '{original_key}' 自动修复超过3次，测试中止。")
                                break
                            print(f"  [诊断] 发现无效日期值，列 '{col}'，对应源字段 '{original_key}'。")
                            suggested_defaults[original_key] = datetime.now()
                            print(f"  [操作] 为 '{original_key}' 加入建议的默认日期。")
                            continue

                print(f"  [失败] 遇到无法自动处理的错误，测试中止: {e}")
                break

        print("\n" + "=" * 60)
        print("--- 测试模式总结与配置建议 ---")
        if suggested_excludes:
            print("\n建议的 `exclude_keys` 列表:")
            print(f"exclude_keys = {list(suggested_excludes)}")
        else:
            print("\n未发现需要排除的字段。")

        if suggested_defaults:
            print("\n建议的 `default_values` 字典 (日期将是运行时的时间):")
            defaults_str = {k: str(v) for k, v in suggested_defaults.items()}
            print(f"default_values = {defaults_str}")
        else:
            print("\n未发现需要设置默认值的日期字段。")
        print("=" * 60 + "\n")

    def run(self, path: Optional[str] = None, start_line: int = 1, test: bool = False):
        if not self.is_ready:
            print("[INFO] 处理器尚未就绪，请根据提示完成配置后再次运行。")
            return

        self.test = test  # 将 test 状态保存到实例

        target_path = path if path is not None else self.path_from_config
        if not target_path or not os.path.exists(target_path):
            if path is None and self.path_from_config is None:
                self._guide_user_to_config()
            else:
                print(f"[ERROR] 目标路径无效或不存在: {target_path}")
            return

        files_to_process = [os.path.join(target_path, f) for f in os.listdir(target_path) if
                            os.path.isfile(os.path.join(target_path, f)) and f.lower().endswith(
                                ('.json', '.txt'))] if os.path.isdir(target_path) else [target_path]

        if not files_to_process:
            print(f"在路径 '{target_path}' 中未找到可处理的文件。")
            return

        if test:
            self._run_test_mode(files_to_process[0])
            return

        if self.print_mapping_table:
            try:
                composite_sample = {}
                lines_scanned = 0
                with open(files_to_process[0], 'r', encoding='utf-8') as f:
                    for line in f:
                        if lines_scanned >= 1000:
                            break
                        if line.strip():
                            if sample_data := self._safe_json_load(line):
                                composite_sample.update(sample_data)
                                lines_scanned += 1
                if composite_sample:
                    self._generate_and_print_mapping(composite_sample)
                else:
                    print("[WARNING] 未能在文件前1000行找到有效的JSON数据来生成对照表。")
            except Exception as e:
                print(f"[WARNING] 无法生成对照表: {e}")

        print(f"\n--- 开始处理路径: {target_path} (模式: {self.mode}) ---")
        print(f"发现 {len(files_to_process)} 个文件待处理...")

        for i, file_path in enumerate(files_to_process):
            filename, line_num = os.path.basename(file_path), 0
            print(f"\n[{i + 1}/{len(files_to_process)}] 正在处理: {filename}")

            try:
                if self.mode == 'file':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        if json_data := self._safe_json_load(content):
                            if not self.filter_function or self.filter_function(json_data, 1):
                                if parsed_dic := self._process_single_item(json_data):
                                    self._execute_batch([parsed_dic], filename)
                        else:
                            print(f"\n[WARNING] 无法解析文件内容: {filename}")

                elif self.mode == 'line':
                    if start_line > 1:
                        print(f"  [INFO] 从第 {start_line} 行开始处理...")
                    total_lines = count_lines_in_single_file(file_path) or 0
                    json_list = []
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if line_num < start_line or not line.strip():
                                continue

                            try:
                                json_data = self._safe_json_load(line)
                                if not json_data:
                                    raise ValueError("解析失败")
                                if self.filter_function and not self.filter_function(json_data, line_num):
                                    continue
                                if parsed_dic := self._process_single_item(json_data):
                                    json_list.append(parsed_dic)

                                if total_lines > 0:
                                    bar = '█' * int(40 * line_num / total_lines) + '-' * (
                                            40 - int(40 * line_num / total_lines))
                                    sys.stdout.write(
                                        f'\r|{bar}| {line_num / total_lines:.1%} ({line_num}/{total_lines})  本批: [{len(json_list)}/{self.batch_size}]')
                                    sys.stdout.flush()

                                if len(json_list) >= self.batch_size:
                                    self._execute_batch(json_list, filename, line_num)
                                    json_list = []
                            except Exception as parse_e:
                                error_msg = f"\n[WARNING] 处理文件 {filename} 第 {line_num} 行时发生错误: {parse_e}"
                                if self.on_error == 'stop':
                                    raise
                                if self.on_error == 'log_to_file':
                                    with open('error.log', 'a', encoding='utf-8') as err_f:
                                        err_f.write(
                                            f"{datetime.now()} | {filename} | Line {line_num} | {parse_e}\n{line}\n")
                                print(error_msg)
                                print(f"  [FAILING LINE]: {line.strip()}")
                    print()
                    self._execute_batch(json_list, filename, line_num)
                print(f"  [成功] 文件已处理。")
            except Exception as e:
                print(f"\n  [失败] 处理文件 {filename} 时发生致命错误: {e}。")
                continue
        print("\n--- 所有任务处理完成 ---")
