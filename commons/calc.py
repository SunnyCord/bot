from commons import diff_calc
import requests
from commons import pp_calc
import sys
from commons import b_info
import config as cfg
from commons.beatmap import Beatmap
key = cfg.OSU_API
def calc_pp(file_name, acc, mod_s, combo, misses):
	file = requests.get(b_info.main(file_name, key)).text.splitlines()
	map = Beatmap(file)
	if combo == 0 or combo > map.max_combo:
		combo = map.max_combo


	def mod_str(mod):
		string = ""
		if mod.nf:
			string += "NF"
		if mod.ez:
			string += "EZ"
		if mod.hd:
			string += "HD"
		if mod.hr:
			string += "HR"
		if mod.dt:
			string += "DT"
		if mod.ht:
			string += "HT"
		if mod.nc:
			string += "NC"
		if mod.fl:
			string += "FL"
		if mod.so:
			string += "SO"
		if mod.td:
			string += "TD"
		return string

	class mods:
		def __init__(self):
			self.nomod = 0,
			self.nf = 0
			self.ez = 0
			self.hd = 0
			self.hr = 0
			self.dt = 0
			self.ht = 0
			self.nc = 0
			self.fl = 0
			self.so = 0
			self.td = 0
			self.speed_changing = self.dt | self.ht | self.nc
			self.map_changing = self.hr | self.ez | self.speed_changing
		def update(self):
			self.speed_changing = self.dt | self.ht | self.nc
			self.map_changing = self.hr | self.ez | self.speed_changing
	mod = mods()

	def set_mods(mod, m):
			if m == "NF":
				mod.nf = 1
			if m == "EZ":
				mod.ez = 1
			if m == "HD":
				mod.hd = 1
			if m == "HR":
				mod.hr = 1
			if m == "DT":
				mod.dt = 1
			if m == "HT":
				mod.ht = 1
			if m == "NC":
				mod.nc = 1
			if m == "FL":
				mod.fl = 1
			if m == "SO":
				mod.so = 1
			if m == "TD":
				mod.td = 1

	if mod_s != "":
		mod_s = [mod_s[i:i+2] for i in range(0, len(mod_s), 2)]
		for m in mod_s:
			set_mods(mod, m)
			mod.update()

	mod_string = mod_str(mod)
	map.apply_mods(mod)
	diff = diff_calc.main(map)
	pp = pp_calc.pp_calc_acc(diff[0], diff[1], diff[3], acc, mod, combo, misses,1)
	title = map.artist + " - "+map.title + "["+map.version+"]" 
	if mod_string != "":
		title += "+" + mod_string
	title += " (" + map.creator + ")"
	return(f"{round(diff[2], 2)}\n{round(pp.pp, 2)}")
