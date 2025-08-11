#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
from pathlib import Path
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional, Dict, Any

from loguru import logger

from .libmcp import extract_call_tool_str, extra_call_tool_blocks
from ..interface import Trackable

@dataclass
class CodeBlock:
    """代码块对象"""
    name: str
    version: int
    lang: str
    code: str
    path: Optional[str] = None
    deps: Optional[Dict[str, set]] = None

    def add_dep(self, dep_name: str, dep_value: Any):
        """添加依赖"""
        if self.deps is None:
            self.deps = {}
        if dep_name not in self.deps:
            deps = set()
            self.deps[dep_name] = deps
        else:
            deps = self.deps[dep_name]

        # dep_value 可以是单个值，或者一个可迭代对象
        if isinstance(dep_value, (list, set, tuple)):
            deps.update(dep_value)
        else:
            deps.add(dep_value)

    def save(self):
        """保存代码块到文件"""
        if not self.path:
            return False
            
        path = Path(self.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.code, encoding='utf-8')
        return True

    @property
    def abs_path(self):
        if self.path:
            return Path(self.path).absolute()
        return None
    
    def get_lang(self):
        lang = self.lang.lower()
        return lang
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            '__type__': 'CodeBlock',
            'name': self.name,
            'version': self.version,
            'lang': self.lang,
            'code': self.code,
            'path': self.path,
            'deps': self.deps
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CodeBlock':
        """从字典恢复对象"""
        return cls(
            name=data.get('name', ''),
            version=data.get('version', 1),
            lang=data.get('lang', ''),
            code=data.get('code', ''),
            path=data.get('path'),
            deps=data.get('deps')
        )

    def __repr__(self):
        return f"<CodeBlock name={self.name}, version={self.version}, lang={self.lang}, path={self.path}>"

