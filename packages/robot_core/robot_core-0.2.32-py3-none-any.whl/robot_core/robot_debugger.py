# -*- coding:utf8 -*-
import base64
import io
import json
import os
import sys

from loguru import logger
from pydantic import BaseModel

sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)


class PythonREPL(BaseModel):
	"""Simulates a standalone Python REPL."""

	globals = {}
	locals = {}

	def run(self, command: str) -> str:
		"""Run command with own globals/locals and returns anything printed."""
		try:
			exec(command, self.globals, self.locals)
		except Exception as e:
			output = str(e)
			return output


def main(input_param):
	robot_raw_inputs = base64.b64decode(input_param).decode('utf-8')
	robot_inputs = json.loads(robot_raw_inputs)

	init_log()
	args = robot_inputs.get('inputs', {})
	if args is None:
		args = {}

	if 'environment_variables' in robot_inputs and robot_inputs['environment_variables'] is not None:
		for env_key, env_value in robot_inputs['environment_variables'].items():
			if env_value is not None:
				os.environ[env_key] = env_value
	if 'sys_path_list' in robot_inputs and robot_inputs['sys_path_list'] is not None:
		_insert_sys_path(robot_inputs['sys_path_list'])
	repl = PythonREPL()
	while True:
		code = input('>>>')
		# code = base64.b64decode(code).decode("utf-8")
		result = repl.run(code)
		if result:
			logger.error(result)


def init_log():
	# 移除默认输出（避免重复）
	logger.remove()
	# 添加 JSON 格式的处理器（控制台）
	logger.add(sys.stdout, format='{message}', serialize=True)
	logger.level('OUTPUT', no=25, color='<green>', icon='✅')


def _insert_sys_path(sys_path_list):
	for sys_path in sys_path_list:
		sys.path.insert(0, sys_path)


if __name__ == '__main__':
	main('e30=')
