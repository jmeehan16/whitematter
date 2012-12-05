$(function() {
	console.log("started"); 
	var filler="";
	if ($("body").hasClass("mysql")){
		filler = "MySQL";
	}
	//var dimensions = getJsonSync("/wm/wsgi/dimensions"+filler+".wsgi?name=image");
    var doneMovingTheSlider = 100;
	var initialslicedepth = 120;
	var timer0;
	var timer1;
	var timer2;
	//initSliders();
	//initColorBars();
	
	
	//PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
	var viewers = new Array();
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
			$(this).find("div.top").prepend('<input type="text" value="'+initialslicedepth+'" id="slice-top-input-'+i+'" class="slice-text top" style="line-height:'+width+'px"/><div id="slider-top-vertical-'+i+'" class="slider" style="float:left;height: '+width+'px;"></div>');
			$(this).find("div.side").prepend('<input type="text" value="'+initialslicedepth+'" id="slice-side-input-'+i+'" class="slice-text side" style="line-height:'+width+'px"/><div id="slider-side-vertical-'+i+'" class="slider" style="float:left;height: '+width+'px;"></div>');
			$(this).find("div.front").prepend('<input type="text" value="'+initialslicedepth+'" id="slice-front-input-'+i+'" class="slice-text front" style="line-height:'+width+'px"/><div id="slider-front-vertical-'+i+'" class="slider" style="float:left;height: '+width+'px;"></div>');
		});
		
		//TOP SLIDERS
		
		$('#slider-top-vertical-0').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: depth-1,
			value: initialslicedepth,
			change: function(event,ui){ 

				$( '#slice-top-input-0').val( ui.value );
				var vieweridchanged=$('#slice-top-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-0').val( valh );
				
				
				clearTimeout(timer0);
				timer0 = setTimeout(function(){ 
					
					update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change : function( event, ui ) {
				$( '#slice-top-input-1').val( ui.value );
				var vieweridchanged=$('#slice-top-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-1').val( valh );
				
				
				clearTimeout(timer1);
				timer1 = setTimeout(function(){ 
					
					update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change: function( event, ui ) {
				$( '#slice-top-input-2').val( ui.value );
				var vieweridchanged=$('#slice-top-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-top-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-top-input-2').val( valh );
				
				clearTimeout(timer2);
				timer2 = setTimeout(function(){ 
					
					update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			
		});
		
		//FRONT SLIDERS
		
		$('#slider-front-vertical-0').slider({
			orientation: "vertical",
			range: "min",
			min: 0,
			max: height-1,
			value: initialslicedepth,
			change: function(event,ui){ 

				$( '#slice-front-input-0').val( ui.value );
				var vieweridchanged=$('#slice-front-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-0').val( valh );
				
				
				clearTimeout(timer0);
				timer0 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change : function( event, ui ) {
				$( '#slice-front-input-1').val( ui.value );
				var vieweridchanged=$('#slice-front-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-1').val( valh );
				
				
				clearTimeout(timer1);
				timer1 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change: function( event, ui ) {
				$( '#slice-front-input-2').val( ui.value );
				var vieweridchanged=$('#slice-front-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-front-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-front-input-2').val( valh );
				
				clearTimeout(timer2);
				timer2 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					update($("#brains").val(),vieweridchanged,"front");
					//update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change: function(event,ui){ 

				$( '#slice-side-input-0').val( ui.value );
				var vieweridchanged=$('#slice-side-input-0').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-0');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-0').val( valh );
				
				
				clearTimeout(timer0);
				timer0 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change : function( event, ui ) {
				$( '#slice-side-input-1').val( ui.value );
				var vieweridchanged=$('#slice-side-input-1').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-1');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-1').val( valh );
				
				
				clearTimeout(timer1);
				timer1 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					update($("#brains").val(),vieweridchanged,"side");
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
			value: initialslicedepth,
			change: function( event, ui ) {
				$( '#slice-side-input-2').val( ui.value );
				var vieweridchanged=$('#slice-side-input-2').parents(".viewer").attr("id");
				var sliderchanged=$('#slider-side-vertical-2');
				var valh = sliderchanged.slider( "value" );
				$('#slice-side-input-2').val( valh );
				
				clearTimeout(timer2);
				timer2 = setTimeout(function(){ 
					
					//update($("#brains").val(),vieweridchanged,"top");
					//update($("#brains").val(),vieweridchanged,"front");
					update($("#brains").val(),vieweridchanged,"side");
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
		$(".colorbar").each(function(){ $(this).remove(); });
	
	}
    
	function wholebrain(brain,viewerid,viewtype){
		var slicedepth = $("#"+viewerid).parent().find("input").val();
		var width = dimensions["width"];
		var height = dimensions["height"];
		var depth = dimensions["depth"];
		xhr = $.post("/wm/wsgi/multipleslices"+filler+".wsgi",
					{"brain": brain,
					 "width": width,
					 "height": height,
					 "depth": depth,
					 "slicedepth": slicedepth,
					 "viewtype": viewtype
					},
						function(data){ 
						    console.log(data);
							//do something with all the slices
							//$(data).find("something").each(function() {)
							//$('#'+viewerid+' .'+viewtype).append('<span class="slice" id="'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+data+'"/></span>'); 
							//$('#'+viewerid+' .'+viewtype+' .slice').hide().removeClass("visible");
							//$('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
						}
		);
	}
	
	
	
	function update(brain,viewerid,viewtype){ 
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
		if ($('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).length==0){
			//if(xhr || xhr!=null) { 
			//	xhr.abort(); 
			//}
			//else {
				xhr = $.post("/wm/wsgi/slice"+filler+".wsgi",
					{"brain": brain,
					 "width": width,
					 "height": height,
					 "depth": depth,
					 "slicedepth": slicedepth,
					 "viewtype": viewtype,
					 "volume": "1"
					},
					function(data){ 
						$('#'+viewerid+' div.'+viewtype+' .slice-container').append('<span class="slice" id="'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+data+'"/></span>'); 
						$('#'+viewerid+' div.'+viewtype+' .slice-container .slice').hide().removeClass("visible");
						$('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
					}
				);
			//}
		}
		else {
			$('#'+viewerid+' .'+viewtype+' .slice-container .slice').hide().removeClass("visible");
			$('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
		}
	}	
	
	
	function populateListOfStudies(names, sel) {
		var nameSelection = $(sel);
		var nameOptions = nameSelection.prop("options");
		$("options", nameSelection).remove();
		names.forEach(function(name) {
			nameOptions[nameOptions.length] = new Option(name, name);
		});
		nameSelection.val(names[0]);
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
		var brainvolumes = getJsonSync("/wm/wsgi/numvol"+filler+".wsgi?name="+studyname);
		console.log(brainvolumes);	
		resetUI();
		updateDimensions(studyname);
		initSliders();
		initColorBars();
	});
	
	
	$(document).ready(function() {
			console.log("jquery proper start");
			names = getJsonSync("/wm/wsgi/list"+filler+".wsgi").names;
			//console.log(names);
			populateListOfViewers();
			populateListOfStudies(names, "#studies");
			//TODO REMOVE 
			populateListOfStudies(names, "#brains");
			$("#choose .submitbutton").click(function() {
                    var viewerselected = $("#viewers").val();			
			        // if (viewerselected != "viewer2"){
						update( $("#brains").val(), $("#viewers").val(),"top");
						update( $("#brains").val(), $("#viewers").val(),"front");
						update( $("#brains").val(), $("#viewers").val(),"side");
					//}
					//else {
						//wholebrain($("#brains").val(), $("#viewers").val(),"top");
						//wholebrain($("#brains").val(), $("#viewers").val(),"front");
						//wholebrain($("#brains").val(), $("#viewers").val(),"side");
					//}
				}
			)
	});

});
