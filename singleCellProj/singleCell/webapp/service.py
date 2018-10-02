import os, sys, csv,json,datetime,time,math,scipy.stats, collections;
import re

import numpy as np;
import scipy as sp;
import math;
import linecache

from scipy.spatial import distance 
from scipy.stats import ranksums;

import pymongo;
from bson.objectid import ObjectId
from pymongo import MongoClient


from bson.json_util import dumps

import sklearn;

import pyRserve;
import base64;

import copy
import random
import operator


client = MongoClient('localhost', 9999);





db = client.singleCellDB;



def loginVerify(username,password):

	user = db.userInfo.find({"_id":username,"password":password})
	usercount = user.count();

	userrole ="";
	if usercount ==1:
		userrole = user[0]["role"];
	else:
		userrole ="";

	data = dict();
	data["role"]=userrole;
	data["count"]=usercount;

	return data;






def getMapDataBySampleId(sampleid):

	#sampleid = ObjectId(sampleid);
	
	tsneMetaCollection = "meta_"+sampleid;

	tsneMap = db[tsneMetaCollection].find({});

	tsneMap = list(tsneMap);

	return tsneMap;

def getAllSampleInfo(userid):
	data = db.dataInfo.find({},{"_id":1,"name":1,"study":1,"subjectid":1,"tissue":1,"disease":1,"source":1,"comment":1});
	resdata=[];
	for i in data:
		i["_id"]=str(i["_id"]);
		resdata.append(i);
	return resdata;


def getClusterInfo(sampleid):


	sampleid = ObjectId(sampleid);
	clstrs = db.cluster.find({"mapid":sampleid},{"_id":1,"clstrName":1,"clstrType":1,"color" :1, "x":1, "y" : 1, "label" : 1, "prerender" : 1,"marks":1});

	resclstrs=dict();
	for i in clstrs:
		clstrtype = i["clstrType"];
		idstr=str(i["_id"]);
		i["_id"]=idstr;
		if clstrtype in resclstrs:
			resclstrs[clstrtype].append(i);
		else:
			resclstrs[clstrtype]=[i];

	return resclstrs;


def getExprdataByGene(sampleid,gene):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	res =dict();

	for i in range(len(countexpr)):
		if countexpr[i] >0:
			res[i]=countexpr[i];


	return res;


def queryClstrType():
	clstrTypes = db.clusterType.distinct("_id");
	clstrTypes = list(clstrTypes);
	return clstrTypes;



def getGeneSearchPlotData(gene,sampleid):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	clusters = db.cluster.find({"mapid":ObjectId(sampleid)},{"cells":1,"clstrName" : 1, "clstrType":1,"_id":1,"color":1});

	res=[]
	for i in clusters:
		
		cid = str(i["_id"]);
		cells=i["cells"]
		clstrlen = len(cells);
		nonzeros=[];
		for pos in cells:
			expr_val = countexpr[pos];
			if expr_val >0:
				nonzeros.append(expr_val);

		if len(nonzeros)==0:
			nonzeros_mean = 0;
			nonzeros_median = 0;
			nonzeros_1percentile=0;
			nonzeros_3percentile=0;
			nonzeros_perc = 0;
			nonzeros_min = 0;
			nonzeros_max = 0;
		else:
			nonzeros_mean = np.mean(nonzeros);
			
			nonzeros_1percentile = np.percentile(nonzeros,25);
			nonzeros_median = np.percentile(nonzeros,50);
			nonzeros_3percentile = np.percentile(nonzeros,75);
			nonzeros_perc = len(nonzeros)/clstrlen;
			#print(nonzeros_1percentile);
			#print(nonzeros_median)
			#print(nonzeros_3percentile);
			
			iqr = nonzeros_3percentile-nonzeros_1percentile;
			nonzeros_min = nonzeros_1percentile-1.5*iqr;
			nonzeros_max = nonzeros_3percentile+1.5*iqr;

			p100=np.percentile(nonzeros,100);
			p0=np.percentile(nonzeros,0);
			if nonzeros_min < p0:
				nonzeros_min=p0

			if nonzeros_max > p100:
				nonzeros_max=p100


		res.append({"name":i["clstrName"],"color":i["color"],"ctype":i["clstrType"],"cid":cid,"mean":nonzeros_mean,"median":nonzeros_median,"perc":nonzeros_perc,"1q":nonzeros_1percentile,"3q":nonzeros_3percentile,"min":nonzeros_min,"max":nonzeros_max})
		#break;

	return res;





