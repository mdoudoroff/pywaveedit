#!/usr/bin/env python
# encoding: utf-8

import struct
import wave

stHeaderFields = dict()
rawData = None

class Wavetable(object):
	'''Organizes a single wavetable for the Synthesis Technology E352/E370'''

	def __init__(self, bank=None):
		self._values = [0]*256  # always 256
		self._bank = bank

	def values(self):
		'''returns the list of values for this wavetable (256 integers)'''
		return self._values

	def initValues(self, v):
		'''set all values for this wavetable to the same integer'''
		if type(v) != type(1) or v > 32767 or v < -32767:
			raise Exception, u'Table values must be integers between 32767 and -32767'
		self._values = [v]*256

	def setValue(self, pos, v):
		'''set the value of a particular position (0-255)'''
		if type(v) != type(1) or v > 32767 or v < -32767:
			raise Exception, u'Table values must be integers between 32767 and -32767'
		if pos > 255 or pos < 0:
			raise Exception, u'Position must be an integer between 0 and 255'
		self._values[pos] = v

	def setValues(self, l):
		'''set all 256 values at once to a list of 256 integers'''
		if not type(l) == type([1,2]):
			raise Exception, u'Table values must be a list'
		if not len(l) == 256:
			raise Exception, u'Table values must be a list exactly 256 integers long'
		if not len(set([type(x) for x in l]))==1 or type(l[0]) != type(1):
			raise Exception, u'Table values must be integers'
		if max(l) > 32767 or min(l) < -32767:
			raise Exception, u'Table values must be integers between 32767 and -32767'
		self._values = l

	def index(self):
		'''convenience method: which index is this in the bank?'''
		return self._bank.tables().index(self)

class Bank(object):
	'''Organizes a bank of wavetables for the Synthesis Technology E352/E370'''

	def __init__(self):
		self._tables = []

		# create 64 blank wavetables
		for x in range(64):
			self._tables.append(Wavetable(self))

	def tables(self):
		'''returns the list of 64 Wavetable objects'''
		return self._tables

	def values(self):
		'''returns a flattened list of values for the entire bank'''
		values = []
		for table in self._tables:
			values += table.values()
		return values

	def readBankFromFile(self,fn):
		'''loads the values of an E352/E370-compatible wavetable file into this bank'''

		# The code in this method is lightly adapted from:
		# https://stackoverflow.com/questions/27424712/rebuilding-my-wave-file-with-struct

		with open(fn, "rb") as f:
			riffTag = f.read(4)
			if riffTag != 'RIFF':
				raise Exception, 'not a valid RIFF file'

			riffLength = struct.unpack('<L', f.read(4))[0]
			riffType = f.read(4)
			if riffType != 'WAVE':
				raise Exception, 'not a WAV file'
				exit(1)

			# now read children
			while f.tell() < 8 + riffLength:
				tag = f.read(4)
				length = struct.unpack('<L', f.read(4))[0]

				if tag == 'fmt ': # format element
					fmtData = f.read(length)
					fmt, numChannels, sampleRate, byteRate, blockAlign, bitsPerSample = struct.unpack('<HHLLHH', fmtData)
					stHeaderFields['AudioFormat'] = fmt
					stHeaderFields['NumChannels'] = numChannels
					stHeaderFields['SampleRate'] = sampleRate
					stHeaderFields['ByteRate'] = byteRate
					stHeaderFields['BlockAlign'] = blockAlign
					stHeaderFields['BitsPerSample'] = bitsPerSample

				elif tag == 'data': # data element
					rawData = f.read(length)

				else: # some other element, just skip it
					f.seek(length, 1)

		print stHeaderFields

		blockAlign = stHeaderFields['BlockAlign']
		numChannels = stHeaderFields['NumChannels']

		# some sanity checks
		assert(stHeaderFields['BitsPerSample'] == 16)
		assert(numChannels * stHeaderFields['BitsPerSample'] == blockAlign * 8)

		data = []

		for offset in range(0, len(rawData), blockAlign):
			samples = struct.unpack('<' + 'h' * numChannels, rawData[offset:offset+blockAlign])

			# now samples contains a tuple with sample values for each channel
			# (in case of mono audio, you'll have a tuple with just one element).
			# you may store it in the array for future processing, 
			# change and immediately write to another stream, whatever.

			data.append(samples[0])

		if not len(data)==16384:
			raise Exception, 'WAV file is wrong length: must be exactly 16384 samples long'

		# split the data across our 64 wavetables
		n = 256
		chunks = [data[i:i + n] for i in xrange(0, len(data), n)]
		for chunk in chunks:
			self._tables[chunks.index(chunk)]._values = chunk

		print u'\nLoaded %s as Bank' % fn


	def saveBankToFile(self,fn):
		'''saves this bank as an E352/E370-compatible file'''
		fout = wave.open(fn,'w')
		fout.setnchannels(1)
		fout.setsampwidth(2)
		fout.setframerate(44100)
		fout.setcomptype('NONE','Not Compressed')
		data = self.values()
		BinStr = ''
		for i in range(len(data)):
			BinStr = BinStr + struct.pack('h',data[i])
		fout.writeframesraw(BinStr)
		fout.close()

		print u'\nSaved bank as %s' % fn


