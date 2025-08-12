#  conn_jack/__init__.py
#
#  Copyright 2025 liyang <liyang@veronica>
#
"""
Classes for managing jack client connections.

These differ from the JACK Client for Python (jack), in that it makes possible
connecting and disconnecting ports which are not "owned" by a client created in
your process.

Utilizes "jacklib" for port access.
"""
import logging
from functools import cached_property
from queue import Queue
import jacklib
from jacklib.helpers import c_char_p_p_to_list
from jacklib.helpers import get_jack_status_error_string
from log_soso import log_error

__version__ = "1.2.0"


class JackPort:

	def __init__(self, ptr, name):
		self.ptr = ptr
		self.name = name

	@cached_property
	def aliases(self):
		num_aliases, *aliases = jacklib.port_get_aliases(self.ptr)
		return list(aliases[:num_aliases])

	@cached_property
	def flags(self):
		return jacklib.port_flags(self.ptr)

	@cached_property
	def is_physical(self):
		return self.flags & jacklib.JackPortIsPhysical

	@cached_property
	def is_input(self):
		return self.flags & jacklib.JackPortIsInput

	@cached_property
	def is_output(self):
		return self.flags & jacklib.JackPortIsOutput

	@property
	def client_name(self):
		return self._split_name[0]

	@property
	def port_name(self):
		return self._split_name[1]

	@cached_property
	def type(self):
		return jacklib.port_type(self.ptr)

	@property
	def is_midi(self):
		return 'midi' in self.type

	@property
	def is_audio(self):
		return 'audio' in self.type

	@cached_property
	def _split_name(self):
		try:
			return self.name.split(':', 1)
		except ValueError:
			return ('[error]', '[error]')

	def __str__(self):
		return self.name

	def __repr__(self):
		return '<JackPort "{}" ({}, {})>'.format(
			self.name,
			'physical' if self.is_physical else 'plugin',
			'input'if self.is_input else 'output'
		)


class JackConnectError(RuntimeError):
	pass


class _JackConnectionManager():

	client = None

	def __init__(self, *, client_name = 'conn-man'):
		status = jacklib.jack_status_t()
		self.client = jacklib.client_open(client_name, jacklib.JackNoStartServer, status)
		if status.value:
			raise JackConnectError(get_jack_status_error_string(status))
		if not self.client:
			raise JackConnectError('No client created')
		name = jacklib.get_client_name(self.client)
		if name is None:
			raise RuntimeError("Could not get JACK client name.")
		self.client_name = name.decode()
		self.queue = Queue()
		self.xruns = 0
		jacklib.set_error_function(self._error_callback)
		jacklib.set_client_registration_callback(self.client, self._client_registration_callback, None)
		jacklib.set_port_registration_callback(self.client, self._port_registration_callback, None)
		jacklib.set_port_connect_callback(self.client, self._port_connect_callback, None)
		jacklib.set_port_rename_callback(self.client, self._port_rename_callback, None)
		jacklib.set_xrun_callback(self.client, self._xrun_callback, None)
		jacklib.on_shutdown(self.client, self._shutdown_callback, None)
		jacklib.activate(self.client)

	def close(self):
		if self.client:
			jacklib.deactivate(self.client)
			jacklib.client_close(self.client)

	# ------------------------------
	# State

	@property
	def samplerate(self):
		return jacklib.get_sample_rate(self.client)

	@property
	def buffer_size(self):
		return jacklib.get_buffer_size(self.client)

	# ------------------------------
	# Port / connection info funcs

	def get_ports(self, flags = 0, *, port_name_pattern = ''):
		"""
		Returns a list of JackPort objects which match the given flags (if any).
		The available flags from jacklib/api.py:

			JackPortIsInput = 0x1
			JackPortIsOutput = 0x2
			JackPortIsPhysical = 0x4
			JackPortCanMonitor = 0x8
			JackPortIsTerminal = 0x10
			JackPortIsControlVoltage = 0x100

		"""
		return [
			self.get_port_by_name(name) \
			for name in c_char_p_p_to_list(
				jacklib.get_ports(self.client, port_name_pattern, '', flags))
		]

	def get_port_by_name(self, name):
		"""
		Returns JackPort object.
		"""
		ptr = jacklib.port_by_name(self.client, name)
		return JackPort(ptr, name)

	def get_port_by_id(self, port_id):
		"""
		Returns JackPort object.
		"""
		ptr = jacklib.port_by_id(self.client, port_id)
		return JackPort(ptr, jacklib.port_name(ptr))

	def get_client_ports(self, client_name):
		return self.get_ports(port_name_pattern = f'{client_name}:*')

	def get_port_connections(self, port):
		"""
		Returns a list of JackPort objects.
		"""
		return [ self.get_port_by_name(port_name) \
			for port_name in jacklib.port_get_all_connections(self.client, port.ptr) ] \
			if jacklib.port_connected(port.ptr) \
			else []

	def get_connections(self, *, ports = None):
		"""
		Generator which yields tuples of JackPort, JackPort.
		"""
		if ports is None:
			ports = self.get_ports()
		for port in ports:
			if jacklib.port_connected(port.ptr):
				for port_name in jacklib.port_get_all_connections(self.client, port.ptr):
					yield((port, self.get_port_by_name(port_name)))

	def input_ports(self):
		"""
		Returns a list of JackPort objects.
		"""
		return self.get_ports(jacklib.JackPortIsInput)

	def output_ports(self):
		"""
		Returns a list of JackPort objects.
		"""
		return self.get_ports(jacklib.JackPortIsOutput)

	def physical_input_ports(self):
		"""
		Returns a list of JackPort objects.
		"""
		return self.get_ports(jacklib.JackPortIsInput | jacklib.JackPortIsPhysical)

	def physical_output_ports(self):
		"""
		Returns a list of JackPort objects.
		"""
		return self.get_ports(jacklib.JackPortIsOutput | jacklib.JackPortIsPhysical)

	def physical_playback_clients(self):
		"""
		Returns a list of (str) client names.
		"""
		return list(set(port.client_name \
			for port in self.get_ports(jacklib.JackPortIsInput | jacklib.JackPortIsPhysical) \
			if not port.is_midi))

	def first_physical_playback_client(self):
		"""
		Returns (str) client name.
		"""
		for port in self.get_ports(jacklib.JackPortIsInput | jacklib.JackPortIsPhysical):
			if not port.is_midi:
				return port.client_name

	def connect(self, outport: JackPort, inport: JackPort):
		"""
		Connect the given JackPort to the given JackPort
		"""
		jacklib.connect(self.client, outport.name, inport.name)

	def connect_by_name(self, outport: str, inport: str):
		"""
		Connect the ports identified by their name.
		"""
		jacklib.connect(self.client, outport, inport)

	def disconnect(self, outport: JackPort, inport: JackPort):
		"""
		Disconnect the given JackPort to the given JackPort
		"""
		jacklib.disconnect(self.client, outport.name, inport.name)

	def disconnect_by_name(self, outport: str, inport: str):
		"""
		Disconnect the ports identified by their name.
		"""
		jacklib.disconnect(self.client, outport, inport)


