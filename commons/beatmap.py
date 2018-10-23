import math
import sys
class Beatmap:
	def __init__(self, file):
		self.searchfile = file
		self.main()
	def main(self):

		## Setting init beatmap values
		# Metadata
		self.title = None
		self.artist = None
		self.creator = None
		self.version = None

		# difficulty
		self.hp = 0
		self.cs = 0
		self.od = 0
		self.ar = 0
		self.sv = 0
		self.tick_rate = 1
		self.speed = 1

		# Combo
		self.num_circles = 0
		self.num_sliders = 0
		self.num_spinners = 0
		self.max_combo = 0
		self.num_objects = 0

		# Slider data
		class slider_data:
			def __init__(self, s_type, points, repeats, length):
				self.s_type = s_type
				self.points = points
				self.repeats = repeats
				self.length = length

		# Hit Object
		self.objects = []
		ho_num = 0
		class hit_object:
			def __init__(self,pos,time,h_type,end_time,slider):
				self.pos = pos
				self.time = time
				self.h_type = h_type
				self.end_time = end_time
				self.slider = slider


		# Timing points
		self.timing_points = []
		tp_num = 0
		class timing_point:
			def __init__(self,time,ms_per_beat,inherit):
				self.time = time
				self.ms_per_beat = ms_per_beat
				self.inherit = inherit

		# Some init variables
		tp_sec = False
		ho_time = False
		valid = False

		# Gathering Metadata
		def metadata(self,line):
			if "Title:" in line:
				self.title = line.split("Title:")[1].split("\r")[0].split("\n")[0]
				#print "Title: "+self.title
			elif "Artist:" in line:
				self.artist = line.split("Artist:")[1].split("\r")[0].split("\n")[0]
				#print "Artist: "+self.artist
			elif "Creator:" in line:
				self.creator = line.split("Creator:")[1].split("\r")[0].split("\n")[0]
				#print "Mapper: "+self.creator
			elif "Version:" in line:
				self.version = line.split("Version:")[1].split("\r")[0].split("\n")[0]
				#print "Dfifficulty: "+self.version
		# Gather difficulty -> remember to check for exceptions
		def difficulty(self,line):
			if "HPDrainRate:" in line:
				self.hp = float(line.split(":")[1].split("\n")[0])
				#print "HP: "+str(self.hp)
			elif "CircleSize:" in line:
				self.cs = float(line.split(":")[1].split("\n")[0])
				#print "CS: "+str(self.cs)
			elif "OverallDifficulty:" in line:
				self.ar = float(line.split(":")[1].split("\n")[0])
				self.od = float(line.split(":")[1].split("\n")[0])
				#print "OD: "+str(self.od)
			elif "ApproachRate:" in line:
				self.ar = float(line.split(":")[1].split("\n")[0])
				#print "AR: "+str(self.ar)
			elif "SliderMultiplier:" in line:
				self.sv = float(line.split(":")[1].split("\n")[0])
				#print "SV: "+str(self.sv)
			elif "SliderTickRate:" in line:
				self.tick_rate = float(line.split(":")[1].split("\n")[0])
				#print "TR: "+str(self.tick_rate)

		# Parse the tp object
		def tp_ptr(self,line):
			temp_tp = line.split("\r")[0].split("\n")[0].split(",")
			
			if temp_tp[0] != '':
				if len(temp_tp) < 3:
					self.timing_points.append(timing_point(temp_tp[0],temp_tp[1],0))
				else:
					self.timing_points.append(timing_point(temp_tp[0],temp_tp[1],temp_tp[6]))
				#print timing_points[tp_num].ms_per_beat

		# Parse the HO. This may take a while
		def ho_ptr(self,line):
			# Start to global stuff. Need to learn more about this
			# Split commas for each line which should be a hit object
			temp_tp = line.split("\r")[0].split("\n")[0].split(",")
			# Only if the line is not null do something
			if temp_tp[0] != '':
				# Set variables to send to hit object
				pos = [temp_tp[0],temp_tp[1]]
				time = temp_tp[2]
				h_type = temp_tp[3]
				end_time = 0
				slider = 0
				slider_true = 0
				if len(line.split("|")) > 1:
					slider_true = 1

				#Circle type
				if h_type == "1" or h_type == "5" or (slider_true == 0 and int(h_type) > 12):
					self.num_circles += 1
					h_type = 1
				#Slider type. Need to do some more math on sliders
				elif h_type == "2" or h_type == "6" or slider_true:
					#print "Found slider beginning analysis..."
					self.num_sliders += 1
					h_type = 2
					pos_s = []
					# split into pipeline for slider logic
					sl_line = line.split("\r")[0].split("\n")[0].split("|")
					sl_type = sl_line[0][len(sl_line[0])-1]
					sl_line = sl_line[1:]
					counter = 0
					# add first slider point
					pos_s.append(pos)
					# iterate line for the rest of the slider points
					for l_pos in sl_line:
						pos_s.append([l_pos.split(":")[0],l_pos.split(":")[1].split(",")[0]])
						if len(l_pos.split(",")) > 2:
							break
					repeats = float(l_pos.split(",")[1])
					length = float(l_pos.split(",")[2])
					#print "Repeats: "+repeats+" Length: "+length+" Points: "
					#print pos_s
					time_p = self.timing_points[0]
					parent = self.timing_points[0]
					# Get timing point
					for tp in self.timing_points:
						if float(tp.time) > float(time):
							break
						time_p = tp
					# Get the parent point
					for tp in self.timing_points:
						if int(tp.inherit) == 1:
							parent = tp
						if tp == time_p:
							break
					# Begin to calculte the amount of ticks for max combo
					sv_mult = 1
					if time_p.inherit == "0" and float(tp.ms_per_beat) < 0:
						sv_mult = (-100.0 / float(time_p.ms_per_beat))
					px_per_beat = self.sv * 100.0 * sv_mult
					num_beats = (length * repeats) / px_per_beat
					duration = math.ceil(num_beats * float(parent.ms_per_beat))
					end_time = float(time) + duration
					slider = slider_data(sl_type,pos_s,repeats,length)
					ticks = math.ceil((num_beats - 0.1) / repeats * self.tick_rate)
					ticks -= 1
					raw_ticks = ticks
					ticks *= repeats
					ticks += repeats + 1
					self.max_combo += ticks - 1




				#Spinner type.
				elif h_type == "8" or h_type == "12":
					self.num_spinners += 1
					h_type = 3
				else:
					print("HELP "+h_type)
				self.num_objects += 1
				self.max_combo += 1
				self.objects.append(hit_object(pos,time,h_type,end_time,slider))

		# Begin to parse beatmap
		try:
			for line in self.searchfile:
				# Gather metadata
				metadata(self,line)
				# Gather Difficulty information
				difficulty(self,line)
				#print "AR: "+str(self.ar)
				if ho_time:
					ho_ptr(self,line)
					ho_num += 1
				if "[HitObjects]" in line:
					ho_time = True
				if "osu file format v" in line:
					valid = True
				if "Mode: 1" in line or "Mode: 2" in line or "Mode: 3" in line:
					valid = False
				# Section for timing points
				if tp_sec:
					tp_ptr(self,line)
					tp_num += 1
				if "[TimingPoints]" in line:
					tp_sec = True
				if tp_sec and (line == "\n" or line == "\r\n" or line == ""):
					tp_sec = False
			#print "Circles: "+str(self.num_circles)+" Sliders: "+str(self.num_sliders)+" Spinners: "+str(self.num_spinners)
			#print "Max combo: "+str(self.max_combo)
			if valid != True:
				print("ERROR: Unsupported gamemode")
				raise()
		except:
			print("ERROR: Processing beatmap failed")
			sys.exit(1)
	def apply_mods(self,mods):
		# Ugly shouldput somewhere else
		od0_ms = 79.5
		od10_ms = 19.5
		ar0_ms = 1800
		ar5_ms = 1200
		ar10_ms = 450

		od_ms_step = 6.0
		ar_ms_step1 = 120.0
		ar_ms_step2 = 150.0
		
		if mods.map_changing == 0:
			return

		speed = 1

		if mods.dt or mods.nc:
			speed *= 1.5

		if mods.ht: 
			speed *= 0.75

		self.speed = speed

		od_multiplier = 1

		if mods.hr:
			od_multiplier *= 1.4

		if mods.ez:
			od_multiplier *= 0.5

		self.od *= od_multiplier
		odms = od0_ms - math.ceil(od_ms_step * self.od)

		ar_multiplier = 1

		if mods.hr:
			ar_multiplier = 1.4

		if mods.ez:
			ar_multiplier = 0.5

		self.ar *= ar_multiplier

		arms = (ar0_ms - ar_ms_step1 * self.ar) if self.ar <= 5 else (ar5_ms - ar_ms_step2 * (self.ar-5))

		cs_multipier = 1

		if mods.hr:
			cs_multipier = 1.3

		if mods.ez:
			cs_multipier = 0.5

		odms = min(od0_ms, max(od10_ms,odms))
		arms = min(ar0_ms,max(ar10_ms,arms))

		odms /= speed
		arms /= speed

		self.od = (od0_ms - odms) / od_ms_step

		self.ar = ((ar0_ms - arms) / ar_ms_step1) if self.ar<= 5.0 else (5.0 + (ar5_ms - arms) / ar_ms_step2)
		self.cs *= cs_multipier
		self.cs = max(0.0,min(10.0,self.cs))

		if mods.speed_changing == 0:
			return

		for tp in self.timing_points:
			tp.time = float(tp.time)
			if int(tp.inherit) == 0:
				tp.ms_per_beat = float(tp.ms_per_beat)


		for obj in self.objects:
			obj.time = float(obj.time)
			obj.end_time = obj.end_time

