console.log("started"); 

PanoJS.CREATE_THUMBNAIL_CONTROLS = false;
var viewer = null;
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

function update() {
    var name = document.show.name.value;

    console.log("detecting zooms"); 
    var zoomNames = zooms(name, names);
    var zoomMax = zoomNames.length - 1;
    console.log("detected " + zoomNames.length + " zooms"); 

    console.log("detecting dimensions"); 
    var dimensions = getJsonSync("/wsgi/dimensions.wsgi?name=" + zoomNames[zoomMax]);
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
        url = "/wsgi/tile.wsgi?name=" + zoomNames[zoomIdx];
        url += "&width=" + tileSize;
        url += "&height=" + tileSize;
        url += "&x=" + x;
        url += "&y=" + y;
        return url;
    }
     
    if (viewer)
        viewer.clear();

    viewer = new PanoJS("viewer", {
        tileUrlProvider : provider,
        tileSize        : tileSize,
        maxZoom         : zoomNames.length - 1,
        imageWidth      : width,
        imageHeight     : height,
        blankTile       : "images/blank.gif",
        loadingTile     : "images/progress.gif"
    });

    Ext.EventManager.addListener(window, "resize", callback(viewer, viewer.resize));
    viewer.init();
    console.log("built viewer");
};

function buildOptions(names, sel) {
    var nameSelection = $(sel);
    var nameOptions = nameSelection.prop("options");
    $("options", nameSelection).remove();
    names.forEach(function(name) {
        nameOptions[nameOptions.length] = new Option(name, name);
    });
    nameSelection.val(names[0]);
}
 
Ext.onReady(function() {
    console.log("initializing"); 
    names = getJsonSync("wsgi/list.wsgi").names;
    console.log(names);
    buildOptions(names, "#name");
    document.show.submit.onclick = update;
    console.log("initialized"); 
});
