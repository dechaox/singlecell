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

	gene = genestr.split(",")[0]
	data = service.getExprdataByGene(sampleid,gene);
	return JsonResponse({"res":data});

def getClusterCellids(request):
	sampleid = request.POST.get("sampleid");
	return JsonResponse({"res":sampleid});














