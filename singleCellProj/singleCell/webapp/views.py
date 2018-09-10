from django.shortcuts import render
from json_render import json_render
import json
import os;
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect

# Create your views here.

from . import service;




# C""reate your views here.
def index(request):


	return render(request,"index/index.html");


def userLogin(request):
	username = request.POST.get("username");
	password = request.POST.get("password");
	data = service.loginVerify(username,password);
	
	status = "";
	if data["count"] ==1:
		status="success";
	else:
		status ="failed"

	return JsonResponse({"status":status,"role":data["role"]});

def getMapDataBySampleId(request):
	
	sampleid = request.POST.get("sampleid");

	data = service.getMapDataBySampleId(sampleid);
	clstrInfo = service.getClusterInfo(sampleid);

	return JsonResponse({"tsneData":data,"clstr":clstrInfo});



def genelistSearch(request):
	sampleid = request.POST.get("sampleid");
	genestr = request.POST.get("genestr");

	gene = genestr.replace(" ","");
	gene = gene.split(",");
	
	gene2=[];
	for i in gene:
		if len(i) > 0:
			gene2.append(i.upper());


	data="";
	geneCount=0;
	gene="";
	if len(gene2) >1:
		data = service.listExistsGenes(sampleid,gene2);
		geneCount = len(data);
		if geneCount == 1:
			gene = data[0];
			data = service.getExprdataByGene(sampleid,data[0]);
			
	elif len(gene2) == 1:
		gene2=gene2[0];
		lastWord = gene2[-1];
		if lastWord == "*":
			data = service.listExistsGenesRegex(sampleid,gene2[0:-1]);
			geneCount = len(data);
			if geneCount == 1:
				gene = data[0];
				data = service.getExprdataByGene(sampleid,data[0]);
				
		else:
			data = service.getExprdataByGene(sampleid,gene2);
			gene=gene2;
			if data== None:
				geneCount=0;
			else:
				geneCount=1;
	maxval=0;
	if geneCount==1:
		for i in data:
			if data[i] > maxval:
				maxval =data[i];

	return JsonResponse({"res":data,"count":geneCount,"gene":gene,"maxval":maxval});

def getClusterCellids(request):
	sampleid = request.POST.get("sampleid");
	return JsonResponse({"res":sampleid});



def savecluster(request):
	sampleid = request.POST.get("sampleid");
	name = request.POST.get("name");
	ctype = request.POST.get("type");
	comment = request.POST.get("comment");
	cells = request.POST.get("cells");
	cells = cells.split(",");
	cells2 = [];
	for i in cells:
		cells2.append(int(i));
	data = service.savecluster(sampleid,name,ctype,cells2,comment);

	return JsonResponse(data);





def queryClstrCellsAndLabelByCid(request):

	cid = request.POST.get("cid");
	data = service.queryClstrCellsAndLabelByCid(cid);


	return JsonResponse(data);



def getSampleLists(request):
	userid = request.POST.get("userid");

	samples = service.getAllSampleInfo(userid);
	
	jsonres=dict();
	jsonres["samples"]=samples;

	return JsonResponse(jsonres)



def getClusterClassification(request):

	clstrType= request.POST.get("clstrType");

	data = service.getClusterClassification(clstrType);

	return JsonResponse({"clstrTypes":data})


def updatecluster(request):
	target = request.POST.get("target");
	clstrid = request.POST.get("clstrid");

	if target == "POS":
		x = request.POST.get("x");
		y = request.POST.get("y");
		
		res = service.updateClusterPostition(clstrid,x,y);
	elif target =="NAME":
		newname = request.POST.get("name");
		res = service.updateClusterName(clstrid,newname);
	elif target =="prerender":
		val = request.POST.get("val");
		res = service.updateClusterIsPreRender(clstrid,val);

	return JsonResponse({"res":res});


def deleteCluster(request):
	clstrid = request.POST.get("clstrid");
	res = service.deleteCluster(clstrid);

	return JsonResponse({"res":res});

