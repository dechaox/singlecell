import os, sys, csv,json,datetime,time,math,scipy.stats, collections;
import re

import numpy as np;
import scipy as sp;
import math;
import linecache

from scipy.spatial import distance 


import pymongo;
from bson.objectid import ObjectId
from pymongo import MongoClient


from bson.json_util import dumps

import sklearn;

import pyRserve;
import base64;

import copy


client = MongoClient('localhost', 9999);





db = client.singleCellDB;

def getMapDataBySampleId(sampleid):

	#sampleid = ObjectId(sampleid);
	
	tsneMetaCollection = "meta_"+sampleid;

	tsneMap = db[tsneMetaCollection].find({});

	tsneMap = list(tsneMap);

	return tsneMap;


def getClusterInfo(sampleid):


	sampleid = ObjectId(sampleid);
	clstrs = db.cluster.find({"mapid":sampleid},{"_id":1,"clstrName":1,"clstrType":1,"color" :1, "x":1, "y" : 1, "label" : 1, "prerender" : 1});

	resclstrs=dict();
	for i in clstrs:
		idstr=str(i["_id"]);
		i.pop("_id",None);
		resclstrs[idstr]= i;

		


	return resclstrs;








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