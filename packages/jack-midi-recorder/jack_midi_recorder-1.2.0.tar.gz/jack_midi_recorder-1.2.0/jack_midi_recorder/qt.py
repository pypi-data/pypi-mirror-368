#  jack_midi_recorder/qt.py
#
#  Copyright 2024 liyang <liyang@veronica>
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
Defines the Qt version which uses Qt signals.
"""
from PyQt5.QtCore import QObject, pyqtSignal
from jack_midi_recorder import MIDIRecorder


class QtMIDIRecorder(MIDIRecorder, QObject):
	"""
	Qt version of MIDIRecorder which utilizes Qt signals / slots.
	"""

	sig_play_finished = pyqtSignal()

	def play(self):
		super().play()
		self.sig_play_finished.emit()

	def __init__(self, client_name):
		QObject.__init__(self)
		MIDIRecorder.__init__(self, client_name)


#  end jack_midi_recorder/qt.py
