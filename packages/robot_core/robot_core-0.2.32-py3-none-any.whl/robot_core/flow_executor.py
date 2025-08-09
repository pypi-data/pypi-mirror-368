import base64
import codecs
import importlib
import json
import os
import pdb
import sys
import time
from loguru import logger

if sys.stdout.encoding is None or sys.stdout.encoding.upper() != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding is None or sys.stderr.encoding.upper() != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def main(raw_input):
	robot_raw_inputs = base64.b64decode(raw_input).decode('utf-8')
	robot_inputs = json.loads(robot_raw_inputs)

	args = robot_inputs.get('inputs', {})
	if args is None:
		args = {}

	if robot_inputs['environment_variables'] is not None:
		for env_key, env_value in robot_inputs['environment_variables'].items():
			if env_value is not None:
				os.environ[env_key] = env_value

	_insert_sys_path(robot_inputs['sys_path_list'])
	flow_path = robot_inputs['flow_path']

	try:
		logger.info('流程图开始运行')
		execute_flow(flow_path, robot_inputs.get('debug', False))
		logger.info('流程结束运行')
		time.sleep(3)
	except Exception as e:
		logger.exception(e)
		raise e


def execute_flow(flow_path, debug=False):
	with open(flow_path, 'r', encoding='UTF-8') as flow_file:
		flow_config = json.loads(flow_file.read())
	start_block = find_start_block(flow_config)
	if start_block is None:
		raise Exception('找不到开始节点')
	next_block = find_next_block(flow_config, start_block['id'], 'output')
	while next_block is not None:
		block_id = next_block['id']
		edge_type = 'output'
		try:
			mod = importlib.import_module(block_id)
			if debug:
				pdb.set_trace()
			mod.main(next_block['data'])
		except Exception as e:
			logger.exception(e)
			edge_type = 'fallback'

		next_block = find_next_block(flow_config, block_id, edge_type)


def find_start_block(flow_config):
	nodes = flow_config['nodes']
	return list(filter(lambda node: node['data']['nodeType'] == 'Start', nodes))[0]


def find_next_block(flow_config, current_id, edge_type):
	edges = flow_config['edges']
	filtered_edges = list(
		filter(
			lambda edge: edge['source'] == current_id and edge['sourceHandle'].startswith(current_id + '-' + edge_type),
			edges,
		)
	)
	if len(filtered_edges) > 1:
		raise Exception('节点有多个输出')
	if len(filtered_edges) == 0:
		return None
	nodes = flow_config['nodes']
	return list(filter(lambda node: node['id'] == filtered_edges[0]['target'], nodes))[0]


def _insert_sys_path(sys_path_list):
	for sys_path in sys_path_list:
		sys.path.insert(0, sys_path)
