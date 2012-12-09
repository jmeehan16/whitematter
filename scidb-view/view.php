<?php
if (isset($_GET["mysql"])){
	$bodyclass="mysql";
	$titletext="MySQL";
}
else if(isset($_GET["csv"])){
	$bodyclass="csv";
	$titletext="CSV";
}
else {
	$bodyclass="scidb";
	$titletext="SciDB";
}
?>

<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<title><?php echo $titletext;?> Coordinated Viewer</title>

<style type="text/css">@import url(css/style.css);</style>
<link rel="stylesheet" href="http://code.jquery.com/ui/1.9.2/themes/base/jquery-ui.css" />
<script src="http://code.jquery.com/jquery-1.8.3.js"></script>
<script src="http://code.jquery.com/ui/1.9.2/jquery-ui.js"></script>
<script type="text/javascript" src="js/view.js"></script>
                
</head>
<body class="<?php echo $bodyclass;?>">
<h1><?php echo $titletext;?> Coordinated Viewer</h1>

<div id="choose">
	<form name="show">
		<select id="studies"></select>
		<select id="brains"></select>
		<select id="viewers"></select>
		<input type="button" name="submit" value="Show" class="submitbutton"></input>
	</form>
</div>

<div class="viewer-container">
    <div id="viewer" class="viewer" style="width: 100%; height: 100%;">
		<span class="viewer-number">0</span>
		<input type="button" class="prefetch" value="Prefetch!"/>
		<div class="view top">
			<div class="slice-container"></div>
		</div>
		<div class="view side">
			<div class="slice-container"></div>
		</div>
		<div class="view front">
			<div class="slice-container"></div>
		</div>
	</div>
</div>
<div class="viewer-container"> 
	<div id="viewer2" class="viewer" style="width: 100%; height: 100%;">
		<span class="viewer-number">1</span>
		<input type="button" class="prefetch" value="Prefetch!"/>
		<div class="view top">
			<div class="slice-container"></div>
		</div>
		<div class="view side">
			<div class="slice-container"></div>
		</div>
		<div class="view front">
			<div class="slice-container"></div>
		</div>
	</div>
</div>
<div class="viewer-container"> 
	<div id="viewer3" class="viewer" style="width: 100%; height: 100%;" >
		<span class="viewer-number">2</span>
		<input type="button" class="prefetch" value="Prefetch!"/>
		<div class="view top">
			<div class="slice-container"></div>
		</div>
		<div class="view side">
			<div class="slice-container"></div>
		</div>
		<div class="view front">
			<div class="slice-container"></div>
		</div>
	</div>
</div>
</body>
</html>