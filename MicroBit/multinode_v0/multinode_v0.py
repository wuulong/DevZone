# Microbit Radio multi-node bi-direction communication test
# Licence: MIT
# Limited memory coding style, doc in the same folder
from microbit import *
import radio as ro
import utime as ut
import random as rn
from microbit import display as di

class Comm():
	def __init__(self):
		self.sid = 0
		self.ack = "~"
		self.txc = 0#tx_cnt
		self.rxc = 0#rx_cnt
		self.txnc = 0#tx_new_cnt
		self.rxnc = 0#rx_new_cnt
		self.ackc = 0#ack_cnt
		self.uids = [] #used_ids
		self.uidsn = [] #used_ids_next
		self.ackd = False#ack_received
		ro.config(queue=6,address=0x75626972,channel=4,data_rate=ro.RATE_1MBIT)
		ro.on()
		sleep(100)
	def tx(self,did,value):
		self.txc += 1
		tx_txt = "%i:%i:%s" %(self.sid,did,str(value))
		ro.send(tx_txt)
		self.leds(1,self.txc)
	def gnid(self,used_ids):#get_new_id
		while True:
			id = rn.randint(1, 20)
			if not id in used_ids:
				break
		return id

	def wait_start(self):
		while True:
			if button_a.was_pressed():
				di.show("F")
				self.uids = self.find_used_ids()
				self.sid = self.gnid(self.uids)
				self.show_id()
				break
	def show_id(self):
		di.clear()
		sid = self.sid - 1
		di.set_pixel(sid%5,int(sid/5),9)
		for id in self.uids:
			if id>0:
				uid = id - 1
				di.set_pixel(uid%5,int(uid/5),5)
	def find_used_ids(self):
		used_ids=[]
		t_s = ut.ticks_us()

		while True: # start current measurement
			t_now = ut.ticks_us()
			t_use = ut.ticks_diff(t_now,t_s)
			if 1500000 - t_use <0: # 1.5s
				#di.show("W")
				break
			incoming = ro.receive()
			if incoming:
				items = incoming.split(":")
				if len(items)==3:
					did = int(items[1])
					if not (did in used_ids):
						used_ids.append(did)
		return used_ids

	def leds(self,part,value):#pixel_debug
		if part==1: # 1 LED at bottom-right
			value = value *3 % 10
			di.set_pixel(4, 4, value)
		else: #4 LED
			value = value % 40
			for i in range(4):
				if value >=9:
					di.set_pixel(i, 4, 9)
				elif value<0:
					di.set_pixel(i, 4, 0)
				else:
					di.set_pixel(i, 4, value)
				value -=10

	def bi_tran(self):
		cur_num_tx = 0
		self.wait_start()

		while True:
			self.rxc = 0
			self.rxnc = 0
			self.txc = 0
			self.txnc = 0
			self.ackc = 0
			tp = 1 #test_period s
			t_tick = int(tp * 1000000)

			t_s = ut.ticks_us()
			t_l = t_s

			#broadcast device exist every test period
			self.tx(0,str(0))
			# rate target hz
			rate_target = rn.randint(1, 100)
			send_tick = int(t_tick/rate_target)


			while True: # start current measurement
				t_now = ut.ticks_us()
				t_use = ut.ticks_diff(t_now,t_s)
				if t_tick - t_use <0: # 10s
					self.uids = self.uidsn
					self.show_id()
					self.uidsn = []
					break

				t_last = ut.ticks_diff(t_now,t_l)
				if send_tick - t_last <0: # should send
					t_l = t_now
					if self.ackd:
						cur_num_tx = cur_num_tx+1
					self.ackd = False
					if len(self.uids)>0:
						index = rn.randint(0, len(self.uids)-1)
						did = self.uids[index]
						self.tx(did,cur_num_tx)
						self.txnc += 1

				incoming = ro.receive()
				if incoming:
					self.rxc+=1
					items = incoming.split(":")
					if len(items)==3:

						sid,did,value = items
						sid = int(sid)
						did = int(did)
						if not sid in self.uids:
							self.uids.append(sid)
							self.show_id()

						if not sid in self.uidsn:
							self.uidsn.append(sid)

						if sid == self.sid: # sid collision
							self.sid = self.gnid(self.uids)
							self.show_id()

						if did == self.sid:
							if value == self.ack:
								self.ackd = True
								self.ackc += 1
							else:
								self.rxnc += 1
								self.tx(sid,self.ack)
							#ro.send ("%i:%i:%s"%(self.sid,sid,self.ack))

					self.leds(0,self.rxc)
				if button_b.was_pressed(): # test sid collision
					if len(self.uids)>0:
						self.sid = self.uids[0]
					else:
						self.sid = rn.randint(1, 20)
					break
			tx_rate = float(self.txnc)/tp
			rx_rate = float(self.rxnc)/tp
			str_output = "(%.1f,%.1f,%i)" %(tx_rate, rx_rate, self.txnc - self.ackc)

			print(str_output)

comm = Comm()
comm.bi_tran()