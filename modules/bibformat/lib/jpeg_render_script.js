var page = require('webpage').create(),
	/* Command-line args in order. */
    width, height, address, output

page.onLoadStarted = function () {
    console.log('Start loading...');
};
page.onLoadFinished = function (status) {	
	if(status == "success") {		
		console.log('Loading finished.');
		page.evaluate(function(){
			if (window.jQuery && $('script[type^="text/x-mathjax-config"]')[0] && window.MathJax) {
				MathJax.Hub.Register.StartupHook("End",function () {
					alert("<invenio_export_as_jpeg_msg>MathJax Completed");
				});
			} else {
				alert("<invenio_export_as_jpeg_msg>MathJax is not installed")
			}
		});
	}
};

page.onAlert = function(msg){
	if(msg == "<invenio_export_as_jpeg_msg>MathJax Completed" ||
		msg == "<invenio_export_as_jpeg_msg>MathJax is not installed") {
		page.render(output);
		phantom.exit();
	}
};

if (phantom.args.length < 4 || phantom.args.length > 5) {
    console.log('Usage: rasterize.js width height URL filename');
    phantom.exit();
} else {
	width = phantom.args[0];
	height = phantom.args[1];
    address = phantom.args[2];
    output = phantom.args[3];
    page.viewportSize = { width: width, height: height };
    page.open(address)
}
