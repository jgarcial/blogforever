# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


"""
BibFormat Element - displays a timeline with the blog events
"""

from invenio.config import CFG_SITE_URL
from invenio.webblog_utils import get_parent_blog, get_parent_post
from invenio.search_engine import get_creation_date
from invenio.bibformat_engine import BibFormatObject

def format_element(bfo):
    """
    """
    
    recid = bfo.control_field('001')
    out = """
    <script>
       Timeline_ajax_url="/js/simile-timeline_2.3.0/src/ajax/api/simile-ajax-api.js";
       Timeline_urlPrefix='/js/simile-timeline_2.3.0/src/webapp/api/';       
       Timeline_parameters='bundle=true';
    </script>

    <script src="/js/simile-timeline_2.3.0/src/webapp/api/timeline-api.js" type="text/javascript"></script>
    <script>
        var tl;
        function onLoad() {
	    var Timeline = window.Timeline;
            var eventSource = new Timeline.DefaultEventSource(0);
            
            var zones = [];
            var theme = Timeline.ClassicTheme.create();
			Timeline.ThemeName = 'dark-theme'
			
            theme.event.bubble.width = 250;
            
            var date = "Fri Nov 22 2013 13:00:00 GMT-0600"
            var bandInfos = [
                Timeline.createHotZoneBandInfo({
                    width:          "75%%", 
                    intervalUnit:   Timeline.DateTime.WEEK, 
                    intervalPixels: 200,
                    zones:          zones,
                    eventSource:    eventSource,
                    date:           date,
                    timeZone:       0
                  //  theme:          theme
                }),
                Timeline.createHotZoneBandInfo({
                    width:          "15%%", 
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
                    width:          "10%%", 
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
            
            tl = Timeline.create(document.getElementById("tl"), bandInfos, Timeline.HORIZONTAL);
            tl.loadXML("https://pcuds36.cern.ch/record/%s/export/xtl", function(xml, url) { eventSource.loadXML(xml, url); });
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
    </script>
	<style type="text/css">
		
		#switch_theme{margin-left:2em; cursor:pointer; background:#eee; padding:4px 6px; width:120px; text-align:center; font-weight:bold; border:1px solid #999;}
		
		.t-highlight1{background-color:#ccf;}
		.p-highlight1{background-color:#fcc;}
		
		.timeline-highlight-label-start .label_t-highlight1{color:#f00;}
		.timeline-highlight-label-end .label_t-highlight1{color:#aaf;}
		
		.timeline-band-events .important{color:#f00;}		
		.timeline-band-events .small-important{background:#c00;}
		
		
		/*---------------------------------*/
		
		.dark-theme {color:#eee;}
		.dark-theme .timeline-band-0 .timeline-ether-bg{background-color:#333}
		.dark-theme .timeline-band-1 .timeline-ether-bg{background-color:#111}
		.dark-theme .timeline-band-2 .timeline-ether-bg{background-color:#222}
		.dark-theme .timeline-band-3 .timeline-ether-bg{background-color:#444}
		
		
		.dark-theme .t-highlight1{background-color:#003;}
		.dark-theme .p-highlight1{background-color:#300;}
		
		.dark-theme .timeline-highlight-label-start .label_t-highlight1{color:#f00;}
		.dark-theme .timeline-highlight-label-end .label_t-highlight1{color:#115;}
		
		.dark-theme .timeline-band-events .important{color:#c00;}		
		.dark-theme .timeline-band-events .small-important{background:#c00;}
		
		.dark-theme .timeline-date-label-em{color:#fff;}
		.dark-theme .timeline-ether-lines{border-color:#555; border-style:solid;}
		.dark-theme .timeline-ether-highlight{background:#555;}
		
		.dark-theme .timeline-event-tape,
		.dark-theme .timeline-small-event-tape{background:#f60;}
		.dark-theme .timeline-ether-weekends{background:#111;}
	</style>    
      """ % (recid,)

#    out += """<button type="button" style="z-index:9999; position: relative;" class="close" onClick="onLoad();">Timeline</button>"""
    out += """<div id="tl" class="timeline-default dark-theme" style="height: 350px; margin: 2em;"></div>"""
    out += """<button type="button" class="close" onClick="onLoad();">Timeline</button>"""
   # out += """<script>
   #             $(document).ready(function() {
   #               onLoad();
   #             });
   #           </script>"""
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if
    output of this element should be escaped.
    """

    return 0
