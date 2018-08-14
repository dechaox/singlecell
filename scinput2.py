

import os, sys, csv,json,datetime,time,math,scipy.stats, collections;
import re

import os.path


import pymongo;
from bson.objectid import ObjectId
from pymongo import MongoClient
import numpy as np;
from sklearn import preprocessing


from pymongo import IndexModel, ASCENDING, DESCENDING


client = MongoClient('localhost', 9999)


singleCellDB = client.singleCellDB;


argvlen = len(sys.argv)

if argvlen == 2:
	data=None;
	configfile = sys.argv[1];
	with open(configfile) as f:
		data = json.load(f)
	

	exprScalePath = data["exprScalePath"];
	exprCountPath = data["exprCountPath"];
	tsnepath = data["tsneCoorPath"];
	


	sdata=[];
	shead=[];

	cdata=[];
	chead=[];

	exprhead=[];
	exprheaddict=dict();
	
	iserror=False;
	if os.path.isfile(exprScalePath) and os.path.isfile(tsnepath) and os.path.isfile(exprCountPath):
		
		with open(exprScalePath) as f:
			csvf = csv.reader(f, delimiter=',');
			csvf = list(csvf)
			shead = csvf[0][1:];
			sdata=csvf[1:];

		

		with open(exprCountPath) as f:
			csvf = csv.reader(f, delimiter=',');
			csvf = list(csvf)
			chead = csvf[0][1:];
			cdata=csvf[1:];


		for i in range(len(chead)):
			if chead[i] != shead[i]:
				print("error scale file and count file have different cells");
				iserror = True;


			else:
				exprhead.append(chead[i]);



		for i in range(len(exprhead)):
			exprheaddict[exprhead[i]]=i;

	else:
		print("files not fit");
		iserror = True;


	if iserror == False:

		mapinfo=dict();
		mapinfo["name"]= data["MapName"];
		mapinfo["study"]=data["Study"];
		mapinfo["subjectid"]=data["SubjectID"];
		mapinfo["tissue"]=data["Tissue"];
		mapinfo["disease"]=data["Disease"];
		mapinfo["source"]=data["Source"];

		mapinfo["comment"]=data["Comment"];
		mapinfo["author"]=data["Author"];


		#s1. meta
		newmap = singleCellDB.dataInfo.insert(mapinfo);
		newmap = str(newmap);



		#s2 expr;
		exprCollection = "expr_"+newmap;

		exprdict=dict();

		ndata1=[];
		for i in cdata:
			temp=[];
			for x in i[1:]:
				x=int(x);
				temp.append(x)
			ndata1.append(temp);
			exprdict[i[0]]=dict();
			exprdict[i[0]]["count"]=temp;

		ndata1 = np.array(ndata1)
		ndata1 = ndata1.T;
		ndata1 = preprocessing.normalize(ndata1);
		ndata1 = ndata1.T;
		

		for i in range(len(cdata)):
			
			gene=cdata[i][0];
			tempdt = [];
			tempn = ndata1[i]
			for x in tempn:
				x=round(x*10000,4);
				if x==0:
					x=0;
				tempdt.append(x);
			exprdict[gene]["normalize"]=tempdt;


		for i in sdata:
			temp=[];
			for x in i[1:]:
				x=round(float(x),4);
				if x ==0:
					x=0;
				temp.append(x);

			exprdict[i[0]]["scale"]=temp;


		for i in exprdict:
			gene=i;

			singleCellDB[exprCollection].update({"_id":gene},{"$set":exprdict[i]},upsert=True);


		sdata=None;
		cdata=None;
		shead=None;
		chead=None;

		#s3 tsne;
		tsneCollection ='meta_'+newmap;
		clusterdict=dict();
		with open(tsnepath) as f:
			csvf = csv.reader(f, delimiter=',');
			csvf = list(csvf)
			head = csvf[0];
			coor = csvf[1:];
			for i in coor:
				temp={"_id":i[0],"x":round(float(i[1]),7),"y":round(float(i[2]),7),"order":exprheaddict[i[0]]  };

				tempclstr = i[3];
				if tempclstr in clusterdict:
					clusterdict[tempclstr].append(exprheaddict[i[0]])
				else:
					clusterdict[tempclstr] = [exprheaddict[i[0]]]

				singleCellDB[tsneCollection].insert(temp)


		#s4 cluster
		colorlist=["#CD5C5D","#BDB76B","#008000","#00008B","#FFA071","#696969","#00BFFF","#7CFC00","#E6E6FA","#FFD700","#FF0000","#FFC0CB","#2F4F4F","#FF1493","#FF4500","#008B8B"];
		indx=0
		for i in clusterdict:
			tempcolor = colorlist[indx];
			singleCellDB.cluster.insert({"mapid":ObjectId(newmap),"clstrName":"TBD"+i,"clstrType":"cellType","cells":clusterdict[i],"color":tempcolor,
									"x":"","y":"","label":False,"prerender":False});

			indx+=1;
			if indx == len(colorlist):
				indx=0;


	else:
		print("have error")


else:
	print("please input 1 config file");




		

		

		

			


"""				

		
		#s4 cluster;
		clusterMeanStdCollection = "clstrMeanStd"+newmap;

		


		for g in data3:
			sdt = data3[g];
			temp=dict();
			for i in clusterdict:
				name = "TBD"+i;
				cells=clusterdict[i];
				values=[];
				for x in cells:
					order = exprheaddict[x];
					val = sdt[order];
					values.append(val);

				std = round(np.std(values,ddof=1),4);
				mean = round(np.mean(values),4);
				temp["mean_"+name]=mean;
				temp["std_"+name]=std;

			singleCellDB[clusterMeanStdCollection].update({"_id":g},{"$set":temp},upsert=True);
"""