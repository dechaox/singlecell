

//basic configs
var defaultNodeColor ="#A9A9A9";
var softNodeColor="#ff66ff";
var softNodeColor2 = "#31D8E2";
var NodeHoverColor ='#ff6f00';
var NodeHoverFriendsColor = "#ffc107"
//basic config end;
var defaultR=5;

var svgZoom;
var svgDrag;

var cactMainSvg;

var mainXscale;
var mainYscale;


var mainWidth;
var mainHeight;
var ori_coords = [];
var mainTransform;
var selectednodes;

var contourDensity = d3.contourDensity();


function initD3selections(){

	d3.selection.prototype.moveToFront = function() {  
		return this.each(function(){
			this.parentNode.appendChild(this);
		});
	};
	d3.selection.prototype.moveToBack = function() {
		return this.each(function() { 
			var firstChild = this.parentNode.firstChild; 
			if (firstChild) { 
				this.parentNode.insertBefore(this, firstChild); 
			}
		});
	};

}



function initToolTips(){





}




function drawTsneMap(div_id,nodes,labels,clstrcolor){

	initToolTips();
	initD3selections();

	var width = $(div_id).width();
	var height = $(div_id).height();

	if(width === undefined || width === null){
		width=700;
	}
	if(height === undefined || height === null){
		height=700;
	}
 	

	

	var margin = {top: 50, right: 50, bottom: 50, left:50};
	width = width - margin.left - margin.right;
	height = height - margin.top - margin.bottom;

	mainWidth = width;
	mainHeight = height;


	cactMainSvg = d3.select(div_id).append('svg').attr("id","mainsvg")
		.attr('width', width + margin.left + margin.right)
		.attr('height', height + margin.top + margin.bottom);


	//cactMainSvg.append("rect").attr("width",width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom).style("fill",'c7dbf9');

	cactMainSvg.append("g").attr("id","svgcontour");
	cactMainSvg.append("g").attr("id","svgcontour2");

	var graph_length=height;
	if(width<graph_length){
		graph_length = width;
	}

	var xrange=[0,0];
	var yrange=[0,0];
	
	for(var i in nodes){
		let tempx = nodes[i].x;
		let tempy = nodes[i].y;
		
		if(tempx < xrange[0]){
			xrange[0]=Math.floor(tempx);
		}else if(tempx > xrange[1]){
			xrange[1]=Math.ceil(tempx);
		}

		if(tempy < yrange[0]){
			yrange[0]=Math.floor(tempy);
		}else if(tempy > yrange[1]){
			yrange[1]=Math.ceil(tempy);
		}

	}



	xrange[0]=xrange[0]-1;
	xrange[1]=xrange[1]+1;

	yrange[0]=yrange[0]-1;
	yrange[1]=yrange[1]+1;

	var xScale = d3.scaleLinear()
	.domain(xrange)
	.range([0, graph_length]);



	var yScale = d3.scaleLinear()
	.domain(yrange)
	.range([graph_length, 0]);

	mainXscale = xScale;
	mainYscale = yScale;


	$(div_id).css("background","#f7f7f7");

	var gene_node = cactMainSvg.selectAll('.node')
	.data(nodes)
	.enter().append('circle')
	.attr("id", function(d){return d.gene;})
	.attr('class', 'node')
	.attr("scope","base")
	.attr("ox",function(d){return d.x;})
	.attr("oy",function(d){return d.y;})
	.attr('cx', function(d){return xScale(d.x);})
	.attr('cy', function(d){return yScale(d.y);})
	//.attr('cy', function(d){ return yScale(d.Y); })
	.attr('r', defaultR)
	.attr("init",function(d){if(d.gene in clstrcolor){return  clstrcolor[d.gene];}else{ return defaultNodeColor;} } )
	.style('fill', function(d){if(d.gene in clstrcolor){return  clstrcolor[d.gene];}else{ return defaultNodeColor;} } )
	.style("fill-opacity",0.5)
	.style("stroke","white")
	.style("stroke-width","0.5");



	contourDensity.x(function(d) { return mainXscale(d.x); })
            .y(function(d) { return mainYscale(d.y); })
            .size([mainWidth,mainHeight])
            .bandwidth(14);

    var contourDensityValue = contourDensity(nodes);


    d3.select("#svgcontour2").selectAll(".contourpath")
        .data(contourDensityValue)
        .enter().append("path")
          .attr("class","contourpath contour")
          .style("fill","none")
          .style("stroke","#000")
          .style("stroke-width",0.5)
          .attr("d", d3.geoPath());



	labeldt =[];
	//var initcoor =[];

	for(var i in labels){
		let templb =labels[i];
		labeldt.push({"name":i,x:templb["labelPos"][0],y:templb["labelPos"][1],"_id":templb["_id"]})

		//initcoor.push(templb["coors"])
	}



	//cactMainSvg.append("path").attr("class","node_done_path").attr("d", selectedline(coords ) );

	var clstrlabels = cactMainSvg.selectAll(".clusterLabel")
		.data(labeldt)
		.enter().append("text")
		.text(function(d){ return d.name})
		.attr("class","clusterLabel")
		.attr("lbid",function(d){return d._id;})
		.attr("x",function(d){return xScale(d.x)})
		.attr("y",function(d){return yScale(d.y)})
		

	$(".clusterLabel").click(function(){
		var thisele = $(this);
		var name = $(this).text();
		$("#defaultModal").find(".modal-title").html("");
		$("#defaultModal").find(".modal-body").html("delete cluster label? <a class='btn btn-sm btn-danger' name='yestodelclstr'>Yes</a><a class='btn btn-sm btn-primary'  data-dismiss='modal'>No</a>");          
        $("#defaultModal").find(".modal-footer").html("");

        $('#defaultModal').modal('show');
        var thislbid = $(this).attr("lbid");

        $("#defaultModal").find("[name='yestodelclstr']").click(function(){

        	$.ajax({
        		url:"/dataManager/deleteLabel",
                data:{"lbid":thislbid},
                dataType: "json",
                method:"post",
                success:function(result){
                	$("#defaultModal").find(".modal-body").html("success");
                	thisele.remove();
                }

        	})

        })

	})


	labeldt =null;


    nodes=null;


    d3.selectAll(".node").on("mouseover", handleMouseOverNode)
    .on("mouseout", handleMouseOutNode)
    .on("click", handleClickNode);



	function zoomed() {
		var transform = d3.event.transform;
		mainTransform = transform;
		//translate(-15.404482967761254,5.436876341562794) scale(1)


		//var k = transform.k;
		//var x = transform.x;
		//var y = transform.y;
		d3.selectAll(".node").attr("cx", function(d) {
			return transform.applyX(xScale(d.x));
		}).attr("cy", function(d) {
			return transform.applyY(yScale(d.y));
		});

		d3.select("#svgcontour").attr("transform", d3.event.transform);
		d3.select("#svgcontour").selectAll(".contourpath").style("stroke-width", 0.5 / d3.event.transform.k + "px");

		d3.select("#svgcontour2").attr("transform", d3.event.transform);
		d3.select("#svgcontour2").selectAll(".contourpath").style("stroke-width", 0.5 / d3.event.transform.k + "px");



		d3.selectAll(".genelabel").each(function(d){

			let gene = d3.select(this).text();

			genenode = d3.select("#"+gene);
			let tempx = Number(genenode.attr("cx"));
			let tempy = Number(genenode.attr("cy"));

			d3.select(this).attr("x",tempx+5).attr("y",tempy+3);


		});

		clstrlabels.attr("x", function(d) {
			return transform.applyX(xScale(d.x));
		}).attr("y", function(d) {
			return transform.applyY(yScale(d.y));
		});
	}


	svgZoom = d3.zoom().scaleExtent([1 / 160, 160]).on("zoom", zoomed);

	cactMainSvg.call(svgZoom);

	
	selectednodes=[];
	var coords=[];
	var selectedline = d3.line();
	var dragStart = function() {
		gene_node.classed("selected", false);

		coords = [];
			 
		d3.selectAll(".node_draw_path").remove();
		d3.selectAll(".node_done_path").remove();
			
		gene_node.style("stroke","white").style("stroke-width",0.5);
			
		$("[name='saveSelectedGenesDiv']").html("");
	}

	var drawPath = function(isdone) {
		if(coords.length>1){


			cactMainSvg.append("path").attr("class",'node_draw_path').attr( "d",selectedline([coords[coords.length-2],   coords[coords.length-1] ]));

			if (isdone) {

				coords = coords.concat([coords[0]]);

				ori_coords=[];
				if(mainTransform!==undefined){
					for(var ii in coords){
						var tempx = mainTransform.invertX(coords[ii][0]);
						var tempy = mainTransform.invertY(coords[ii][1]);
						var tempx = mainXscale.invert(tempx);
						var tempy = mainYscale.invert(tempy);

						ori_coords.push([tempx,tempy]);

					}
                }else{

                	for(var ii in coords){
	                	var tempx = mainXscale.invert(coords[ii][0]);
	                	var tempy = mainYscale.invert(coords[ii][1])
						ori_coords.push([tempx,tempy]);
	                }
                }



				cactMainSvg.append("path").attr("class","node_done_path").attr("d", selectedline(coords ) );

				cactMainSvg.selectAll(".node_draw_path").remove();


				gene_node.each(function(d, i) {
					point = [d3.select(this).attr("cx"), d3.select(this).attr("cy")];
					if (pointInPolygon(point, coords)) {
						d3.select(this).classed("selected", true)
					}

				});

				selectPath();
			}

		}
	}
 
	var selectPath = function(){


		let templen =$(".node.selected").length;

		if(templen>0){

			selectednodes = [];
			$(".node.selected").each(function(){
				selectednodes.push($(this).attr("id"));
				
				$(this).css("stroke","black").css("stroke-width",1);;
			})

			execafterselected();

			
		}else{
			$(".node").css("stroke","white").css("stroke-width",0.5);
				//$("[name='cellselectinfo']").html("");
			dragStart();

		}
	}

	var dragMove = function() {
		gene_node.classed("selected", false);
		let tempcoord = d3.mouse(this);


		//tempcoord[0] = tempcoord[0]-gtranslate[0];
		//tempcoord[1] = tempcoord[1]-gtranslate[1];
		
		tempcoord[0] = tempcoord[0];
		tempcoord[1] = tempcoord[1];
		if(coords.length>0){
			let lastcoord = coords[coords.length-1];
			if(Math.abs(lastcoord[0]-tempcoord[0])+ Math.abs(lastcoord[1]-tempcoord[1]) >2){
				coords.push(tempcoord);
				drawPath();

			}
		}else{
			coords.push(tempcoord);
			drawPath();
		}

	}
		

	var dragEnd = function() {
		drawPath(true);

	}


		
	svgDrag = d3.drag().on("start", dragStart).on("drag", dragMove).on("end", dragEnd);
	//svg.call(svgDrag)

	/*
	for(var i in initcoor){

		var tempcoor = initcoor[i]
		var temp = [];

		for(var i in tempcoor){
			temp.push([mainXscale(tempcoor[i][0]) ,mainYscale(tempcoor[i][1])   ])
		}
 	
		cactMainSvg.append("path").attr("d", selectedline(temp ) ).style("stroke","blue").style("fill","none");

	}
	*/


}






