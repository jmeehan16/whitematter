$(function() {
	console.log("started"); 
	var filler="";
	if ($("body").hasClass("mysql")){
		filler = "MySQL";
	}
	else if ($("body").hasClass("csv")){
		filler = "CSV"
	}
	//var dimensions = getJsonSync("/wm/wsgi/dimensions"+filler+".wsgi?name=image");
    var doneMovingTheSlider = 300;
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
	
	function setZoom(viewerid){
		var depth = $("#"+viewerid+" .dimensions .depth").text(); 
		var width = $("#"+viewerid+" .dimensions .width").text();
		var height = $("#"+viewerid+" .dimensions .height").text();
		if (width<256) {
			$("#"+viewerid+" .slice-container").css("zoom",((256/width)*100)+"%");
			$("#"+viewerid+" .slider").each(function() {$(this).css("height",((256/width)*$(this).css("height"))+"px");});
		}
		else if(height<256){
			$("#"+viewerid+" .slice-container").css("zoom",((256/height)*100)+"%");
			$("#"+viewerid+" .slider").each(function() {$(this).css("height",((256/height)*$(this).css("height"))+"px");});
		}
		
		
	}
	
	function getVolumesNumber(arrayName){
		return getJsonSync("/wm/wsgi/numvol"+filler+".wsgi?name="+arrayName).numvolumes;
	}
	
	function getArrayName(studyid,patientid) {
		return arrayName = getJsonSync("/wm/wsgi/getTableName.wsgi?study_id="+studyid+"&pat_id="+patientid).table_name[0];
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
		$("#"+viewerid).find(".view.side").prepend('<input type="text" value="'+Math.floor((width-1)/2)+'" id="slice-side-input-'+viewernumber+'" class="slice-text side" style="line-height:'+depth+'px"/><div id="slider-side-vertical-'+viewernumber+'" class="slider side" style="float:left;height: '+(depth)+'px;"></div>');
		$("#"+viewerid).find(".view.front").prepend('<input type="text" value="'+Math.floor((height-1)/2)+'" id="slice-front-input-'+viewernumber+'" class="slice-text front" style="line-height:'+depth+'px"/><div id="slider-front-vertical-'+viewernumber+'" class="slider front" style="float:left;height: '+(depth)+'px;"></div>');
		//});
		
		var topfunc = function(event,ui,sliderobjcall){ 
			//if (!i || i>2){
			$(".horizontal.topbar").stop().animate({top: ((depth-1-ui.value)/(depth-1))*100+"%"});
			var i=sliderobjcall.parents(".viewer").find(".viewer-number").text();
			//}
			$( '#slice-top-input-'+i).val( ui.value );
			var vieweridchanged=$('#slice-top-input-'+i).parents(".viewer").attr("id");
			var sliderchanged=$('#slider-top-vertical-'+i);
			
			var valh = sliderchanged.slider( "value" );
			$('#slice-top-input-'+i).val( valh );
			
			
			
			var updfunc = function(){
				var brain = $("#"+vieweridchanged+" .status .volume").text();
				var arrayname = $("#"+vieweridchanged+" .status .arrayname").text();
				update(arrayname, brain,vieweridchanged,"top");
			}
			
			if (!$("#"+vieweridchanged).hasClass("prefetched")){
				clearTimeout(timer[i]);
				timer[i] = setTimeout(updfunc,doneMovingTheSlider);
			}
			else {
				updfunc();
			}
			
			if (event.bubbles==true){ //local
				othersliders=otherCoordinatedSliders(sliderobjcall.attr("id"));
				othersliders.slider("value",valh ).trigger("change");
				
			}
			else { //remote
				return false;
			}
			
			

		}
		
		var sidefunc = function(event,ui,sliderobjcall) {			
			
			$(".vertical.sidebar").stop().animate({left: ((width-1-ui.value)/(width-1))*100+"%"});
			$(".horizontal.sidebar").stop().animate({top: ((width-1-ui.value)/(width-1))*100+"%"});
			var i=sliderobjcall.parents(".viewer").find(".viewer-number").text();
			$( '#slice-side-input-'+i).val( ui.value );
			var vieweridchanged=$('#slice-side-input-'+i).parents(".viewer").attr("id");
			var sliderchanged=$('#slider-side-vertical-'+i);
			var valh = sliderchanged.slider( "value" );
			$('#slice-side-input-'+i).val( valh );
			
			var updfunc = function() {
				//var study = $("#"+vieweridchanged+" .status .study").text();
				var brain = $("#"+vieweridchanged+" .status .volume").text();
				var arrayname = $("#"+vieweridchanged+" .status .arrayname").text();
				update(arrayname,brain,vieweridchanged,"side");
			
			}
			
			
			if (!$("#"+vieweridchanged).hasClass("prefetched")){
				clearTimeout(timer[i]);
				timer[i] = setTimeout(updfunc,doneMovingTheSlider);
			}
			else {
				updfunc();
			}
		
			if (event.bubbles==true){ //local
				othersliders=otherCoordinatedSliders(sliderobjcall.attr("id"));
				setTimeout(function() {othersliders.slider("value",valh ).trigger("change");},10);
			}
			else { //remote
				return false;
			}

			

		} 
		
		var frontfunc = function(event,ui,sliderobjectcall){ 
			$(".vertical.frontbar").stop().animate({left: ((ui.value)/(height-1))*100+"%"});
			i=sliderobjectcall.parents(".viewer").find(".viewer-number").text();
			$( '#slice-front-input-'+i).val( ui.value );
			var vieweridchanged=$('#slice-front-input-'+i).parents(".viewer").attr("id");
			var sliderchanged=$('#slider-front-vertical-'+i);
			var valh = sliderchanged.slider( "value" );
			$('#slice-front-input-'+i).val( valh );
			
			
			var updfunc = function() {
				var brain = $("#"+vieweridchanged+" .status .volume").text();
				var arrayname = $("#"+vieweridchanged+" .status .arrayname").text();
				update(arrayname,brain,vieweridchanged,"front");
			}
			
			if (!$("#"+vieweridchanged).hasClass("prefetched")){
				clearTimeout(timer[i]);
				timer[i] = setTimeout(updfunc,doneMovingTheSlider);
			}
			else {
				updfunc();
			}
			
			
			if (event.bubbles==true){ // local
				othersliders=otherCoordinatedSliders(sliderobjectcall.attr("id"));
				othersliders.slider("value",valh ).trigger("change");
			}
			else { //remote
				return false;
			}
			

		}
		
		$("#slider-top-vertical-"+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			slide:  function(event,ui) {topfunc(event,ui,$(this))},
			change: function(event,ui) {topfunc(event,ui,$(this))}
		});	
		
		//SIDE SLIDERS
		
		$('#slider-side-vertical-'+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			slide: function(event,ui){ sidefunc(event,ui,$(this))},
			change: function(event,ui){ sidefunc(event,ui,$(this))}
		
		});
		
		
		//FRONT SLIDERS
	
		$('#slider-front-vertical-'+viewernumber).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: Math.floor((height-1)/2),
			slide: function(event,ui) {frontfunc(event,ui,$(this))},
			change: function(event,ui) {frontfunc(event,ui,$(this))}
			
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
			{"arrayname": arrayname,
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
				$('#'+viewerid).addClass("prefetched");
				
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
					{"arrayname": arrayname,
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
				'<span class="delete">X</span> <input type="button" class="prefetch" value="Prefetch!"/>'+
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
		$("#volumes").empty();
		for (var i=0;i<numvol;i++){ 
			$("#volumes").append('<option value="'+i+'">Volume '+i+'</option>');
		}
	}
				

	//whenever studies drop down menu changes, brain volume drop down menu changes
	$("#studies,#patients").change(function() { console.log("menu changed");
		
		var studyid = $("#studies").val();
		var patientid = $("#patients").val();
		populateListofBrainVolumes(getVolumesNumber(getArrayName(studyid,patientid)));
	});
	
	counter=0;
	
	$(document).ready(function() {
			console.log("jquery proper start");
			populateListofStudies(getListOfStudies(null));
			populateListofPatients(getListOfPatients(null));
			$("#choose .submitbutton").click(function() {
					var viewerid = addAnotherViewer(counter);
					
					
					
					$("#"+viewerid+" .status").remove();
					//add status data in the viewer selected
					$("#"+viewerid).prepend('<span class="status"><span class="patient">'+
										 $("#patients").val()+'</span><span class="study">'+
										 $("#studies").val()+'</span><span class="volume">'+$("#volumes").val()+'</span>');
					//var viewerselected = $("#viewers").val();		
					var study = $("#"+viewerid+" .status .study").text();
					var brain = $("#"+viewerid+" .status .volume").text();
					var patient = $("#"+viewerid+" .status .patient").text(); 
					var arrayname = getArrayName(study,patient);
					//remove any status data present
					$("#"+viewerid+" .status").prepend('<span class="arrayname">'+arrayname+'</span>');
					
					
					var dimensions=setDimensions(arrayname,viewerid);
					setZoom(viewerid);
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
			$(".prefetch").live("click",function() {
				viewerid=$(this).parent().attr("id");
				var study = $(this).parent().find(".status .study").text();
				var brain = $(this).parent().find(".status .volume").text();
				var arrayname = $("#"+viewerid+" .status .arrayname").text();
				wholebrain(arrayname,brain,viewerid);
				$(this).attr("disabled","true");
			});
			//$("#studies").trigger("change");
			
			
			$(".delete").live("click",function() { $(this).parents(".viewer-container").remove() });
			
	});

});