def getExprNormailizedataByGene(sampleid,gene):
	
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	res =[];
	for i in range(len(countexpr)):
		if countexpr[i] >0:
			res.append(i);
	
	return res;




def listExistsGenes(sampleid,genes):

	fitGenes= db["expr_"+sampleid].distinct("_id",{"_id":{"$in":genes}})

	return fitGenes;

def listExistsGenesRegex(sampleid,geneRegex):

	fitGenes= db["expr_"+sampleid].distinct("_id",{"_id":{"$regex":"^"+geneRegex,"$options": "i" }})
	
	return fitGenes;


def savecluster(sampleid,name,ctype,cells,comment,marks):

	sampleid = ObjectId(sampleid);

	color =getRandomColor();

	clstrcount = db.cluster.find({"mapid":sampleid,"clstrName":name,"clstrType":ctype}).count();

	if clstrcount == 0:
		comment = comment.strip();
		db.cluster.insert_one({"mapid":sampleid,"clstrName":name,"clstrType":ctype,"color":color,"cells":cells,"comment":comment,"x" : "", "y" : "", "label" : False, "prerender" : False,"marks":marks})
		clstr = db.cluster.find_one({"mapid":sampleid,"clstrName":name,"clstrType":ctype});

		clstr_id=str(clstr["_id"])
		return {"status":"success","cid":clstr_id,"color":color}

	else:

		return {"status":"failed"}



def getClusterCellsById(clstrid):
	clstrid = ObjectId(clstrid);
	clstrCells = db.cluster.find_one({"_id":clstrid},{"cells":1});
	clstrCells= clstrCells["cells"];
	return clstrCells;


def contrastCellsVsClstr(sampleid,cells,clstr):
	cell2 = getClusterCellsById(clstr);
	cell1= np.array(cells,dtype='i');
	
	data = contrast(sampleid,cell1,cell2);

	return data;


def queryClstrCellsAndLabelByCid(cid):
	cid = ObjectId(cid);
	clstr = db.cluster.find_one({"_id":cid},{"cells":1,"label":1,"x":1,"y":1,"clstrName":1});
	
	res=dict();
	res["cellids"]=clstr["cells"];
	res["name"] = clstr["clstrName"];
	res["labeled"]=clstr["label"];
	res["x"] = clstr["x"];
	res["y"]= clstr["y"];

	return res;








def getClusterClassification(clstrtype):

	data = db[clstrtype].find({});

	return list(data);


def getExprPosCountsByGene(sampleid,g1,g2):
	genexpr1 = db["expr_"+sampleid].find_one({"_id":g1},{"normalize":1})["normalize"];
	genexpr2 = db["expr_"+sampleid].find_one({"_id":g2},{"normalize":1})["normalize"];

	c1=0;
	c2=0;
	c3=0;
	d1=[];
	d2=[];
	d3=[];
	for i in range(len(genexpr1)):
		v1 = genexpr1[i];
		v2 = genexpr2[i];

		if v1>0 and v2 >0:

			c3+=1;
			d3.append(i);
		else:
			if v1>0:
				c1+=1;
				d1.append(i);

			if v2>0:
				c2+=1;
				d2.append(i);

	return {"g":[g1,g2,"intersc"],"c":[c1,c2,c3],"d1":d1,"d2":d2,"d3":d3}



def getExprPosCountByGene(sampleid,gene):
	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	count=0;
	for i in countexpr:
		if i >0:
			count+=1;


	return count;




def updateClusterPostition(clstrid,x,y):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"x":float(x),"y":float(y),"label":True}});
	return "success";

def updateClusterName(clstrid,name):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"clstrName":name}});
	return "success";

def deleteCluster(clstrid):
	res = db.cluster.remove({"_id":ObjectId(clstrid)});

	return "success";


def updateClusterMarks(clstrid,marks):
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"marks":marks}});

	return "success";


def updateClusterIsPreRender(clstrid,val):
	if val =='T':
		val =True;
	elif val =="F":
		val = False;
	res = db.cluster.update_one({"_id":ObjectId(clstrid)},{"$set":{"prerender":val}});
	return "success";