function handleClickNode(){


		let gene = d3.select(this).attr("id");

		//let tempx = Number(d3.select(this).attr("cx"));
		//let tempy = Number(d3.select(this).attr("cy"));
		
		d3.select("#nodetooltip")
		.style("left", (d3.event.pageX) + "px")
		.style("top", (d3.event.pageY - 28) + "px");



		$("#nodetooltip").find("[name='genetitle']").html(gene);

		$("#nodetooltip").find("[name='druginfo']").html("");

		if(gene in druglist){

			let drugs = druglist[gene];

			var drugstr ="<span style='font-size:14px;margin-left:18px;'>Drugs:</span><ul>";
			
			for(d in drugs){

				drugstr += "<li>"+drugs[d].toLowerCase()+"</li>";

			}

			drugstr +="</ul>";

			$("#nodetooltip").find("[name='druginfo']").html(drugstr);

		}

		if(controlModel === "PatientProfiler"){
			$("#nodetooltip").find("[name='sendcorrtolist']").hide();

			if($("#PatientProfiler").find("[name='patientprofilersetChoose'].fa-dot-circle").length ===1){

			
				$("#nodetooltip").find("[name='viewViolinPlot']").show();

			}else{

				$("#nodetooltip").find("[name='viewViolinPlot']").hide();
			}
		}else{

			$("#nodetooltip").find("[name='viewViolinPlot']").hide();
			$("#nodetooltip").find("[name='sendcorrtolist']").show();
			
		}




		$("#nodetooltip").show();


		
		

}




