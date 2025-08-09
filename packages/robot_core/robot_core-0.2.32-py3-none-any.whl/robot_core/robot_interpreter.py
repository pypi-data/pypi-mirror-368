import base64
import importlib
import io
import json
import os
import sys
import threading

import debugpy
from loguru import logger


def input_thread():
	"""子线程：读取标准输入并将命令放入队列"""

	for line in sys.stdin:
		line = line.strip()
		if not line:
			continue
		try:
			action_data = json.loads(line.strip())

			if action_data.get('action') == 'start':
				logger.info(action_data.get('action'))
			else:
				logger.info('无效的命令')
		except Exception as e:
			print(json.dumps({'error': str(e)}, ensure_ascii=False), flush=True)


def main(raw_input):
	# 关键点：把 stdin/stdout 显式设为 UTF-8
	sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
	robot_raw_inputs = base64.b64decode(raw_input).decode('utf-8')
	robot_inputs = json.loads(robot_raw_inputs)

	# os_sleep.start_prevent_os_sleep()
	init_log(robot_inputs)
	args = robot_inputs.get('inputs', {})
	if args is None:
		args = {}

	if robot_inputs['environment_variables'] is not None:
		for env_key, env_value in robot_inputs['environment_variables'].items():
			if env_value is not None:
				os.environ[env_key] = env_value

	_insert_sys_path(robot_inputs['sys_path_list'])

	mod = importlib.import_module(robot_inputs['mod'])
	input_t = threading.Thread(target=input_thread, daemon=True)
	input_t.start()
	try:
		logger.info('流程开始运行')
		if robot_inputs.get('debug', False):
			debugpy.listen(('127.0.0.1', robot_inputs.get('debug_port', 5678)))
			debugpy.wait_for_client()
		result = mod.main(**args)
		logger.info('流程结束运行', result=json.dumps(result, default=custom_default, ensure_ascii=False))
	except Exception as e:
		logger.info('流程运行失败', e)
		logger.exception(e)
		raise e


def init_log(robot_inputs):
	# 移除默认输出（避免重复）
	logger.remove()
	# 添加 JSON 格式的处理器（控制台）
	logger.add(sys.stdout, format='{message}', serialize=True)
	logger.level('OUTPUT', no=25, color='<green>', icon='✅')


def _insert_sys_path(sys_path_list):
	for sys_path in sys_path_list:
		sys.path.insert(0, sys_path)


def custom_default(obj):
	if hasattr(obj, '__dict__'):
		# 如果是自定义类实例，只序列化其可序列化的属性
		return {k: v for k, v in obj.__dict__.items() if isinstance(v, (str, int, float, list, dict, bool))}
	else:
		# 对于其他不可序列化的对象，返回 None 或其他默认值
		return None
