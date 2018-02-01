import os
import subprocess
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
test_path = os.path.join(dir_path, 'test_primjeri')
out_path = os.path.join(dir_path, 'test_out')
sem_an_path = os.path.join(dir_path, 'SemantickiAnalizator.py')

correct: int = 0
all: int = 0

for dir in os.listdir(test_path):
	file_in = test_path + "/" + dir + "/" + "test.in"
	file_real_out = test_path + "/" + dir + "/" + "test.out"
	file_out = out_path + "/" + dir + "/" + "out"
	if not os.path.exists(out_path + "/" + dir):
		os.makedirs(out_path + "/" + dir)
	f = open(file_out, "w+")
	process = subprocess.Popen(sem_an_path + " " + file_in, shell=True, stdout=f)
	process.wait()
	f.close()
	
	expected = open(file_real_out, "r").read().strip()
	got = open(file_out, "r").read().strip()
	
	all = all + 1
	if expected == got:
		correct = correct + 1

		
if correct < all:
	sys.exit(1)
else:
	sys.exit(0)