class JackConnectionManager(_JackConnectionManager):

	# ------------------------------
	# Callbacks

	_cb_error= None
	_cb_client_registration = None
	_cb_port_registration = None
	_cb_port_connect = None
	_cb_port_rename = None
	_cb_xrun = None
	_cb_shutdown = None

	def on_error(self, callback):
		"""
		Sets the function to call when there is an error.
		The given callback must have the following signature:
		<callback>(error_message: str)
		Note: by default, errors are logged using the "logging" module.
		"""
		self._cb_error = callback

	def on_client_registration(self, callback):
		"""
		Sets the function to call when a new client is registered / unregistered.
		The given callback must have the following signature:
		<callback>(client_name: str, action: bool)
		"action" will be True on register, False on unregister.
		"""
		self._cb_client_registration = callback

	def on_port_registration(self, callback):
		"""
		Sets the function to call when a new port is registered / unregistered.
		The given callback must have the following signature:
		<callback>(port: JackPort, action: bool)
		"action" will be True on register, False on unregister.
		"""
		self._cb_port_registration = callback

	def on_port_connect(self, callback):
		"""
		Sets the function to call when two ports are connected / disconnected.
		The given callback must have the following signature:
		<callback>(port_a: JackPort, port_b: JackPort, action: bool)
		"action" will be True on connect, False on disconnect.
		"""
		self._cb_port_connect = callback

	def on_port_rename(self, callback):
		"""
		Sets the function to call when a port is renamed.
		The given callback must have the following signature:
		<callback>(port: JackPort, old_name: str, new_name: str)
		"""
		self._cb_port_rename = callback

	def on_xrun(self, callback):
		"""
		Sets the function to call when there is an xrun.
		The given callback must have the following signature:
		<callback>(xruns: int)
		"""
		self._cb_xrun = callback

	def on_shutdown(self, callback):
		"""
		Sets the function to call when jack shuts down.
		The given callback must have the following signature:
		<callback>()
		"""
		self._cb_shutdown = callback

	def _error_callback(self, error):
		error_message = error.decode(jacklib.ENCODING, errors='ignore')
		if self._cb_error is None:
			logging.error(error_message)
		else:
			try:
				self._cb_error(error_message)
			except Exception as e:
				log_error(e)

	def _client_registration_callback(self, client_name, action, *_):
		if self._cb_client_registration is not None:
			try:
				self._cb_client_registration(client_name.decode(jacklib.ENCODING, errors='ignore'), action)
			except Exception as e:
				log_error(e)

	def _port_registration_callback(self, port_id, action, *_):
		if self._cb_port_registration is not None:
			try:
				self._cb_port_registration(self.get_port_by_id(port_id), action)
			except Exception as e:
				log_error(e)

	def _port_connect_callback(self, port_a_id, port_b_id, connect, *_):
		if self._cb_port_connect is not None:
			try:
				self._cb_port_connect(
					self.get_port_by_id(port_a_id),
					self.get_port_by_id(port_b_id),
					bool(connect)
				)
			except Exception as e:
				log_error(e)

	def _port_rename_callback(self, port_id, old_name, new_name, *_):
		if self._cb_port_rename is not None:
			try:
				self._cb_port_rename(
					self.get_port_by_id(port_id),
					old_name.decode(jacklib.ENCODING, errors='ignore') if old_name else 'NO_OLD_NAME',
					new_name.decode(jacklib.ENCODING, errors='ignore') if new_name else 'NO_NEW_NAME'
				)
			except Exception as e:
				log_error(e)

	def _xrun_callback(self, _):
		self.xruns += 1
		if self._cb_xrun is not None:
			try:
				self._cb_xrun(self.xruns)
			except Exception as e:
				log_error(e)
		return 0

	def _shutdown_callback(self, *_):
		if self._cb_shutdown is not None:
			try:
				self._cb_shutdown()
			except Exception as e:
				log_error(e)


#  end kitbash/connection_manager.py
