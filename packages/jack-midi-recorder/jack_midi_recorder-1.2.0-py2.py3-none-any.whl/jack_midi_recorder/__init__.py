#  jack_midi_recorder/__init__.py
#
#  Copyright 2024 Leon Dionne <ldionne@dridesign.sh.cn>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
"""
Basic implementation of MIDI event recording / playback.
"""
import logging, threading
import numpy as np
from jack import Client, Port, Status, JackError, CallbackExit, \
				STOPPED, ROLLING, STARTING, NETSTARTING

__version__ = "1.2.0"


class MIDIRecorder:
	"""
	A class which records incoming MIDI events, saves/loads as raw numpy data, and plays back recorded events.
	"""

	# state constants:
	INACTIVE	= 0
	PLAYING		= 1
	RECORDING	= 2
	FREEWHEEL	= 8

	BUFFER_SIZE	= 2097152

	msgtype	= np.dtype([
		('frame', np.uint32),
		('offset', np.uint32),
		('data', np.uint8, (3,))
	])

	def __init__(self, client_name = 'midi-recorder'):
		self.state = self.INACTIVE
		self.ports = []
		self.in_ports = {}
		self.out_ports = {}
		self.client = Client(client_name, no_start_server=True)
		self.finished_playing_event = threading.Event()
		self.__real_process_callback = self.null_process_callback
		self.__frame = None
		self.__last_frame = None
		self.client.set_blocksize_callback(self.blocksize_callback)
		self.client.set_samplerate_callback(self.samplerate_callback)
		self.client.set_process_callback(self.process_callback)
		self.client.set_shutdown_callback(self.shutdown_callback)
		self.client.set_xrun_callback(self.xrun_callback)
		self.client.activate()
		self.client.get_ports()
		self.set_port_list([])

	def shutdown(self):
		self.stop()
		self.client.deactivate()

	def first_input_port(self):
		"""
		Here for testing from the command line
		"""
		return self.in_ports[self.ports[0]]

	def set_port_list(self, ports):
		old_ports = set(self.ports)
		new_ports = set(ports)
		self.ports = ports
		for port in old_ports - new_ports:
			self.in_ports[port].unregister()
			self.out_ports[port].unregister()
		for port in new_ports - old_ports:
			self.in_ports[port] = self.client.midi_inports.register(f'port_{port}_in')
			self.out_ports[port] = self.client.midi_outports.register(f'port_{port}_out')
		self.buffers = { port: np.zeros(self.BUFFER_SIZE, self.msgtype) for port in self.ports }
		self.buf_idx = { port: 0 for port in self.ports }

	def connect_input_port(self, port_number, other_port_name):
		if not self.in_ports[port_number].is_connected_to(other_port_name):
			self.in_ports[port_number].connect(other_port_name)

	def connect_output_port(self, port_number, other_port_name):
		if not self.out_ports[port_number].is_connected_to(other_port_name):
			self.out_ports[port_number].connect(other_port_name)

	def event_count(self):
		return sum(self.buf_idx.values())

	def event_counts(self):
		return [ 0 if self.buffers[port] is None \
			else self.buf_idx[port] \
			for port in self.ports ]

	def events(self):
		return [ None if self.buffers[port] is None \
			else self.buffers[port][ : self.buf_idx[port] ] \
			for port in self.ports ]

	def ready_to_record(self):
		return all(port.number_of_connections > 0 for port in self.in_ports.values())

	def ready_to_play(self):
		return self.event_count() > 0

	def record(self):
		logging.debug('RECORD')
		for port in self.ports:
			self.buf_idx[port] = 0
		self.__frame = 0
		self.__real_process_callback = self.record_process_callback
		self.state = self.RECORDING

	def stop(self):
		logging.debug('STOP')
		self.__real_process_callback = self.null_process_callback
		if self.state == self.RECORDING:
			first_frame = min([ self.buffers[port][0]['frame'] for port in self.ports ])
			for port in self.ports:
				self.buffers[port]['frame'] -= first_frame
			self.__last_frame = self.__frame - first_frame
		self.state = self.INACTIVE

	def save_to(self, filename):
		"""
		Save the midi events recorded in a raw numpy format.

		No not include port numbers in the filename; the port number is automatically
		appended. One file is saved for each port recorded.
		"""
		for port in self.ports:
			npfilename = f'{filename}-{port}.npy'
			logging.debug('Saving port %s data to "%s"', port, npfilename)
			np.save(npfilename, self.buffers[port])

	def load_from(self, filename):
		"""
		Load midi events saved with "save_to()".

		No not include port numbers in the filename; the port number is automatically
		appended. One file is loaded for each port defined. If a file is not found with
		the appropriate port numbers, an exception is raised.

		For example:
			r = MIDIRecorder([1, 4, 6])
			r.load_from("file")
		... will search for these files in the current directory:
			file-1.npy
			file-4.npy
			file-6.npy
		"""
		for port in self.ports:
			npfilename = f'{filename}-{port}.npy'
			logging.debug('Loading port %s data from "%s"', port, npfilename)
			self.buffers[port] = np.load(npfilename)

	def play(self):
		logging.debug('PLAY')
		for port in self.ports:
			if self.buffers[port] is None:
				raise RuntimeError("Empty record buffer")
			self.buf_idx[port] = 0
		self.finished_playing_event.clear()
		self.state = self.PLAYING
		self.__frame = 0
		self.__real_process_callback = self.play_process_callback
		self.finished_playing_event.wait()
		self.stop()

	def null_process_callback(self, frames):
		pass

	def record_process_callback(self, _):
		for port in self.ports:
			for offset, indata in self.in_ports[port].incoming_midi_events():
				if len(indata) == 3:
					self.buffers[port][self.buf_idx[port]] = (self.__frame, offset, indata)
					self.buf_idx[port] += 1
		self.__frame += 1

	def play_process_callback(self, _):
		for port in self.ports:
			self.out_ports[port].clear_buffer()
			while self.__frame == self.buffers[port][self.buf_idx[port]]['frame']:
				self.out_ports[port].write_midi_event(
					self.buffers[port][self.buf_idx[port]]['offset'],
					self.buffers[port][self.buf_idx[port]]['data']
				)
				self.buf_idx[port] += 1
		if self.__frame == self.__last_frame:
			self.finished_playing_event.set()
		self.__frame += 1

	# -----------------------
	# JACK callbacks

	def blocksize_callback(self, _):
		"""
		The argument blocksize is the new buffer size. The callback is supposed to
		raise CallbackExit on error.
		"""
		if self.state != self.INACTIVE:
			raise CallbackExit

	def samplerate_callback(self, _):
		"""
		The argument samplerate is the new engine sample rate. The callback is supposed
		to raise CallbackExit on error.
		"""
		if self.state != self.INACTIVE:
			raise CallbackExit

	def process_callback(self, frames):
		try:
			self.__real_process_callback(frames)
		except Exception as e:
			logging.error(e)
			raise CallbackExit from e

	def shutdown_callback(self, *_):
		"""
		The argument status is of type jack.Status.
		"""
		if self.state != self.INACTIVE:
			raise JackShutdownError

	def xrun_callback(self, delayed_usecs):
		"""
		The callback argument is the delay in microseconds due to the most recent XRUN
		occurrence. The callback is supposed to raise CallbackExit on error.
		"""
		pass


class JackShutdownError(Exception):

	pass


#  end jack_midi_recorder/__init__.py