function handleMouseOverNode(){

		if(controlModel === "TargetExplorer"){

			let gene = d3.select(this).attr("id").toString();

			let tempx = Number(d3.select(this).attr("cx"));
			let tempy = Number(d3.select(this).attr("cy"));
			let tempr = Number(d3.select(this).attr("r"));
			let tempColor = d3.select(this).style("fill");

			//d3.select(this).attr("r",tempr+4).style("fill",NodeHoverColor).style("fill-opacity",1);
			d3.select(this).attr("r",tempr+1).attr("oldfill",tempColor).style("fill",NodeHoverColor).style("fill-opacity",1).moveToFront();


			cactMainSvg.append("text").attr("temptext",gene).text(gene)
				.attr("x",tempx+15).attr("y",tempy+3).style("font-size","12").style("stroke","black").style("stroke-width",0.4);


			//friends
			let friends= corrData[gene];

			//NodeHoverFriendsColor

			for(let g in friends){

				let tempele = $("#"+g);
				let tempx = tempele.attr("cx");
				let tempy = tempele.attr("cy");
				let tempColor = tempele.css("fill");
				let tempopacity = tempele.css("fill-opacity");
				tempele.attr("oldfill",tempColor).attr("oldopacity",tempopacity).css("fill",NodeHoverFriendsColor).css("fill-opacity",1);



			}


		}else if(controlModel === "PatientProfiler"){
			let gene = d3.select(this).attr("id");

			let tempx = Number(d3.select(this).attr("cx"));
			let tempy = Number(d3.select(this).attr("cy"));
			let tempr = Number(d3.select(this).attr("r"));
			
			let zs = d3.select(this).attr("zs");
			



			d3.select(this).attr("r",tempr+2).moveToFront();
			if(zs !== null && zs !== ""){


				let textColor = "black";

				let ppaggcheckclz = $("#PatientProfiler").find("[name='isaggsamplescheck']").attr("class");

				let ppaggmethod = $("#PatientProfiler").find("[name='sampleaggcontrol2']").find(".fa-dot-circle.radio").attr("name");

				if( (ppaggcheckclz === "far fa-square") || (ppaggmethod==="MeanSamples") ){

					let zslist = zs.split(",");
					
					if(zslist.length===1){

						zs = Number(zslist[0]);
						if(zs>0){
							textColor = "red";
							zs= " +"+zs;
						}else{

							textColor = "blue";
							zs= " "+zs;
							
						}

						

					}


				}else{
					let zslist = zs.split(",");
					
					if(zslist.length===1){

						zs = Number(zslist[0]);
						if(zs>0){
							textColor = "red";
							zs= " +"+zs+"%";
						}else{

							textColor = "blue";
							zs= " "+zs+"%";
						}

						

					}else if(zslist.length===2){

						textColor = "green";

						zs = " +"+zslist[0]+"%"+" , "+zslist[1]+"%";


					}





				}

				

				$("#mainsvg").find(".genelabel[gene='"+gene+"']").hide();

				let temptext = cactMainSvg.append("text").attr("temptext",gene).text(gene+" "+zs)
					.attr("x",tempx+15).attr("y",tempy+3).style("font-size","14")
					//.style("font-weight","bold").style("stroke",textColor)
					//.style("stroke","white").style("stroke-width",0.4)
					.style("text-shadow","2px 0 0 #fff, -2px 0 0 #fff, 0 2px 0 #fff, 0 -2px 0 #fff, 1px 1px #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff")
 


			}else{



				let temptext = cactMainSvg.append("text")
					.attr("temptext",gene).text(gene)
					.attr("x",tempx+15).attr("y",tempy+3).style("font-size","14")
					//.style("font-weight","bold")
					.style("stroke",'black')
					//.style("stroke","white").style("stroke-width",0.4)
					.style("text-shadow","2px 0 0 #fff, -2px 0 0 #fff, 0 2px 0 #fff, 0 -2px 0 #fff, 1px 1px #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff")
 



			}

			

			


		}
}



