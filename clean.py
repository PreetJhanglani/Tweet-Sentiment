import re
import numpy as np
import pandas as pd



def GetHshtg(x):
	hsh = [re.findall(r'#.*?(?=\s|$)',str(x))]
	return hsh


def RmRt(x):
	twt = re.sub("RT @[\w]*:"," ",str(x))
	return twt

def RmAt(x):
	twt = re.sub("@"," ",str(x))
	return twt

def RmUrl(x):
    text =re.sub(r"http\S+"," ",str(x))
    return text

def RmScP(x):
	twt = re.sub(('[^A-Za-z0-9-#!\s]*[\U0001F600-\U0001F64F]+[\U0001F300-\U0001F5FF]+[\U0001F680-\U0001F6FF]+[\U0001F1E0-\U0001F1FF]+[\U00002702-\U000027B0]+[\U000024C2-\U0001F251]+|\n|/N|[,;:.()-+=_*&^%$]') ," " ,str(x))
	return twt

def RmNum(x):
	twt = re.sub("[\d]*","",str(x)) 
	return twt


def RmHshtg(x):
	twt = re.sub("#\W*"," ",str(x))
	return twt





