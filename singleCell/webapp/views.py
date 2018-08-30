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
	return JsonResponse({"res":data,"count":geneCount,"gene":gene});

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

	return JsonResponse({"result":data});





def queryClstrCellsByCid(request):

	cid = request.POST.get("cid");
	cellids = service.queryClstrCellsByCid(cid);


	return JsonResponse({"cellids":cellids});



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