def contrast(sampleid,cells1,cells2):

	p=dict();
	n=dict();
	allexpr = db["expr_"+sampleid].find({},{"_id":1,"normalize":1});
	for i in allexpr:
		g = i["_id"];
		expr = i["normalize"];
		x=[];
		y=[];
		for j in cells1:
			x.append(expr[j])
		for j in cells2:
			y.append(expr[j])
		

		ranksumsres = scipy.stats.ranksums(x,y);	
		statics = ranksumsres[0];
		pval = ranksumsres[1];
			
		if pval < 0.01:
			if statics >=0:
				p[g]=pval;
			else:
				n[g]=pval;

	p = sorted(p.items(), key=lambda kv: kv[1] );
	n =	sorted(n.items(), key=lambda kv: kv[1] );

	p2=[];
	n2=[];
	for i in p:
		p2.append(i[0]);
	p=None;
	for i in n:
		n2.append(i[0]);
	n=None;
	return {"p":p2,"n":n2}


def contrastwithrest(sampleid,cells):

	

	#cells=np.array(cells,dtype="i");
	cellsdict= dict();
	for i in cells:
		cellsdict[int(i)]=None;



	p=dict();
	n=dict();

	allexpr = db["expr_"+sampleid].find({},{"_id":1,"normalize":1});
	for i in allexpr:
		g = i["_id"];
		expr = i["normalize"];
		x=[];
		y=[];
		for j in range(len(expr)):
			if j in cellsdict:
				x.append(expr[j])
			else:
				y.append(expr[j]);

		ranksumsres = scipy.stats.ranksums(x,y);
		
		statics = ranksumsres[0];
		pval = ranksumsres[1];

		
		
		if pval < 0.01:
			if statics >=0:
				p[g]=pval;
			else:
				n[g]=pval;

	p = sorted(p.items(), key=lambda kv: kv[1] );
	n =	sorted(n.items(), key=lambda kv: kv[1] );

	p2=[];
	n2=[];
	for i in p:
		p2.append(i[0]);
	p=None;
	for i in n:
		n2.append(i[0]);
	n=None;
	return {"p":p2,"n":n2}


def runRanksums(sampleid,arr,compareTargets):

	if compareTargets =='all':
		pass;
	else:
		print(compareTargets);





	return ""


def contrastGeneSearch(gene,cells1,cells2,sampleid,name1,name2):


	genexpr = db["expr_"+sampleid].find_one({"_id":gene},{"normalize":1});

	if genexpr == None:
		return None;
	countexpr= genexpr["normalize"];

	maxval =0;

	exprdict =dict();
	for i in range(len(countexpr)):
		if countexpr[i] >0:
			exprdict[i]=countexpr[i];
			if countexpr[i] > maxval:
				maxval	= countexpr[i];
	
	res=[];

	for i in [1,2]:
		if i ==1:
			cells=cells1;
			name=name1;
			color="orange";
		elif i ==2:
			cells=cells2;
			name=name2;
			color="steelblue";

		clstrlen = len(cells);
		nonzeros=[];
		for pos in cells:
			expr_val = countexpr[pos];
			if expr_val >0:
				nonzeros.append(expr_val);

		if len(nonzeros)==0:
			nonzeros_mean = 0;
			nonzeros_median = 0;
			nonzeros_1percentile=0;
			nonzeros_3percentile=0;
			nonzeros_perc = 0;
			nonzeros_min = 0;
			nonzeros_max = 0;
		else:
			nonzeros_mean = np.mean(nonzeros);
			
			nonzeros_1percentile = np.percentile(nonzeros,25);
			nonzeros_median = np.percentile(nonzeros,50);
			nonzeros_3percentile = np.percentile(nonzeros,75);
			nonzeros_perc = len(nonzeros)/clstrlen;
			#print(nonzeros_1percentile);
			#print(nonzeros_median)
			#print(nonzeros_3percentile);
			
			iqr = nonzeros_3percentile-nonzeros_1percentile;
			nonzeros_min = nonzeros_1percentile-1.5*iqr;
			nonzeros_max = nonzeros_3percentile+1.5*iqr;

			p100=np.percentile(nonzeros,100);
			p0=np.percentile(nonzeros,0);
			if nonzeros_min < p0:
				nonzeros_min=p0

			if nonzeros_max > p100:
				nonzeros_max=p100


		res.append({"name":name,"color": color,"mean":nonzeros_mean,"median":nonzeros_median,"perc":nonzeros_perc,"1q":nonzeros_1percentile,"3q":nonzeros_3percentile,"min":nonzeros_min,"max":nonzeros_max})
	

	return res,exprdict,maxval;



#import multiprocessing as mp;
#p1=mp.Process(target=runWilcoxon,args=(arr))
#p1.start();
#p1.join();


