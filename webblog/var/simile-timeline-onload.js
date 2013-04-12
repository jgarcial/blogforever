var tl;
function onLoad() {
    var Timeline = window.Timeline;
    var eventSource = new Timeline.DefaultEventSource(0);
    
    var zones = [];
    var theme = Timeline.ClassicTheme.create();
		Timeline.ThemeName = 'dark-theme'
		
    theme.event.bubble.width = 250;
    
    var $divTl = $('#tl');
    var date = $divTl.attr('data-initial-date')
    var bandInfos = [
	Timeline.createHotZoneBandInfo({
	    width:          "75%", 
	    intervalUnit:   Timeline.DateTime.WEEK, 
	    intervalPixels: 200,
	    zones:          zones,
	    eventSource:    eventSource,
	    date:           date,
	    timeZone:       0
	  //  theme:          theme
	}),
	Timeline.createHotZoneBandInfo({
	    width:          "15%", 
	    intervalUnit:   Timeline.DateTime.MONTH, 
	    intervalPixels: 200,
	    zones:          zones, 
	    eventSource:    eventSource,
	    date:           date, 
	    timeZone:       0,
	    overview:       true
	   // theme:          theme
	}),
	Timeline.createHotZoneBandInfo({
	    width:          "10%", 
	    intervalUnit:   Timeline.DateTime.YEAR, 
	    intervalPixels: 200,
	    zones:          zones, 
	    eventSource:    eventSource,
	    date:           date, 
	    timeZone:       0,
	    overview:       true
	   // theme:          theme
	})
    ];
    bandInfos[1].syncWith = 0;
    bandInfos[2].syncWith = 1;
    bandInfos[1].highlight = true;
    bandInfos[2].highlight = true;
    
    for (var i = 0; i < bandInfos.length; i++) {
	bandInfos[i].decorators = [
	];
    }
    
    tl = Timeline.create(document.getElementById('tl'), bandInfos, Timeline.HORIZONTAL);
    tl.loadXML($divTl.attr('data-source'), 
	       function(xml, url) { eventSource.loadXML(xml, url); });
}

var resizeTimerID = null;
function onResize() {
    if (resizeTimerID == null) {
	resizeTimerID = window.setTimeout(function() {
	    resizeTimerID = null;
	    tl.layout();
	}, 500);
    }
}
	function themeSwitch(){
		var timeline = document.getElementById('tl');           
		timeline.className = (timeline.className.indexOf('dark-theme') != -1) ? timeline.className.replace('dark-theme', '') : timeline.className += ' dark-theme';
		
	}

$(document).ready(function() {
	onLoad();
});

