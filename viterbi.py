#!/usr/bin/python

import sys,re, math, os
import collections

INIT_STATE = 'init'
FINAL_STATE = 'final'
OOV_SYMBOL = 'OOV'
A = collections.defaultdict(lambda: 0)
B = collections.defaultdict(lambda: 0)
Voc = collections.defaultdict(lambda: 0)
STATES = collections.defaultdict(lambda: 0)
words = []
V = collections.defaultdict(lambda: 0)
BACKTRACE = collections.defaultdict(lambda: 0)
verbose = 0
traceback = []

with open("my.hmm") as HMM:
	for line in HMM:
		if re.search("^trans\s", line):
			tokens = line.split()
			qq = tokens[1]
			q = tokens[2]
			p = float(tokens[3])
			# i.e. NN VBP
			trans_pairs = '%s %s' % (qq, q)
			A[trans_pairs] = math.log(p)
			STATES[qq] = 1
			STATES[q] = 1

		elif re.search("^emit\s", line):
			tokens = line.split()
			q = tokens[1]
			w = tokens[2]
			p = float(tokens[3])
			# i.e. VB PLAY
			emiss_pairs = '%s %s' % (q, w)
			B[emiss_pairs] = math.log(p)
			STATES[q] = 1
			Voc[w] = 1

with open("ptb.22.txt") as ptb:
	for sentence in ptb:
		words = sentence.split(' ')
		words = ['s'] + words
		#for word in sentence:
		#	words.append(word)
		V[str(0) + " " + INIT_STATE] = 0.0 # base case of the recurisve equations!
		#print (len(words))

		for i in range(1, len(words)): # work left to right ...
			# if a word isn't in the vocabulary, rename it with the OOV symbol
			if Voc[words[i]] == 0:
				if verbose:
					print >> sys.stderr, "OOV:  %s\n" % words[i]
				words[i] = OOV_SYMBOL

			for q in STATES: # q is the key
				for qq in STATES:
					#print (qq)
					A_pairs = '%s %s' % (qq, q)
					B_pairs = '%s %s' % (q, words[i])
					V_pairs = '%s %s' % (str(i-1), qq)
					if A_pairs in A and B_pairs in B and V_pairs in V:
						v = V[V_pairs] + A[A_pairs] + B[B_pairs]
						pair = '%s %s' % (str(i), q)
						if pair not in V or v > V[pair]:
							V[pair] = v
							BACKTRACE[pair] = qq
				if verbose:
					new_V_pairs = '%s %s' % (str(i), q)
					#print >> sys.stderr, "%s = %s %s\n" % (V[new_V_pairs], V[V_pairs], B[V_pairs])

		foundgoal = 0
		goal = 0
		for qq in STATES:
			pair = '%s %s' % (str(len(words)-1), qq)
			if A['%s %s' % (qq, FINAL_STATE)] != 0 and pair in V:
				v = V['%s %s' % (len(words)-1, qq)] + A["%s %s" % (qq, FINAL_STATE)]
				if (not foundgoal) or v > goal:
					goal = v
					foundgoal = 1
					q = qq
		#t = [q]
		t = []
		if foundgoal:
			for i in range(len(words)-1, 0, -1):
				t = [q] + t
				q = BACKTRACE[('%s %s' % (str(i), q))]
				#traceback.append(BACKTRACE['%s %s' % (str(i), q)])
		#if verbose:
		#	print >> sys.stderr, "%s\n" % (math.exp(goal))
		t = t[0:-1]
		if foundgoal:
			print (t)
			#print (traceback)
			#for i in range(1, len(traceback)):
			#	print(traceback[i])
		print()
