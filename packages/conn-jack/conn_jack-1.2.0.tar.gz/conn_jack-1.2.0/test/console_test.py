#  conn_jack/test/console_test.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
"""
Test to be run from the console, testing the non-Qt JackConnectionManager
"""
import sys, logging
from conn_jack import JackConnectionManager, JackConnectError


def on_error(error_message):
	print(f'ERROR: {error_message}')


def on_client_registration(client_name, action):
	action = 'REGISTERED' if action else 'GONE'
	print(f'Client "{client_name}": {action}')


def on_port_registration(port, action):
	action = 'REGISTERED' if action else 'GONE'
	print(f'{port}: {action}')


def on_port_connect(port_a, port_b, action):
	action = 'CONNECTED' if action else 'DISCONNECTED'
	print(f'{port_a} -> {port_b}: {action}')


def on_port_rename(port, old_name, new_name):
	print(f'{port} renamed from "{old_name}" to "{new_name}"')


def on_xrun(xruns):
	print(f'{xruns} xruns')


def on_shutdown():
	print('JACK is shutting down')


def list_ports(ports):
	for port in ports:
		print(port.name + '; alias "' + '", "'.join(port.aliases) + '"') \
			if port.aliases \
			else port.name


def main():

	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)4d] %(levelname)-8s %(message)s"
	)

	try:
		conn_man = JackConnectionManager()
	except JackConnectError:
		print('Could not connect to JACK server. Is it running?')
		return 1

	conn_man.on_error(on_error)
	conn_man.on_client_registration(on_client_registration)
	conn_man.on_port_registration(on_port_registration)
	conn_man.on_port_connect(on_port_connect)
	conn_man.on_port_rename(on_port_rename)
	conn_man.on_xrun(on_xrun)
	conn_man.on_shutdown(on_shutdown)

	print('Current port list:')
	print('==== INPUT PORTS ====')
	list_ports(conn_man.output_ports())
	print()
	print('==== OUTPUT PORTS ====')
	list_ports(conn_man.input_ports())
	print()
	print('==== CONNECTIONS =====')
	for port in conn_man.output_ports():
		print(port.name)
		for tgt in conn_man.get_port_connections(port):
			print(f'  {tgt.name}')
	print()

	print('Printing events at the console. Press Enter to quit...')
	try:
		input()
	except KeyboardInterrupt:
		pass
	return 0


if __name__ == "__main__":
	sys.exit(main())


#  end conn_jack/test/console_test.py
