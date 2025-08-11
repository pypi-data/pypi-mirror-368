#  jack_midi_recorder/tests/basic_usage.py
#
#  Copyright 2025 Leon Dionne <ldionne@dridesign.sh.cn>
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
import sys, os, logging
from tempfile import mkstemp
from jack import JackError
from jack_midi_recorder import MIDIRecorder


def main():

	logging.basicConfig(
		level = logging.DEBUG,
		format = "[%(filename)24s:%(lineno)-4d] %(levelname)-8s %(message)s"
	)

	try:
		rec = MIDIRecorder()
	except JackError:
		print('Could not connect to JACK server. Is it running?')
		return 1

	rec.set_port_list([1])
	for p in rec.client.get_ports(is_midi=True, is_output=True, is_terminal=True):
		if p.name.lower().find('through') < 0:
			print(f"Connecting to {p.name}")
			try:
				rec.first_input_port().connect(p.name)
				break
			except Exception as e:
				print(e)

	print('#' * 80)
	print('Recording ... press Return to quit')
	print('#' * 80)
	rec.record()
	try:
		input()
	except KeyboardInterrupt:
		print("Interrupted")
	rec.stop()

	print('#' * 80)
	print('Ready to play ... press Return')
	print('#' * 80)
	try:
		input()
		rec.play()
	except KeyboardInterrupt:
		print("Interrupted")

	_, filename = mkstemp()
	print('#' * 80)
	print('Saving')
	print('#' * 80)
	rec.save_to(filename)

	print('#' * 80)
	print('Loading')
	print('#' * 80)
	rec.load_from(filename)

	os.unlink(filename)
	return 0


if __name__ == "__main__":
	sys.exit(main())


#  end jack_midi_recorder/tests/basic_usage.py
