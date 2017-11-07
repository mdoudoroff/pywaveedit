#!/usr/bin/env python
# encoding: utf-8

# Rudimentary example of fabricating a complete bank from scratch:
# - create a bank
# - loop through the tables
# 	- initialize all the values in the table (initValues)
#	- surgically set the values of particular positions (setValue)
# - save the bank

from Bank import Bank

bank = Bank()

for table in bank.tables():

	# set some initial values
	table.initValues(-32767)

	pulses = table.index()+1
	length = 256.0/pulses
	print '%s - pulses: %s, spacing: %s' % (table.index(), pulses, length)

	for x in range(pulses):
		pos = int(x*length)
		table.setValue(pos,32767)
		table.setValue(pos+1,32767)
		if pulses<=32:
			table.setValue(pos+2,32767)

bank.saveBankToFile('multiplier.wav')


