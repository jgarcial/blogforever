$(document).ready(function() {
	$("#language-combo-box").change(function() {
		var val = $("#language-combo-box")
				.val();
		$(".goog-te-sectional-gadget-link")
				.remove();
		if (val != "") {
			$(".dummy-translate-link").hide();
			var script = document
					.createElement('script');
			script.type = 'text/javascript';
			script.src = "//translate.google.com/translate_a/element.js?cb=googleSectionalElementInit&ug=section&hl="
					+ val
			$("#translate-script").append(
					script);
		} else {
			$(".dummy-translate-link").show();
						}
	});
});
