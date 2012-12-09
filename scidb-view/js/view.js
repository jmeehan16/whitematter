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
	function updateDimensions(studyname){
		dimensions = getJsonSync("/wm/wsgi/dimensions"+filler+".wsgi?name="+studyname);
	}
	
	function updateVolumesNumber(studyname){
		brainvolumesnumber = getJsonSync("/wm/wsgi/numvol"+filler+".wsgi?name="+studyname).numvolumes;
	}
	
	
	function initColorBars(){
		$(".view.top .slice-container").each(function(){ $(this).prepend('<div class="horizontal sidebar colorbar"></div>'); });
		$(".view.top .slice-container").each(function(){ $(this).prepend('<div class="vertical frontbar colorbar"></div>'); });
		$(".view.side .slice-container").each(function(){ $(this).prepend('<div class="horizontal topbar colorbar"></div>'); });
		$(".view.side .slice-container").each(function(){ $(this).prepend('<div class="vertical frontbar colorbar"></div>'); });
		$(".view.front .slice-container").each(function(){ $(this).prepend('<div class="horizontal topbar colorbar"></div>'); });
		$(".view.front .slice-container").each(function() { $(this).prepend('<div class="vertical sidebar colorbar"></div>'); });
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
		var depth = dimensions["depth"];
		var width = dimensions["width"];
		var height = dimensions["height"];
		//foreach viewer-container prepend a slider with max depth acquired
		//var viewers = $(".viewer-container")
		//viewers.each(function(i){ 
		$("#"+viewerid).find(".view.top").prepend('<input type="text" value="'+Math.floor((depth-1)/2)+'" id="slice-top-input-'+i+'" class="slice-text top" style="line-height:'+width+'px"/><div id="slider-top-vertical-'+i+'" class="slider top" style="float:left;height: '+(width)+'px;"></div>');
		$("#"+viewerid).find(".view.side").prepend('<input type="text" value="'+Math.floor((width-1)/2)+'" id="slice-side-input-'+i+'" class="slice-text side" style="line-height:'+width+'px"/><div id="slider-side-vertical-'+i+'" class="slider side" style="float:left;height: '+(width)+'px;"></div>');
		$("#"+viewerid).find(".view.front").prepend('<input type="text" value="'+Math.floor((height-1)/2)+'" id="slice-front-input-'+i+'" class="slice-text front" style="line-height:'+width+'px"/><div id="slider-front-vertical-'+i+'" class="slider front" style="float:left;height: '+(width)+'px;"></div>');
		//});
		
		k = $("#"+viewerid).find(".viewer-number").text();
		$("#slider-top-vertical-"+i).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			change: function(event,ui){ 
				//if (!i || i>2){
				i=$(this).parents(".viewer").find(".viewer-number").text();
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
		
		$('#slider-side-vertical-'+i).slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			change: function(event,ui){ 
				i=$(this).parents(".viewer").find(".viewer-number").text();
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
	
		$('#slider-front-vertical-'+i).slider({
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
			
		$("#slider-top-vertical-"+i+" .ui-slider-handle").css("background",color1);
		$("#slider-side-vertical-"+i+" .ui-slider-handle").css("background",color2);
		$("#slider-front-vertical-"+i+" .ui-slider-handle").css("background",color3);
		
		
	
	}
	
	
	
	/*function initSliders() {
	    //var depth = dimensions["depth"];
		//foreach viewer-container prepend a slider with max depth acquired
		//var viewers = $(".viewer-container")
		//viewers.each(function(i){ 
		//				$(this).prepend('<input type="text" data-slider="true" id="slider'+i+'" data-slider-step="1" data-slider-theme="volume" data-slider-range="0,'+(depth-1)+'">');  
		//			});
		var depth = dimensions["depth"];
		var width = dimensions["width"];
		var height = dimensions["height"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
			$(this).find(".view.top").prepend('<input type="text" value="'+Math.floor((depth-1)/2)+'" id="slice-top-input-'+i+'" class="slice-text top" style="line-height:'+width+'px"/><div id="slider-top-vertical-'+i+'" class="slider top" style="float:left;height: '+(width)+'px;"></div>');
			$(this).find(".view.side").prepend('<input type="text" value="'+Math.floor((width-1)/2)+'" id="slice-side-input-'+i+'" class="slice-text side" style="line-height:'+width+'px"/><div id="slider-side-vertical-'+i+'" class="slider side" style="float:left;height: '+(width)+'px;"></div>');
			$(this).find(".view.front").prepend('<input type="text" value="'+Math.floor((height-1)/2)+'" id="slice-front-input-'+i+'" class="slice-text front" style="line-height:'+width+'px"/><div id="slider-front-vertical-'+i+'" class="slider front" style="float:left;height: '+(width)+'px;"></div>');
		});
		
		
		for (var k=0; k<=2; k++){
			//TOP SLIDERS
			$("#slider-top-vertical-"+k).slider({
				orientation: "vertical",
				range: "min",
				min: 0,
				max: depth-1,
				value: Math.floor((depth-1)/2),
				change: function(event,ui){ 
					//if (!i || i>2){
					i=$(this).parents(".viewer").find(".viewer-number").text();
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
			
			$('#slider-side-vertical-'+k).slider({
				orientation: "vertical",
				range: "min",
				min: 0,
				max: width-1,
				value: Math.floor((width-1)/2),
				change: function(event,ui){ 
					i=$(this).parents(".viewer").find(".viewer-number").text();
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
		
			$('#slider-front-vertical-'+k).slider({
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
		}
		
		//coloring the sliders
		
		var color1 = "#ffaaaa";
		var color2 = "#aaffaa";
		var color3 = "#aaaaff";
		
		$("#slider-top-vertical-0 .ui-slider-handle").css("background",color1);
		$("#slider-top-vertical-1 .ui-slider-handle").css("background",color1);
		$("#slider-top-vertical-2 .ui-slider-handle").css("background",color1);
		$("#slider-side-vertical-0 .ui-slider-handle").css("background",color2);
		$("#slider-side-vertical-1 .ui-slider-handle").css("background",color2);
		$("#slider-side-vertical-2 .ui-slider-handle").css("background",color2);
		$("#slider-front-vertical-0 .ui-slider-handle").css("background",color3);
		$("#slider-front-vertical-1 .ui-slider-handle").css("background",color3);
		$("#slider-front-vertical-2 .ui-slider-handle").css("background",color3);
		
		
		
			
    }*/
	
	function resetUI(){
		$(".slider").each(function(){ $(this).remove(); });
		$(".slice-text").each(function(){ $(this).remove(); });
		$(".colorbar").each(function(){ $(this).remove(); });
	
	}
    
	function wholebrain(study,volume,viewerid){
		//var slicedepth = $("#"+viewerid).parent().find("input").val();
		var width = dimensions["width"];
		var height = dimensions["height"];
		var depth = dimensions["depth"];
		$('#'+viewerid+" .prefetch").after('<span class="preloader"><img src="images/preloader.gif"/></span>');
		xhr = $.post("/wm/wsgi/multipleslices"+filler+".wsgi",
			{"study": study,
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
						if ($('#'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth).length==0){
							$('#'+viewerid+' div.'+viewtype+' .slice-container').append('<span class="slice" id="'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+content+'"/></span>'); 
							$('#'+viewerid+' div.'+viewtype+' .slice-container .slice').hide().removeClass("visible");
							$('#'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
						}
					});
				});
				$('#'+viewerid+' .preloader').remove();
			},
			"json"
		);
	}
	
	
	
	function update(study,volume,viewerid,viewtype){ 
		//var brain = brainlist.val(); //selected brain
		//var viewerid = viewerslist.val(); //selected viewer
		var width = dimensions["width"];
		var height = dimensions["height"];
		var depth = dimensions["depth"];
		var slicedepth = $("#"+viewerid).parent().find("."+viewtype).find("input").val();
		//check if this slice is there already 
		if ($('#'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth).length==0){
			//if(xhr || xhr!=null) { 
			//	xhr.abort(); 
			//}
			//else {
				xhr = $.post("/wm/wsgi/slice"+filler+".wsgi",
					{"study": study,
					 "width": width,
					 "height": height,
					 "depth": depth,
					 "slicedepth": slicedepth,
					 "viewtype": viewtype,
					 "volume": volume
					},
					function(data){ 
						$('#'+viewerid+' div.'+viewtype+' .slice-container').append('<span class="slice" id="'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+data+'"/></span>'); 
						$('#'+viewerid+' div.'+viewtype+' .slice-container .slice').hide().removeClass("visible");
						$('#'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
					}
				);
			//}
		}
		else {
			$('#'+viewerid+' .'+viewtype+' .slice-container .slice').hide().removeClass("visible");
			$('#'+viewerid+'-'+study+'-'+volume+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
		}
	}	
	
	function addAnotherViewer(viewernumber){
		counter=counter+1;
		return $("#outer-container").append(
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
		'</div>').find(".viewer").attr("id");
		
	}
	
	
	function populateListofStudies() {
		names = getJsonSync("/wm/wsgi/list"+filler+".wsgi").names;
		sel = $("#studies");
		var nameSelection = $(sel);
		var nameOptions = nameSelection.prop("options");
		$("options", nameSelection).remove();
		names.forEach(function(name) {
			nameOptions[nameOptions.length] = new Option(name, name);
		});
		nameSelection.val(names[0]);
	}
	
	function populateListofBrainVolumes(numvol) {
		$("#brains").empty();
		for (var i=0;i<numvol;i++){ 
			$("#brains").append('<option value="'+i+'">Volume '+i+'</option>');
		}
	}
	
	function populateListOfViewers(){
		var viewers = $(".viewer");
		var ViewersSelection = $("#viewers");
		viewers.each(function() { 
						var id = $(this).attr("id");
						ViewersSelection.append('<option value="'+id+'">'+id+'</option>');
		            })
    }					

	//whenever studies drop down menu changes, brain volume drop down menu changes
	$("#studies").change(function() { console.log("studies menu changed");
		var studyname = $(this).val();
		updateVolumesNumber(studyname);
		populateListofBrainVolumes(brainvolumesnumber);
		resetUI();
		updateDimensions(studyname);
		//initSliders();
		initColorBars();
	});
	
	counter=0;
	
	$(document).ready(function() {
			console.log("jquery proper start");
			names = getJsonSync("/wm/wsgi/list"+filler+".wsgi").names;
			populateListOfViewers();
			populateListofStudies();
			$("#choose .submitbutton").click(function() {
					var viewerid = addAnotherViewer(counter);
					initSliders(viewerid);
                    //var viewerselected = $("#viewers").val();		
					
					//remove any status data present
					$("#"+viewerid+" .status").remove();
					
					//add status data in the viewer selected
					$("#"+viewerid).prepend('<span class="status"><span class="brain">'+
										 $("#brains").val()+'</span><span class="study">'+
										 $("#studies").val()+'</span></span>');
					var study = $("#"+viewerid+" .status .study").text();
					var brain = $("#"+viewerid+" .status .brain").text();	
					update( study, brain, viewerid,"top");
					update( study, brain, viewerid,"front");
					update( study, brain, viewerid,"side");
					
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
				wholebrain(study,brain,viewerid);
			});
			$("#studies").trigger("change");
			
			
			
	});

});