def getClusterRestCells(sampleid,cells):
	
	cellorders = db["meta_"+sampleid].find({},{"order":1});
	
	cellsdict=dict();
	for i in cells:
		cellsdict[i]=None;


	res=[];
	for i in cellorders:
		if i["order"] not in cellsdict:
				res.append(i["order"]);

	return res;




def strarrayToIntarray(cellstr):
	cells = np.array(cellstr.split(","),dtype='i');
	return list(cells);



def getRandomColor():
	r = lambda: random.randint(0,255);
	color = '#%02X%02X%02X' % (r(),r(),r());

	return color;






def getClusterNameById(cid):
	clstrid = ObjectId(cid);
	clstrName = db.cluster.find_one({"_id":clstrid},{"clstrName":1});
	clstrName= clstrName["clstrName"];
	return clstrName;












"""




def getPatientProfilerDataByGene(study,ppname,gene,isagg):

	pp=patientProfilerDB.meta.find_one({"scope":study,"name":ppname});

	tumorSamples = exprMatrixDB[study+"_meta"].distinct("order",{"grouplist.category":"TUMOR OR NORMAL","grouplist.group":"TUMOR"})
	normalSamples = exprMatrixDB[study+"_meta"].distinct("order",{"grouplist.category":"TUMOR OR NORMAL","grouplist.group":"NORMAL"})
	
	if len(tumorSamples) == 0 :
		tumorSamples = exprMatrixDB[study+"_meta"].distinct("order",{"grouplist.category":"TUMOR.OR.NORMAL","grouplist.group":"TUMOR"})
		normalSamples = exprMatrixDB[study+"_meta"].distinct("order",{"grouplist.category":"TUMOR.OR.NORMAL","grouplist.group":"NORMAL"})
	


	test_samples = pp["test_samples"];
	control_samples = pp["control_samples"];

	test_study = pp["test_study"];
	control_study = pp["control_study"];

	test_samples = exprMatrixDB[test_study+"_meta"].distinct("order",{"_id":{"$in":test_samples }});

	control_samples = exprMatrixDB[control_study+"_meta"].distinct("order",{"_id":{"$in": control_samples }});

	exprstr="$expr"
	if "isRNAseq":
		exprstr='$log2expr';

	aggEleAtarr=[];
	for i in tumorSamples:
		aggEleAtarr.append({"$arrayElemAt":[exprstr,i]});

	tumordt = exprMatrixDB[study].aggregate([
		{"$match":{"_id":gene}},
		{"$project":{"_id":0,"expr": aggEleAtarr}},
		{"$unwind":"$expr"},
		{"$sort":{"expr":1}}
	])

	tumor=[];
	for i in tumordt:
		tumor.append(round( i["expr"],3))


	aggEleAtarr=[];
	for i in normalSamples:
		aggEleAtarr.append({"$arrayElemAt":[exprstr,i]});

	normaldt = exprMatrixDB[study].aggregate([
		{"$match":{"_id":gene}},
		{"$project":{"_id":0,"expr": aggEleAtarr}},
		{"$unwind":"$expr"},
		{"$sort":{"expr":1}}

	])
	normal=[];
	for i in normaldt:
		normal.append(round( i["expr"],3))

	aggEleAtarr=[];
	for i in test_samples:
		aggEleAtarr.append({"$arrayElemAt":[exprstr,i]});

	testdt = exprMatrixDB[test_study].aggregate([
		{"$match":{"_id":gene}},
		{"$project":{"_id":0,"expr": aggEleAtarr}},
		{"$unwind":"$expr"},
		{"$sort":{"expr":1}}

	]);
	test = [];
	for i in testdt:
		test.append(round( i["expr"],3))

	aggEleAtarr=[];
	for i in control_samples:
		aggEleAtarr.append({"$arrayElemAt":[exprstr,i]});

	ctrldt = exprMatrixDB[control_study].aggregate([
		{"$match":{"_id":gene}},
		{"$project":{"_id":0,"expr": aggEleAtarr}},
		{"$unwind":"$expr"},
		{"$sort":{"expr":1}}
	]);

	ctrl = [];
	for i in ctrldt:
		ctrl.append(round( i["expr"],3));

	return {"s1":{"name":"Tumor" ,"values":tumor},
			"s2":{"name":"Normal","values":normal},
			"d":{"name":test_study ,"values":test},
			"n":{"name":control_study ,"values":ctrl}}


"""