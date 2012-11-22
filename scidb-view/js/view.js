$(function() {
	console.log("started"); 
    initSliders();
	PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
	var viewers = new Array();
	//var viewer2 = null;
	//var viewer3 = null;
	
	var names = [];

	function getJsonSync(url) {
		return JSON.parse($.ajax({
			type: "GET",
			url: url,
			dataType: "json",
			success: function() {},
			data: {},
			async: false
		}).responseText);
	};

	function zooms(name, names) {
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
	};
	
	function initSliders() {
	    var dimensions = getJsonSync("/wm/wsgi/dimensions.wsgi?name=image");
	    var depth = dimensions["depth"];
		//foreach viewer-container prepend a slider with max depth acquired
		var viewers = $(".viewer-container")
		viewers.each(function(i){ 
						$(this).prepend('<input type="text" data-slider="true" id="slider'+i+'" data-slider-step="1" data-slider-theme="volume" data-slider-range="0,'+depth+'">');  
					});
		
    }

	

	function show(brainlist,viewerslist) {
		var brain = brainlist.val(); //selected brain
		var viewerid = viewerslist.val(); //selected viewer
		console.log("detecting zooms"); 
		var zoomNames = zooms(brain, names);
		var zoomMax = zoomNames.length - 1;
		console.log("detected " + zoomNames.length + " zooms"); 

		console.log("detecting dimensions"); 
		var dimensions = getJsonSync("/wm/wsgi/dimensions.wsgi?name=" + zoomNames[zoomMax]);
		var width = dimensions["width"];
		var height = dimensions["height"];
		
		var tileSize = 128;
		console.log("detected width = " + width); 
		console.log("detected height = " + height); 
		console.log("detected tileSize = " + tileSize); 

		console.log("building viewer");
		var provider = new PanoJS.TileUrlProvider('','','');
		provider.assembleUrl = function(x, y, zoom) {
			var zoomIdx = zoom > zoomMax ? zoomMax: zoom;
			url = "/wm/wsgi/tile.wsgi?name=" + zoomNames[zoomIdx];
			url += "&width=" + tileSize;
			url += "&height=" + tileSize;
			url += "&x=" + x;
			url += "&y=" + y;
			url += "&z=" + "120"
			return url;
		}
		//var viewer = viewers[viewerid];
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
		viewers[viewerid].init();
		console.log("built viewer");
	};
	
	
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
	  
	Ext.onReady(function() {
		console.log("initializing"); 
		names = getJsonSync("/wm/wsgi/list.wsgi").names;
		console.log(names);
		populateListOfViewers();
		populateListOfBrains(names, "#brains");
		$("#choose .submitbutton").click(function() { show($(this).parent().find("#brains"),$(this).parent().find("#viewers"));})
		//document.show.submit.onclick = update;
		console.log("initialized"); 
	});
	
	
	
	$(document).ready(function() {
			console.log("jquery proper start");
			$("[data-slider]").each(function () {
									var input = $(this);
									$("<span>").addClass("output").insertAfter($(this));
								}).bind("slider:ready slider:changed", function (event, data) {
													$(this).nextAll(".output:first").html(data.value.toFixed(3));
			//document.execCommand("enableObjectResizing", false, false);
			});
	});

});