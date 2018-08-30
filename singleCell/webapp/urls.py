from django.urls import path,re_path

from . import views

urlpatterns = [
	path('', views.index, name='index'),

	path("getMapDataBySampleId",views.getMapDataBySampleId,name='getMapDataBySampleId'),

	path("genelistSearch",views.genelistSearch,name='genelistSearch'),
	path("getClusterCellids",views.getClusterCellids,name='getClusterCellids'),
	path("savecluster",views.savecluster,name="savecluster"),
	path("queryClstrCellsByCid",views.queryClstrCellsByCid,name="queryClstrCellsByCid"),
	path("getSampleLists",views.getSampleLists,name="getSampleLists"),
	path("getClusterClassification",views.getClusterClassification,name="getClusterClassification"),
]
