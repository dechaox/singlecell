
	var geneXYexpr;




	function InitScatterPlot(meta){

		
		var $selectGeneX = $('#geneX').selectize({
			valueField: 'gene',
			labelField: 'gene',
			searchField: 'gene',
			create: false,
			persist: true,
			load: function(query, callback) {
				if (!query.length) return callback();

				query = query.toUpperCase();
				if(query in corrData){
					callback([{"gene":query}])
				}else{
					callback()
				}
			}

		});

		var controlGeneX = $selectGeneX[0].selectize;

		

		
		
		var $selectGeneY =$('#geneY').selectize({
			create: false,
			persist: false,
			load: function(query, callback) {
				if (!query.length) return callback();

				query = query.toUpperCase();
				if(query in corrData){
					callback([{"value":query,"text":query}])
				}else{
					callback()
				}
			}
		});
		var controlGeneY = $selectGeneY[0].selectize;
		//controlGeneY.clearOptions();

		$("#geneX").change(function(){
			let selectGene = $(this).val();
			if(selectGene.length>0){

				let corrGenes = corrData[selectGene];
				controlGeneY.clearOptions();
				let defaultval=false;
				for(let i in corrGenes){
					if(defaultval === false){
						defaultval = i;
					}
					controlGeneY.addOption({
						value: i,
						text: (i+"  ["+corrGenes[i]+"]")

					})
				}

				let negCorrGene = negativeCorrData[selectGene];
				for(let i in negCorrGene){
					
					controlGeneY.addOption({
						value: i,
						text: (i+"  ["+negCorrGene[i]+"]")

					})
				}


				controlGeneY.setValue(defaultval,false)

			}
			


		})




		var metaorder={"TUMOR OR NORMAL":null,"DISEASECATEGORY":null};

		for(var i in meta){
			if(meta[i] in metaorder){

				$("#contrastColumn").append("<option value='"+meta[i]+"'>"+meta[i]+"</option>");
			}


		} 
		for(var i in meta){
			if(meta[i] in metaorder){


			}else{
				$("#contrastColumn").append("<option value='"+meta[i]+"'>"+meta[i]+"</option>");

			}

			

		}

		$("#contrastColumn").selectize({
			create:false,
			persist:false

		});



		$("#contrastColumn").change(function(){



			let genex = $("#geneX").val();
			let geney =	$("#geneY").val();

			let contrast = $("#contrastColumn").val();

			if(genex && genex.length>0 && geney && geney.length>0 && contrast && contrast.length>0){
				renderScatterPlot(genex,geney,contrast,"#scatterplotSVG",1);

			}

		});

		$("#geneY").change(function(){
			let genex = $("#geneX").val();
			let geney =	$("#geneY").val();

			let contrast = $("#contrastColumn").val();


			if(genex && genex.length>0 && geney && geney.length>0 && contrast && contrast.length>0){
				renderScatterPlot(genex,geney,contrast,"#scatterplotSVG",1);

			}


		})


		$("[name='spSwapGenes']").click(function(){

			
		})






	}






	function renderScatterPlot(genex,geney,category,div_id,method){

		if(method ===1 ){

			$.ajax({

				url:"/dataManager/getExpressionByStudyAndGenes",
				data:{"geneX":genex,"geneY":geney,"study":study,"category":category},
				method:"post",
				success:function(result){
					//geneXYexpr = result;
					drawScatterPlot(genex,geney,category,div_id,result);

				},
				error:function(){

					//alert("error in server");
				}



			})




			//update geneX and Y expression
		}else if(method ===2){
			
			drawScatterPlot(genex,geney,category,div_id,geneXYexpr);

		}




	}


	function drawScatterPlot(genex,geney,category,div_id,data){
		//alert($("#cccc").width())//768

		//alert($("#xxxxx").width())//546
		//alert($("#yy").width())//162
		var groups = data.groups;
		var expression = data.data;
		var spSVG = d3.select(div_id);
		spSVG.selectAll("*").remove()
		var topMargin = 5;
		var leftMargin = 49;
		var rightMargin = 180;
		var bottomMargin = 60;

		//width =758
		var totalw = $(div_id).width();
		var totalh = $(div_id).height();

		var width = totalw - leftMargin - rightMargin;
		var height = totalh - topMargin - bottomMargin;
		
		var xScale = d3.scaleLinear().range([0, width])
		var yScale = d3.scaleLinear().range([0, height])

		xScale.domain([data["geneXmin"], data["geneXmax"]]);
		yScale.domain([data["geneYmax"], data["geneYmin"]]);


		// x axis and label
		spSVG.append("g").attr("transform", "translate(" + leftMargin + "," + (height+topMargin) + ")").call(d3.axisBottom(xScale));
		spSVG.append("text").attr("transform", "translate(" + (leftMargin + width / 2) + " ," + (height + topMargin + 35) + ")")
		.style("text-anchor", "middle").text(genex);

		if("isRNAseq"==""){

			spSVG.append("text")
			.attr("transform", "translate(" + (50 + width / 2) + " ," + (height + topMargin + 40) + ")")
			.style("text-anchor", "middle")
			.text("log2(FPKM+0.5)")
		}

		//y
		spSVG.append("g").attr("transform", "translate(" + leftMargin + ","+topMargin+")").call(d3.axisLeft(yScale));
		spSVG.append("text").attr("transform", "rotate(-90)").attr("y", 0)
		.attr("x", 0 - (height / 2)).attr("dy", "1em")
		.style("text-anchor", "middle").text(geney);	 	


		var scatterSVG = spSVG.append("g").attr("id",'scatter').attr("transform","translate(" + leftMargin + ","+topMargin+")");


		//render groups;
		var colorlist=["#FF7E00","#551B8C","#008000","#FF033E",'#391802','#007FFF',"#FFBF00","#F364A2",
		"#21ABCD","#7DC242","#A1CAF1","#7C0A02","#9966CC","#FF6600","#92A1CF","#D0FF14","#000000",'#A40000',"#B9F2FF","#3B3B6D","#CFCFCF"]
		var spLegendg = spSVG.append("g").attr("transform", "translate(" + (leftMargin+width) + ",0)");
		
		
		//db.GTEx_from_Omicsoft.insert
		//alert(JSON.stringify(expression))
		var colorGroups={};
		for(let i=0;i<groups.length;i++){
			spLegendg.append("rect").attr("group",groups[i]).attr("width",16).attr("height",16).attr("x",10).attr("y",22*i+10).style("fill",colorlist[i]);
			spLegendg.append("text").text(groups[i]).attr("group",groups[i]).attr("x",32).attr("y",22*i+22).style("font-size","11px");
			
			colorGroups[groups[i]]=colorlist[i];
		}




		for (var s in expression) {
			scatterSVG.append("circle").attr("class","scatternode").attr("cx",xScale(expression[s]["x"])).attr("cy",yScale(expression[s]["y"]))
			.attr("sample",s)
			.style("fill", colorGroups[ expression[s]["group"] ] ).attr("r",4).attr("gexpx",expression[s]["x"]).attr("gexpy",expression[s]["y"])
			.style("stroke","grey").style("stroke-width",0.5);
			//scatterSVG.append("circle").attr("cx", expression[s]["xx"] ).attr("cy",expression[s]["yy"]).style("fill",expression[s]["color"]).attr("r",3)

		}


		d3.selectAll(".scatternode").on("mouseover", function() {		
	    
		    let gexpx = d3.select(this).attr("gexpx");
		    let gexpy = d3.select(this).attr("gexpy");
		    let tempthiscoord = d3.mouse(this);


			tempthiscoord[0] = tempthiscoord[0]-gtranslate[0];
			tempthiscoord[1] = tempthiscoord[1]-gtranslate[1];
		    let d3pagex = (tempthiscoord[0]+50)+"px";
		    let d3pagey = (tempthiscoord[1]+50)+"px";
			$(".scattertooltip")
	            .css("left", d3pagex)		
	            .css("top",d3pagey )
	            .html("<h7>"+d3.select(this).attr("sample")+"</h7><br><h7>"+genex+": "+gexpx+"</h7><br><h7>"+geney+": "+gexpy+"</h7>")
	            .show();

		}).on("mouseout", function(d) {		
			$(".scattertooltip").html("").hide();	
		});
   


		//var scattertooltip = d3.select("#scatterplotdiv").append("div").attr("class","scattertooltip");
		//$(".scattertooltip").html("teset123123")


		var gtranslate = getTransform("#scatter","translate");

		var dot = scatterSVG.selectAll(".scatternode");
		var selectedSamples=[];
		var coords=[];
		var selectedline = d3.line();
		var dragStart = function() {
        
	        dot.classed("selected", false);

			coords = [];
			 
			d3.selectAll(".scatter_draw_path").remove();
			d3.selectAll(".scatter_done_path").remove();
			
			dot.style("stroke","grey").style("stroke-width",0.5);
			
			$("[name='saveSelectedSample']").html("");
		}







		var drawPath = function(isdone) {
			if(coords.length>1){

				scatterSVG.append("path").attr("class",'scatter_draw_path').attr( "d",selectedline([coords[coords.length-2],   coords[coords.length-1] ]));

				if (isdone) {

					scatterSVG.append("path").attr("class","scatter_done_path").attr("d", selectedline( coords.concat([coords[0]]) ) );

					scatterSVG.selectAll(".scatter_draw_path").remove();


					dot.each(function(d, i) {
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


			let templen =$(".scatternode.selected").length;

			if(templen>0){

				selectedSamples = [];
				$(".scatternode.selected").each(function(){
					selectedSamples.push($(this).attr("sample"));
				
					$(this).css("stroke","red").css("stroke-width",1);;
				})


				$("[name='saveSelectedSample']").html("<span style='color:steelblue;display:inline-block;'>"+selectedSamples.length+"</span> samples selected &nbsp;&nbsp; <input name='savedSelectSampleinput' class='form-control input-sm' placeholder='Enter Samples Name' style='width:200px;display:inline-block;'>  &nbsp;&nbsp;<a class='btn btn-sm btn-primary' name='selectedsamplesave' style='display:inline-block;'> save </a>");
				
				$("[name='saveSelectedSample']").find("[name='selectedsamplesave']").click(function(){

					var samplesetname= $("[name='savedSelectSampleinput']").val();
					var samplelength = selectedSamples.length;

					if(samplelength>0 && samplesetname.length>0){
						
						$.ajax({
							url:"/dataManager/saveSampleSetByStudyAndName",
							method:"post",
							data:{"study":study,"name":samplesetname,"samples":selectedSamples.join(",")},
							success:function(res){
								if(res.status===1){

									$("[name='saveSelectedSample']").html("<span style='color:green;font-size:16px;'>success</span>");

								}else{
									$("[name='saveSelectedSample']").html("<span style='color:red;font-size:16px;'>save error</span>");
								}

							},error(e){

							}


						})

						

					}

				})


			}else{
				$(".scatternode").css("stroke","grey").css("stroke-width",0.5);
				//$("[name='cellselectinfo']").html("");
				dragStart();

			}
		}

		var dragMove = function() {
			dot.classed("selected", false);
			let tempcoord = d3.mouse(this);


			tempcoord[0] = tempcoord[0]-gtranslate[0];
			tempcoord[1] = tempcoord[1]-gtranslate[1];
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


		spSVG.call(d3.drag()
                .on("start", dragStart)
                .on("drag", dragMove)
                .on("end", dragEnd));










	}