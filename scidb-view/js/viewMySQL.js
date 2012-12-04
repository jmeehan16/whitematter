$(function() {
	console.log("started"); 
	var dimensions = getJsonSync("/wm/wsgi/dimensionsMySQL.wsgi?name=image");
    var doneMovingTheSlider = 100;
	var timer;
	initSliders();
	//PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
	var viewers = new Array();
	//var viewer2 = null;
	//var viewer3 = null;
	
	var names = [];
    var xhr=null;
	function getJsonSync(url) {
	    //don't let multiple ajax calls accumulate
		if(xhr || xhr!=null) { 
			xhr.abort(); 
		}
		else {
			xhr = $.ajax({
				type: "GET",
				url: url,
				dataType: "json",
				success: function() {},
				data: {},
				async: false
			});
			return JSON.parse(xhr.responseText);
		}
	};

	/*function zooms(name, names) {
		var zoomNames = [];
		for (i = 0; i < names.length; i++) {
			var zoomName = name + "_zoom_" + i; 
			if ($.inArray(zoomName, names) >= 0) {
				zoomNames[i] = zoomName;
			} else {
				break;
			}
		}

		if (zoomNames.length == 0)
			zoomNames[0] = name;


		return zoomNames;
	};*/
	
	function initSliders() {
	    /*var depth = dimensions["depth"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
						$(this).prepend('<input type="text" data-slider="true" id="slider'+i+'" data-slider-step="1" data-slider-theme="volume" data-slider-range="0,'+(depth-1)+'">');  
					});*/
		var depth = dimensions["depth"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
			$(this).prepend('<input type="text" id="slice-input-'+i+'"/><div id="slider-vertical-'+i+'" style="height: 200px;"></div>');
			$('#slider-vertical-'+i).slider({
				orientation: "vertical",
				range: "min",
				min: 0,
				max: depth-1,
				//value: 120,
				slide: function( event, ui ) {
					$( '#slice-input-'+i ).val( ui.value );
					var vieweridchanged=$('#slice-input-'+i).parent().find(".viewer").attr("id");
					$('#slice-input-'+i).val( $('#slider-vertical-'+i).slider( "value" ) );
					clearTimeout(timer);
					timer = setTimeout(function(){ 
						
						update($("#brains").val(),vieweridchanged,"top");
						update($("#brains").val(),vieweridchanged,"front");
						update($("#brains").val(),vieweridchanged,"side");
					},doneMovingTheSlider);
					
				}
				
			});
			
		});
    }
    
	function wholebrain(brain,viewerid,viewtype){
		var slicedepth = $("#"+viewerid).parent().find("input").val();
		var width = dimensions["width"];
		var height = dimensions["height"];
		xhr = $.post("/wm/wsgi/multipleslicesMySQL.wsgi",
					{"brain": brain,
					 "width": width,
					 "height": height,
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
		var slicedepth = $("#"+viewerid).parent().find("input").val();
		console.log(slicedepth);
		//brain = "image"; //TODO REMOVE
		if (slicedepth == null || !slicedepth)
		    slicedepth = 120;
		//check if this slice is there already 
		if ($('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).length==0){
			//if(xhr || xhr!=null) { 
			//	xhr.abort(); 
			//}
			//else {
				xhr = $.post("/wm/wsgi/sliceMySQL.wsgi",
					{"brain": brain,
					 "width": width,
					 "height": height,
					 "slicedepth": slicedepth,
					 "viewtype": viewtype
					},
					function(data){ 
						$('#'+viewerid+' .'+viewtype).append('<span class="slice" id="'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth+'"><img src="data:image/png;base64,'+data+'"/></span>'); 
						$('#'+viewerid+' .'+viewtype+' .slice').hide().removeClass("visible");
						$('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
					}
				);
			//}
		}
		else {
			$('#'+viewerid+' .'+viewtype+' .slice').hide().removeClass("visible");
			$('#'+viewerid+'-'+brain+'-'+viewtype+'-'+slicedepth).show().addClass("visible").show();
		}
	}	

	/*function show(brainlist,viewerslist) {
		var brain = brainlist.val(); //selected brain
		var viewerid = viewerslist.val(); //selected viewer
		console.log("detecting zooms"); 
		zoomNames = zooms(brain, names);
		zoomMax = zoomNames.length - 1;
		console.log("detected " + zoomNames.length + " zooms"); 

		console.log("detecting dimensions"); 
		var width = dimensions["width"];
		var height = dimensions["height"];
		
		var tileSize = 256;
		console.log("detected width = " + width); 
		console.log("detected height = " + height); 
		console.log("detected tileSize = " + tileSize); 

		console.log("started viewer");
		var provider = new PanoJS.TileUrlProvider('','','');
		provider.assembleUrl = function(x, y, zoom) {
			var zoomIdx = zoom > zoomMax ? zoomMax: zoom;
			url = "/wm/wsgi/slice.wsgi?name=" + zoomNames[zoomIdx];
			url += "&width=" + tileSize;
			url += "&height=" + tileSize;
			url += "&x=" + x;
			url += "&y=" + y;
			url += "&z=" + "120"
			return url;
		}
		if (viewers[viewerid])
			viewers[viewerid].clear();

		viewers[viewerid] = new PanoJS(viewerid, {
			tileUrlProvider : provider,
			tileSize        : tileSize,
			maxZoom         : zoomNames.length - 1,
			imageWidth      : width,
			imageHeight     : height,
			blankTile       : "images/blank.gif",
			loadingTile     : "images/progress.gif"
		});

		Ext.EventManager.addListener(window, "resize", callback(viewers[viewerid], viewers[viewerid].resize));
		xhr = "something"
		viewers[viewerid].init();
		xhr = null
		console.log("built viewer");
	};*/
	
	/*function update(viewerid) {
		var width = dimensions["width"];
		var height = dimensions["height"];
		
		var tileSize = 256;
		var provider = new PanoJS.TileUrlProvider('','','');
		var z = $("#"+viewerid).parent().find("input").val()
		provider.assembleUrl = function(x, y, zoom) {
			var zoomIdx = zoom > zoomMax ? zoomMax: zoom;
			url = "/wm/wsgi/slice.wsgi?name=image_50chunk";
			url += "&width=" + tileSize;
			url += "&height=" + tileSize;
			url += "&x=" + x;
			url += "&y=" + y;
			url += "&z=" + z;
			return url;
		}
                if (viewers[viewerid])
			viewers[viewerid].clear();
                 
		viewers[viewerid] = new PanoJS(viewerid, {
			tileUrlProvider : provider,
			tileSize        : tileSize,
			maxZoom         : zoomNames.length - 1,
			imageWidth      : width,
			imageHeight     : height,
			blankTile       : "images/blank.gif",
			loadingTile     : "images/progress.gif"
		});

		//Ext.EventManager.addListener(window, "resize", callback(viewers[viewerid], viewers[viewerid].resize));
		xhr = "something"
		viewers[viewerid].init();
		console.log("updated viewer");
		xhr = null
	
	}*/
	
	
	function populateListOfBrains(names, sel) {
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
	  
	/*Ext.onReady(function() {
		console.log("initializing"); 
		names = getJsonSync("/wm/wsgi/list.wsgi").names;
		console.log(names);
		populateListOfViewers();
		populateListOfBrains(names, "#brains");
		$("#choose .submitbutton").click(function() { show($(this).parent().find("#brains"),$(this).parent().find("#viewers"));})
		//document.show.submit.onclick = update;
		console.log("initialized"); 
	});*/
	
	
	
	$(document).ready(function() {
			console.log("jquery proper start");
			names = getJsonSync("/wm/wsgi/listMySQL.wsgi").names;
			console.log(names);
			populateListOfViewers();
			populateListOfBrains(names, "#brains");
			$("#choose .submitbutton").click(function() {
                    var viewerselected = $("#viewers").val();			
			        if (viewerselected != "viewer2"){
						update( $("#brains").val(), $("#viewers").val(),"top");
						update( $("#brains").val(), $("#viewers").val(),"front");
						update( $("#brains").val(), $("#viewers").val(),"side");
					}
					else {
						wholebrain($("#brains").val(), $("#viewers").val(),"top");
						//wholebrain($("#brains").val(), $("#viewers").val(),"front");
						//wholebrain($("#brains").val(), $("#viewers").val(),"side");
					}
				}
			)
			/*$("[data-slider]").each(function () {
									var input = $(this);
									$("<span>").addClass("output").insertAfter($(this));
								}).bind("slider:ready slider:changed", function (event, data) {
																			$(this).nextAll(".output:first").html(data.value);
																			var vieweridchanged=$(this).parent().find(".viewer").attr("id");
																			
																			//if(xhr || xhr!=null) { 
																			//	//xhr.abort(); 
																			//	xhr = null;
																			//}
																			//else {
																				update($("#brains").val(),vieweridchanged,"top");
																				update($("#brains").val(),vieweridchanged,"front");
																				update($("#brains").val(),vieweridchanged,"side");
																			//}
																	   });*/
	});

});