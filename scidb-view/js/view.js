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
    var doneMovingTheSlider = 100;
	var initialslicedepth = 120;
	//var timer0;
	//var timer1;
	//var timer2;
	var timer = new Array();
	//initSliders();
	//initColorBars();
	
	
	//PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
	//var viewers = new Array();
	//var viewer2 = null;
	//var viewer3 = null;
	
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
		$("div.top .slice-container").each(function(){ $(this).prepend('<div class="horizontal sidebar colorbar"></div>'); });
		$("div.top .slice-container").each(function(){ $(this).prepend('<div class="vertical frontbar colorbar"></div>'); });
		$("div.side .slice-container").each(function(){ $(this).prepend('<div class="horizontal topbar colorbar"></div>'); });
		$("div.side .slice-container").each(function(){ $(this).prepend('<div class="vertical frontbar colorbar"></div>'); });
		$("div.front .slice-container").each(function(){ $(this).prepend('<div class="horizontal topbar colorbar"></div>'); });
		$("div.front .slice-container").each(function() { $(this).prepend('<div class="vertical sidebar colorbar"></div>'); });
	}
	
	
	
	
	function initSliders() {
	    /*var depth = dimensions["depth"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
						$(this).prepend('<input type="text" data-slider="true" id="slider'+i+'" data-slider-step="1" data-slider-theme="volume" data-slider-range="0,'+(depth-1)+'">');  
					});*/
		var depth = dimensions["depth"];
		var width = dimensions["width"];
		var height = dimensions["height"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
			$(this).find("div.top").prepend('<input type="text" value="'+Math.floor((depth-1)/2)+'" id="slice-top-input-'+i+'" class="slice-text top" style="line-height:'+width+'px"/><div id="slider-top-vertical-'+i+'" class="slider" style="float:left;height: '+(width)+'px;"></div>');
			$(this).find("div.side").prepend('<input type="text" value="'+Math.floor((width-1)/2)+'" id="slice-side-input-'+i+'" class="slice-text side" style="line-height:'+width+'px"/><div id="slider-side-vertical-'+i+'" class="slider" style="float:left;height: '+(width)+'px;"></div>');
			$(this).find("div.front").prepend('<input type="text" value="'+Math.floor((height-1)/2)+'" id="slice-front-input-'+i+'" class="slice-text front" style="line-height:'+width+'px"/><div id="slider-front-vertical-'+i+'" class="slider" style="float:left;height: '+(width)+'px;"></div>');
		});
		
		//TOP SLIDERS
		for (i=0; i<=2; i++){
			$("#slider-top-vertical-"+i).slider({
				orientation: "vertical",
				range: "min",
				min: 0,
				max: depth-1,
				value: Math.floor((depth-1)/2),
				change: function(event,ui){ 
					if (!i){
						i=$(this).parents(".viewer").find(".viewer-number").text();
					}
					$( '#slice-top-input-'+i).val( ui.value );
					var vieweridchanged=$('#slice-top-input-'+i).parents(".viewer").attr("id");
					var sliderchanged=$('#slider-top-vertical-'+i);
					if (jQuery.isFunction(sliderchanged.slider)){
						var valh = sliderchanged.slider( "value" );
						$('#slice-top-input-'+i).val( valh );
					}
					
					clearTimeout(timer[i]);
					timer[i] = setTimeout(function(){
						var study = $("#"+vieweridchanged+" .status .study").text();
						var brain = $("#"+vieweridchanged+" .status .brain").text();	
						update(study, brain,vieweridchanged,"top");
					},doneMovingTheSlider);
					
					if (event.bubbles==true){
						console.log("local");
						var sliderid=$(this).attr("id");
						if (sliderid=="slider-top-vertical-0"){
						   othersliders=$("#slider-top-vertical-2,#slider-top-vertical-1");
						}
						else if(sliderid=="slider-top-vertical-1"){
							othersliders=$("#slider-top-vertical-0,#slider-top-vertical-2");
						}
						else if(sliderid=="slider-top-vertical-2"){
							othersliders=$("#slider-top-vertical-0,#slider-top-vertical-1");
						}
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
		
		}
		
		
		
		/*$('#slider-top-vertical-0').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			change: function(event,ui){ 

				$( '#slice-top-input-0').val( ui.value );
				var vieweridchanged=$('#slice-top-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-0').val( valh );
				
				
				clearTimeout(timer0);
				timer0 = setTimeout(function(){
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();	
					update(study, brain,vieweridchanged,"top");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-top-vertical-2,#slider-top-vertical-1")
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
	
		$('#slider-top-vertical-1').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			change : function( event, ui ) {
				$( '#slice-top-input-1').val( ui.value );
				var vieweridchanged=$('#slice-top-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-1').val( valh );
				
				
				clearTimeout(timer1);
				timer1 = setTimeout(function(){ 		
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study, brain,vieweridchanged,"top");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-top-vertical-0,#slider-top-vertical-2")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".horizontal.topbar").stop().animate({top: ((depth-1-ui.value)/(depth-1))*100+"%"});
				
			},
			
		});		
	
	
		$('#slider-top-vertical-2').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: Math.floor((depth-1)/2),
			change: function( event, ui ) {
				$( '#slice-top-input-2').val( ui.value );
				var vieweridchanged=$('#slice-top-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-2').val( valh );
				
				clearTimeout(timer2);
				timer2 = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain,vieweridchanged,"top");
				},doneMovingTheSlider);
				
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-top-vertical-0,#slider-top-vertical-1")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".horizontal.topbar").stop().animate({top: ((depth-1-ui.value)/(depth-1))*100+"%"});
				
			},
			
		});*/
		
		//FRONT SLIDERS
		
		$('#slider-front-vertical-0').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: Math.floor((height-1)/2),
			change: function(event,ui){ 

				$( '#slice-front-input-0').val( ui.value );
				var vieweridchanged=$('#slice-front-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-0').val( valh );
				
				
				clearTimeout(timer[0]);
				timer[0] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain,vieweridchanged,"front");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-front-vertical-2,#slider-front-vertical-1")
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
	
		$('#slider-front-vertical-1').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: Math.floor((height-1)/2),
			change : function( event, ui ) {
				$( '#slice-front-input-1').val( ui.value );
				var vieweridchanged=$('#slice-front-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-1').val( valh );
				
				
				clearTimeout(timer[1]);
				timer[1] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study, brain,vieweridchanged,"front");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-front-vertical-0,#slider-front-vertical-2")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".vertical.frontbar").stop().animate({left: ((ui.value)/(height-1))*100+"%"});
				
			},
			
		});		
	
	
		$('#slider-front-vertical-2').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: Math.floor((height-1)/2),
			change: function( event, ui ) {
				$( '#slice-front-input-2').val( ui.value );
				var vieweridchanged=$('#slice-front-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-2').val( valh );
				
				clearTimeout(timer[2]);
				timer[2] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain, vieweridchanged,"front");
				},doneMovingTheSlider);
				
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-front-vertical-0,#slider-front-vertical-1")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".vertical.frontbar").stop().animate({left: ((ui.value)/(height-1))*100+"%"});
				
			},
			
		});
		
		
		
		
		
		
		
		
		
		
		
		
		//SIDE SLIDERS
		
		$('#slider-side-vertical-0').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			change: function(event,ui){ 

				$( '#slice-side-input-0').val( ui.value );
				var vieweridchanged=$('#slice-side-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-0').val( valh );
				
				
				clearTimeout(timer[0]);
				timer[0] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain,vieweridchanged,"side");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-side-vertical-2,#slider-side-vertical-1")
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
	
		$('#slider-side-vertical-1').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			change : function( event, ui ) {
				$( '#slice-side-input-1').val( ui.value );
				var vieweridchanged=$('#slice-side-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-1').val( valh );
				
				
				clearTimeout(timer[1]);
				timer[1] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study,brain,vieweridchanged,"side");
				},doneMovingTheSlider);
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-side-vertical-0,#slider-side-vertical-2")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".vertical.sidebar").stop().animate({left: ((width-1-ui.value)/(width-1))*100+"%"});
				$(".horizontal.sidebar").stop().animate({top: ((width-1-ui.value)/(width-1))*100+"%"});
				
			},
			
		});		
	
	
		$('#slider-side-vertical-2').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: width-1,
			value: Math.floor((width-1)/2),
			change: function( event, ui ) {
				$( '#slice-side-input-2').val( ui.value );
				var vieweridchanged=$('#slice-side-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-2').val( valh );
				
				clearTimeout(timer[2]);
				timer[2] = setTimeout(function(){ 
					var study = $("#"+vieweridchanged+" .status .study").text();
					var brain = $("#"+vieweridchanged+" .status .brain").text();
					update(study, brain,vieweridchanged,"side");
				},doneMovingTheSlider);
				
				
				if (event.bubbles==true){
					console.log("local");
					othersliders=$("#slider-side-vertical-0,#slider-side-vertical-1")
					othersliders.slider("value",valh ).trigger("change");
				}
				else {
					console.log("remote");
					return false;
				}
				
				
				
			},
			slide: function(event,ui){
				$(".vertical.sidebar").stop().animate({left: ((width-1-ui.value)/(width-1))*100+"%"});
				$(".horizontal.sidebar").stop().animate({top: ((width-1-ui.value)/(width-1))*100+"%"});
				
			},
			
		});
		
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
		
		
		
			
    }
	
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
		
		//console.log(slicedepth);
		//console.log(slicedepth);
		//brain = "image"; //TODO REMOVE
		if (slicedepth == null || !slicedepth){
		    slicedepth = initialslicedepth;
		}
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
		initSliders();
		initColorBars();
	});
	
	
	$(document).ready(function() {
			console.log("jquery proper start");
			names = getJsonSync("/wm/wsgi/list"+filler+".wsgi").names;
			populateListOfViewers();
			populateListofStudies();
			$("#choose .submitbutton").click(function() {
                    var viewerselected = $("#viewers").val();			
			        // if (viewerselected != "viewer2"){
					
					//remove any status data present
					$("#"+viewerselected+" .status").remove();
					
					//add status data in the viewer selected
					$("#"+viewerselected).prepend('<span class="status"><span class="brain">'+
										 $("#brains").val()+'</span><span class="study">'+
										 $("#studies").val()+'</span></span>');
					var study = $("#"+viewerselected+" .status .study").text();
					var brain = $("#"+viewerselected+" .status .brain").text();	
					update( study, brain, viewerselected,"top");
					update( study, brain, viewerselected,"front");
					update( study, brain, viewerselected,"side");
					$(".horizontal.topbar").stop().animate({top: "50%"});
					$(".vertical.topbar").stop().animate({left: "50%"});
					$(".horizontal.sidebar").stop().animate({top: "50%"});
					$(".vertical.sidebar").stop().animate({left: "50%"});
					$(".horizontal.frontbar").stop().animate({top: "50%"});
					$(".vertical.frontbar").stop().animate({left: "50%"});
					//}
					//else {
						//wholebrain($("#brains").val(), $("#viewers").val(),"top");
						//wholebrain($("#brains").val(), $("#viewers").val(),"front");
						//wholebrain($("#brains").val(), $("#viewers").val(),"side");
					//}
				}
			)
			$(".prefetch").click(function() {
				viewerid=$(this).parent().attr("id");
				wholebrain("image","0",viewerid);
			});
			$("#studies").trigger("change");
			
			
			
	});

});