class CodeBlocks(Trackable):
    def __init__(self):
        self.history = []
        self.blocks = OrderedDict()
        self.code_pattern = re.compile(
            r'<!--\s*Block-Start:\s*(\{.*?\})\s*-->\s*```(\w+)?\s*\n(.*?)\n```\s*<!--\s*Block-End:\s*(\{.*?\})\s*-->',
            re.DOTALL
        )
        self.line_pattern = re.compile(
            r'<!--\s*Cmd-(\w+):\s*(\{.*?\})\s*-->'
        )
        self.log = logger.bind(src='code_blocks')

    def __len__(self):
        return len(self.blocks)
    
    def parse(self, markdown_text, parse_mcp=False):
        blocks = OrderedDict()
        errors = []
        for match in self.code_pattern.finditer(markdown_text):
            start_json, lang, content, end_json = match.groups()
            try:
                start_meta = json.loads(start_json)
                end_meta = json.loads(end_json)
            except json.JSONDecodeError as e:
                self.log.exception('Error parsing code block', start_json=start_json, end_json=end_json)
                error = {'JSONDecodeError': {'Block-Start': start_json, 'Block-End': end_json, 'reason': str(e)}}
                errors.append(error)
                continue

            code_name = start_meta.get("name")
            if code_name != end_meta.get("name"):
                self.log.error("Start and end name mismatch", start_name=code_name, end_name=end_meta.get("name"))
                error = {'Start and end name mismatch': {'start_name': code_name, 'end_name': end_meta.get("name")}}
                errors.append(error)
                continue

            version = start_meta.get("version", 1)
            if code_name in blocks or code_name in self.blocks:
                old_block = blocks.get(code_name) or self.blocks.get(code_name)
                old_version = old_block.version
                if old_version >= version:
                    self.log.error("Duplicate code name with same or newer version", code_name=code_name, old_version=old_version, version=version)
                    error = {'Duplicate code name with same or newer version': {'code_name': code_name, 'old_version': old_version, 'version': version}}
                    errors.append(error)
                    continue

            # 创建代码块对象
            block = CodeBlock(
                name=code_name,
                version=version,
                lang=lang,
                code=content,
                path=start_meta.get('path'),
            )

            blocks[code_name] = block
            self.history.append(block)
            self.log.info("Parsed code block", code_block=block)

            try:
                block.save()
                self.log.info("Saved code block", code_block=block)
            except Exception as e:
                self.log.error("Failed to save file", code_block=block, reason=e)

        self.blocks.update(blocks)

        exec_blocks = []
        line_matches = self.line_pattern.findall(markdown_text)
        for line_match in line_matches:
            cmd, json_str = line_match
            try:
                line_meta = json.loads(json_str)
            except json.JSONDecodeError as e:
                self.log.error(f"Invalid JSON in Cmd-{cmd} block", json_str=json_str, reason=e)
                error = {f'Invalid JSON in Cmd-{cmd} block': {'json_str': json_str, 'reason': str(e)}}
                errors.append(error)
                continue

            error = None
            if cmd == 'Exec':
                exec_name = line_meta.get("name")
                if not exec_name:
                    error = {'Cmd-Exec block without name': {'json_str': json_str}}
                elif exec_name not in self.blocks:
                    error = {'Cmd-Exec block not found': {'exec_name': exec_name, 'json_str': json_str}}
                else:
                    exec_blocks.append(self.blocks[exec_name])
            else:
                error = {f'Unknown command in Cmd-{cmd} block': {'cmd': cmd}}

            if error:
                errors.append(error)

        ret = {}
        if errors: ret['errors'] = errors
        if exec_blocks: ret['exec_blocks'] = exec_blocks
        if blocks: ret['blocks'] = [v for v in blocks.values()]

        if parse_mcp:
            # 首先尝试从代码块中提取 MCP 调用, 然后尝试从markdown文本中提取
            json_content = extra_call_tool_blocks(list(blocks.values())) or extract_call_tool_str(markdown_text)

            if json_content:
                ret['call_tool'] = json_content
                self.log.info("Parsed MCP call_tool", json_content=json_content)

        return ret
    
    def get_code_by_name(self, code_name):
        try:
            return self.blocks[code_name].code
        except KeyError:
            self.log.error("Code name not found", code_name=code_name)
            return None

    def get_block_by_name(self, code_name):
        try:
            return self.blocks[code_name]
        except KeyError:
            self.log.error("Code name not found", code_name=code_name)
            return None

    def to_list(self):
        """将 CodeBlocks 对象转换为 JSON 字符串
        
        Returns:
            str: JSON 格式的字符串
        """
        blocks = [block.to_dict() for block in self.history]
        return blocks
    
    def get_state(self):
        """获取需要持久化的状态数据"""
        return self.to_list()
    
    def restore_state(self, blocks_data):
        """从代码块数据恢复状态"""
        self.history.clear()
        self.blocks.clear()
        
        if blocks_data:
            for block_data in blocks_data:
                code_block = CodeBlock(
                    name=block_data['name'],
                    version=block_data['version'],
                    lang=block_data['lang'],
                    code=block_data['code'],
                    path=block_data.get('path'),
                    deps=block_data.get('deps')
                )
                self.history.append(code_block)
                self.blocks[code_block.name] = code_block
    

    def clear(self):
        self.history.clear()
        self.blocks.clear()
    
    # Trackable接口实现
    def get_checkpoint(self) -> int:
        """获取当前检查点状态 - 返回history长度"""
        return len(self.history)
    
    def restore_to_checkpoint(self, checkpoint: Optional[int]):
        """恢复到指定检查点"""
        if checkpoint is None:
            # 恢复到初始状态
            self.clear()
        else:
            # 恢复到指定长度
            if checkpoint < len(self.history):
                # 获取要删除的代码块
                deleted_blocks = self.history[checkpoint:]
                
                # 从 blocks 字典中删除对应的代码块
                for block in deleted_blocks:
                    if block.name in self.blocks:
                        del self.blocks[block.name]
                
                # 截断 history 到指定长度
                self.history = self.history[:checkpoint]