function handleMouseOutNode(){




		if(controlModel === "TargetExplorer"){

			let tempr = Number(d3.select(this).attr("r"));
			let oldfill = d3.select(this).attr("oldfill");
			let oldopacity = d3.select(this).attr("oldopacity");

			$(this).removeAttr("oldfill");

			let gene = d3.select(this).attr("id").toString();
			//d3.select(this).attr("r",tempr-4).style("fill",defaultNodeColor).style("fill-opacity",0.5);
			d3.select(this).attr("r",tempr-1).style("fill",oldfill).style("fill-opacity",oldopacity);
			$("[temptext='"+gene+"']").remove();




			$(".node[oldfill]").each(function(){

				let oldfill = $(this).attr("oldfill");
				$(this).removeAttr("oldfill");
				$(this).css("fill",oldfill).css("fill-opacity",0.5);


			})


		}else if(controlModel === "PatientProfiler"){
			let gene = d3.select(this).attr("id");

			//let tempx = Number(d3.select(this).attr("cx"));
			//let tempy = Number(d3.select(this).attr("cy"));
			let tempr = Number(d3.select(this).attr("r"));
			
			d3.select(this).attr("r",tempr-2);

			$("#mainsvg").find(".genelabel[gene='"+gene+"']").show();

			$("#mainsvg").find("[temptext]").remove();


		}

}






