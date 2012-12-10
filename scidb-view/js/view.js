$(function() {
	console.log("started"); 
	var filler="";
	if ($("body").hasClass("mysql")){
		filler = "MySQL";
	}
	else if ($("body").hasClass("csv")){
		filler = "CSV"
	}
	//addAnotherViewer(0);
	//addAnotherViewer(1);
	//addAnotherViewer(2);
	//var dimensions = getJsonSync("/wm/wsgi/dimensions"+filler+".wsgi?name=image");
    var doneMovingTheSlider = 100;
	//var initialslicedepth = 120;
	var timer = new Array();
	
	var names = [];
    var xhr=null;
	function getJsonSync(url) {
	    //don't let multiple ajax calls accumulate
		//if(xhr || xhr!=null) { 
		//	xhr.abort(); 
		//} 
		//else {
		xhr = $.ajax({
			type: "GET",
			url: url,
			dataType: "json",
			success: function() {},
			data: {},
			async: false
		});
		return JSON.parse(xhr.responseText);
		//}
	};
	function setDimensions(arrayname,viewerid){
		dimensions = getJsonSync("/wm/wsgi/dimensions"+filler+".wsgi?name="+arrayname);
		var depth = dimensions["depth"];
		var width = dimensions["width"];
		var height = dimensions["height"];
		$("#"+viewerid).prepend('<span class="dimensions"><span class="width">'+width+'</span><span class="height">'+height+'</span><span class="depth">'+depth+'</span></span>');
		
	}
	
	function getVolumesNumber(arrayName){
		return getJsonSync("/wm/wsgi/numvol"+filler+".wsgi?name="+arrayName).numvolumes;
	}
	
	function getArrayName(studyid,patientid) {
		return arrayName = getJsonSync("/wm/wsgi/getTableName.wsgi?study_id="+studyid+"&pat_id="+patientid).table_name;
	}
	
	
	function initColorBars(viewerid){
		$("#"+viewerid+" .view.top .slice-container").prepend('<div class="horizontal sidebar colorbar"></div>');
		$("#"+viewerid+" .view.top .slice-container").prepend('<div class="vertical frontbar colorbar"></div>'); 
		$("#"+viewerid+" .view.side .slice-container").prepend('<div class="horizontal topbar colorbar"></div>'); 
		$("#"+viewerid+" .view.side .slice-container").prepend('<div class="vertical frontbar colorbar"></div>');
		$("#"+viewerid+" .view.front .slice-container").prepend('<div class="horizontal topbar colorbar"></div>'); 
		$("#"+viewerid+" .view.front .slice-container").prepend('<div class="vertical sidebar colorbar"></div>'); 
	}
	
	
	function otherCoordinatedSliders(sliderid){
		var slider = $("#"+sliderid);
		if(slider.hasClass("top")){
			return $(".slider.top").not("#"+slider.attr("id"));
		}
		else if(slider.hasClass("front")){
			return $(".slider.front").not("#"+slider.attr("id"));
		}
		else {
			return $(".slider.side").not("#"+slider.attr("id"));
		}
	}
	
	
	function initSliders(viewerid){
		var depth = $("#"+viewerid+" .dimensions .depth").text(); 
		var width = $("#"+viewerid+" .dimensions .width").text();
		var height = $("#"+viewerid+" .dimensions .height").text();
		//foreach viewer-container prepend a slider with max depth acquired
		//var viewers = $(".viewer-container")
		//viewers.each(function(i){ 
		var viewernumber= $("#"+viewerid).find(".viewer-number").text();
		$("#"+viewerid).find(".view.top").prepend('<input type="text" value="'+Math.floor((depth-1)/2)+'" id="slice-top-input-'+viewernumber+'" class="slice-text top" style="line-height:'+width+'px"/><div id="slider-top-vertical-'+viewernumber+'" class="slider top" style="float:left;height: '+(width)+'px;"></div>');
		$("#"+viewerid).find(".view.side").prepend('<input type="text" value="'+Math.floor((width-1)/2)+'" id="slice-side-input-'+viewernumber+'" class="slice-text side" style="line-height:'+width+'px"/><div id="slider-side-vertical-'+viewernumber+'" class="slider side" style="float:left;height: '+(width)+'px;"></div>');
		$("#"+viewerid).find(".view.front").prepend('<input type="text" value="'+Math.floor((height-1)/2)+'" id="slice-front-input-'+viewernumber+'" class="slice-text front" style="line-height:'+width+'px"/><div id="slider-front-vertical-'+viewernumber+'" class="slider front" style="float:left;height: '+(width)+'px;"></div>');
		//});
		
		
		$("#slider-top-vertical-"+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			change: function(event,ui){ 
				//if (!i || i>2){
				var i=$(this).parents(".viewer").find(".viewer-number").text();
				//}
				$( '#slice-top-input-'+i).val( ui.value );
				var vieweridchanged=$('#slice-top-input-'+i).parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-'+i);
				
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-'+i).val( valh );
				
				clearTimeout(timer[i]);
				timer[i] = setTimeout(function(){
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();	
					console.log("about to call update 2 from #"+vieweridchanged);
					update(study, brain,vieweridchanged,"top");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=otherCoordinatedSliders($(this).attr("id"));
					othersliders.slider("value",valh ).trigger("change");
					
				}
				else {
					console.log("remote");
					return false;
				}
				
				

			} ,
			slide: function(event,ui){
				$(".horizontal.topbar").stop().animate({top: ((depth-1-ui.value)/(depth-1))*100+"%"});
				
			},
			
		});	
		
		//SIDE SLIDERS
		
		$('#slider-side-vertical-'+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			change: function(event,ui){ 
				var i=$(this).parents(".viewer").find(".viewer-number").text();
				$( '#slice-side-input-'+i).val( ui.value );
				var vieweridchanged=$('#slice-side-input-'+i).parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-'+i);
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-'+i).val( valh );
				
				
				clearTimeout(timer[i]);
				timer[i] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain,vieweridchanged,"side");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=otherCoordinatedSliders($(this).attr("id"));
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				

			} ,
			slide: function(event,ui){
				$(".vertical.sidebar").stop().animate({left: ((width-1-ui.value)/(width-1))*100+"%"});
				$(".horizontal.sidebar").stop().animate({top: ((width-1-ui.value)/(width-1))*100+"%"});
				
			},
		
		});
		
		
		//FRONT SLIDERS
	
		$('#slider-front-vertical-'+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: Math.floor((height-1)/2),
			change: function(event,ui){ 
				i=$(this).parents(".viewer").find(".viewer-number").text();
				$( '#slice-front-input-'+i).val( ui.value );
				var vieweridchanged=$('#slice-front-input-'+i).parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-'+i);
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-'+i).val( valh );
				
				
				clearTimeout(timer[i]);
				timer[i] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					console.log("about to call update 2 from #"+vieweridchanged);
					update(study,brain,vieweridchanged,"front");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=otherCoordinatedSliders($(this).attr("id"));
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				

			} ,
			slide: function(event,ui){
				$(".vertical.frontbar").stop().animate({left: ((ui.value)/(height-1))*100+"%"});
				
			},
			
		});
			
		var color1 = "#ffaaaa";
		var color2 = "#aaffaa";
		var color3 = "#aaaaff";
			
		$("#slider-top-vertical-"+viewernumber+" .ui-slider-handle").css("background",color1);
		$("#slider-side-vertical-"+viewernumber+" .ui-slider-handle").css("background",color2);
		$("#slider-front-vertical-"+viewernumber+" .ui-slider-handle").css("background",color3);
		
		
	
	}
	
	function resetUI(){
		$(".slider").each(function(){ $(this).remove(); });
		$(".slice-text").each(function(){ $(this).remove(); });
		$(".colorbar").each(function(){ $(this).remove(); });
	
	}
    
	function wholebrain(arrayname,volume,viewerid){
		//var slicedepth = $("#"+viewerid).parent().find("input").val();
		var depth = $("#"+viewerid+" .dimensions .depth").text(); 
		var width = $("#"+viewerid+" .dimensions .width").text();
		var height = $("#"+viewerid+" .dimensions .height").text();
		$('#'+viewerid+" .prefetch").after('<span class="preloader"><img src="images/preloader.gif"/></span>');
		xhr = $.post("/wm/wsgi/multipleslices"+filler+".wsgi",
			{"study": arrayname,
			 "width": width,
			 "height": height,
			 "depth": depth,
			 //"slicedepth": slicedepth,
			 //"viewtype": viewtype,
			 "volume": volume,
			},
			function(data){ 
				//console.log(data);
				//console.log(data["top"][0]["c"])
				//var viewtype="top";
				$.each(data, function(viewtype, item) {
					$.each(data[viewtype], function(i, item) {
						var content = data[viewtype][i]["c"];
						var slicedepth = data[viewtype][i]["s"]
						if ($('#'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth).length==0){
							$('#'+viewerid+' div.'+viewtype+' .slice-container').append('<span class="slice" id="'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+content+'"/></span>'); 
							$('#'+viewerid+' div.'+viewtype+' .slice-container .slice').hide().removeClass("visible");
							$('#'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
						}
					});
				});
				$('#'+viewerid+' .preloader').remove();
			},
			"json"
		);
	}
	
	
	
	function update(arrayname,volume,viewerid,viewtype){ 
		//var brain = brainlist.val(); //selected brain
		//var viewerid = viewerslist.val(); //selected viewer
		var depth = $("#"+viewerid+" .dimensions .depth").text(); 
		var width = $("#"+viewerid+" .dimensions .width").text();
		var height = $("#"+viewerid+" .dimensions .height").text();
		var slicedepth = $("#"+viewerid).parent().find("."+viewtype).find("input").val();
		//check if this slice is there already 
		if ($('#'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth).length==0){
			//if(xhr || xhr!=null) { 
			//	xhr.abort(); 
			//}
			//else {
				xhr = $.post("/wm/wsgi/slice"+filler+".wsgi",
					{"study": arrayname,
					 "width": width,
					 "height": height,
					 "depth": depth,
					 "slicedepth": slicedepth,
					 "viewtype": viewtype,
					 "volume": volume
					},
					function(data){ 
						$('#'+viewerid+' div.'+viewtype+' .slice-container').append('<span class="slice" id="'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+data+'"/></span>'); 
						$('#'+viewerid+' div.'+viewtype+' .slice-container .slice').hide().removeClass("visible");
						$('#'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
					}
				);
			//}
		}
		else {
			$('#'+viewerid+' .'+viewtype+' .slice-container .slice').hide().removeClass("visible");
			$('#'+viewerid+'-'+arrayname+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
		}
	}	
	
	function addAnotherViewer(viewernumber){
		counter=counter+1;
		$("#outer-container").append(
		'<div class="viewer-container">'+
			'<div id="viewer'+viewernumber+'" class="viewer" style="width: 100%; height: 100%;">'+
				'<span class="viewer-number">'+viewernumber+'</span>'+
				'<input type="button" class="prefetch" value="Prefetch!"/>'+
				'<div class="view top">'+
					'<div class="slice-container"></div>'+
				'</div>'+
				'<div class="view side">'+
					'<div class="slice-container"></div>'+
				'</div>'+
				'<div class="view front">'+
					'<div class="slice-container"></div>'+
				'</div>'+
			'</div>'+
		'</div>');
		return "viewer"+viewernumber; 
		
	}
	function getListOfStudies(patientid){
		if (!patientid){
			var studieslist = getJsonSync("/wm/wsgi/getStudies.wsgi");
		}
		else {
			var studieslist = getJsonSync("/wm/wsgi/getStudies.wsgi?id="+patientid);
		}
		return studieslist["studies"];
	}
	
	function getListOfPatients(studyid){
		if (!studyid){
			var patientslist = getJsonSync("/wm/wsgi/getPatients.wsgi");
		}
		else {
			var patientslist = getJsonSync("/wm/wsgi/getPatients.wsgi?id="+studyid);
		}
		return patientslist["patients"];
	}
	
	
	function populateListofStudies(studieslist) {
		//studies = getJsonSync("/wm/wsgi/getStudies.wsgi");

		//var nameSelection = $(sel);
		//var nameOptions = nameSelection.prop("options");
		/*$("options", nameSelection).remove();
		names.forEach(function(name) {
			nameOptions[nameOptions.length] = new Option(name, name);
		});
		nameSelection.val(names[0]);*/
		$("#studies").empty();

		$.each(studieslist,function(i){
			var id = studieslist[i].id;
			var name = studieslist[i].name;
			$("#studies").append('<option value="'+id+'">'+name+'</option>');
		});
	}
	
	function populateListofPatients(patientslist) {
		$("#patients").empty();
		$.each(patientslist,function(i){
			var id = patientslist[i].id;
			var name = patientslist[i].name;
			$("#patients").append('<option value="'+id+'">'+name+'</option>');
		});
	}
	
	function populateListofBrainVolumes(numvol) {
		$("#brains").empty();
		for (var i=0;i<numvol;i++){ 
			$("#brains").append('<option value="'+i+'">Volume '+i+'</option>');
		}
	}
	
	/*function populateListOfViewers(){
		var viewers = $(".viewer");
		var ViewersSelection = $("#viewers");
		viewers.each(function() { 
						var id = $(this).attr("id");
						ViewersSelection.append('<option value="'+id+'">'+id+'</option>');
		            })
    }*/					

	//whenever studies drop down menu changes, brain volume drop down menu changes
	$("#studies,#patients").change(function() { console.log("menu changed");
		
		var studyid = $("#studies").val();
		var patientid = $("#patients").val();
		populateListofBrainVolumes(getVolumesNumber(getArrayName(studyid,patientid)));
		//updateVolumesNumber(studyname);
		//populateListofBrainVolumes(brainvolumesnumber);
		//resetUI();
		//updateDimensions(studyname);
		//initSliders();
		//initColorBars();
	});
	
	counter=0;
	
	$(document).ready(function() {
			console.log("jquery proper start");
			//names = getJsonSync("/wm/wsgi/list"+filler+".wsgi").names;
			//populateListOfViewers();
			populateListofStudies(getListOfStudies(null));
			populateListofPatients(getListOfPatients(null));
			$("#choose .submitbutton").click(function() {
					var viewerid = addAnotherViewer(counter);
					
					
					
					$("#"+viewerid+" .status").remove();
					$("#"+viewerid).prepend('<span class="status"><span class="brain">'+
										 $("#brains").val()+'</span><span class="study">'+
										 $("#studies").val()+'</span></span>');
					//var viewerselected = $("#viewers").val();		
					var study = $("#"+viewerid+" .status .study").text();
					var brain = $("#"+viewerid+" .status .brain").text();	
					var arrayname = getArrayName(study,brain);
					//remove any status data present
					$("#"+viewerid+" .status").prepend('<span class="arrayname">'+arrayname+'</span>');
					
										 
										
					
					//add status data in the viewer selected
					

					var dimensions=setDimensions(arrayname,viewerid);
					initSliders(viewerid);
                    initColorBars(viewerid);
					update( arrayname, brain, viewerid,"top");
					update( arrayname, brain, viewerid,"front");
					update( arrayname, brain, viewerid,"side");
					
					$(".horizontal.topbar").stop().animate({top: "50%"});
					$(".vertical.topbar").stop().animate({left: "50%"});
					$(".horizontal.sidebar").stop().animate({top: "50%"});
					$(".vertical.sidebar").stop().animate({left: "50%"});
					$(".horizontal.frontbar").stop().animate({top: "50%"});
					$(".vertical.frontbar").stop().animate({left: "50%"});
				}
			)
			$(".prefetch").click(function() {
				viewerid=$(this).parent().attr("id");
				var study = $(this).parent().find(".status .study").text();
				var brain = $(this).parent().find(".status .brain").text();
				var arrayname = $("#"+viewerid+" .status .arrayname").text();
				wholebrain(arrayname,brain,viewerid);
			});
			$("#studies").trigger("change");
			
			
			
	});

});
