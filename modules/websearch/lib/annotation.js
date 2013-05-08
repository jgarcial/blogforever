annotationTooltipOptions = {
		'tooltipList' : {},

		'addNewTooltip' : function(id, text) {
			this.tooltipList[id] = text;
		},
		'getTooltipWithId' : function(id) {
			return this.tooltipList[id];
		},
		'deleteTooltipWithId' : function(id) {
			delete this.tooltipList[id];
		},
		'deleteWholeList' : function() {
			this.tooltipList = {};
		},
		'getWholeList' : function() {
			return this.tooltipList;
		}
};

$(document).ready(function() {
    currentAnnotationId = null;
    objectMouseOn = null;

    rangeX = 50;
    rangeY = 50;

    tooltipTopPos = 0;
    tooltipLeftPos = 0;

    colorContent = $('#color_palette_edit').html();
    langEditAnnotation = $("#langEditAnnotation").html();
    langAddAnnotation = $("#langAddAnnotation").html();
    langAddNewNote = $("#langAddNewNote").html();
    langDelete = $("#langDelete").html();
    langAnnotationInfoText = $("#langAnnotationInfoText").html();

    /*
     * Arrange positions, porperties of the highlight and annotation elements.
     * */

    // Makes annotation box resizable and draggable
    $('#annotation_panel').resizable({
        maxHeight: 300,
        maxWidth: 400,
        minHeight: 195,
        minWidth: 250,
        alsoResize: '#text_area'
    });

    $('#annotation_panel').draggable({
        handle: ".highlight-modal-header"
    });
    $('#annotation_panel').hide();

    $('#annotation_close_but').click(function() {
        closeAnnotationBox();
    });

    $('#annotation_save_but').click(function() {
        var annotationText = $('textarea#text_area').val();
        var form = {
            'path': location.pathname,
            'annotation': annotationText,
            'id': currentAnnotationId
        };

        var selector = "highlight[high_anno_id=" + currentAnnotationId + "]"
        $(selector).tooltip('destroy');
        addAnnotationTooltip($(selector), currentAnnotationId, annotationText);

        annotationTooltipOptions.addNewTooltip(currentAnnotationId, annotationText);
        $.ajax({
            type: 'POST',
            url: '/youraccount/saveannotation',
            data: form,
            dataType: 'json',
            success: function(data) {
            	$("div.tooltip").remove();

                var currentHtmlCode = $('div.highlightable').html();
                $('highlight[high_anno_id=' +currentAnnotationId + ']').addClass('has_annotation');

                // Undo operation.
                if ($('#date_info > i.icon-pencil').size()) {
                    undoStack.addOperationRecord('InsertedNote');
                    undoStack.recordInsertNote(currentAnnotationId);
                } else {
                    undoStack.addOperationRecord('EditedNote');
                    undoStack.recordEditedNote(currentAnnotationId, data.annotation, data.last_updated);
                }
                toggleAnnotationFromHighlight(currentAnnotationId, 1);
                closeAnnotationBox();
            }
        });
    });

    $('#annotation_remove_but').click(function() {
    	var selector = $("highlight[high_anno_id=" + currentAnnotationId + "]");
        selector.tooltip('destroy');
    	addHighlightTooltip(selector[0], 'hover', 'mouse');
        undoStack.addOperationRecord('DeletedNote');
        undoStack.recordDeletedNote(currentAnnotationId, $('#text_area').val(), $('#date_info').attr("title"));
        removeAnnotation(currentAnnotationId);
        toggleAnnotationFromHighlight(currentAnnotationId, 0);
        closeAnnotationBox();
    });
});

function optionMenuTextContainerClick(elem, mouse) {
	$("highlight").tooltip("hide");
	currentAnnotationId = $(elem).attr('high_anno_id');
	highlightElem = $('highlight[high_anno_id=' + currentAnnotationId + ']');

    if ($(elem).attr('id') == 'edit_menu_link_1') {
        if (($(highlightElem).hasClass('has_annotation'))) {
        	getAndShowAnnotation(mouse);
        } else {
            openAddAnnotation(mouse);
        }
    } else {
        undoStack.addOperationRecord('DeletedHighlight');
        deleteHighlight(highlightElem);
        constructJsonObject();
        closeAnnotationBox();
    }
}

function colorEditClick(elem) {
	$("div.tooltip").remove();
    undoStack.addOperationRecord('Highlight');
    undoStack.recordHighlight( $('div.highlightable').html());
    var color = $(elem).css('background-color');

    currentAnnotationId =  $(elem).parent().attr("high_anno_id");
    highlightElem = $("highlight[high_anno_id=" + currentAnnotationId + "]")[0];

    if (!($([highlightElem]).hasClass('has_annotation'))) {
        var nextS = highlightElem.nextSibling;
        if (nextS && nextS.nodeType == 1 && nextS.tagName.toLowerCase() == 'highlight' && $(nextS).attr('high_anno_id')
            && color == nextS.style.backgroundColor) {
            $(highlightElem).attr('high_anno_id', $(nextS).attr('high_anno_id'));
        }
        highlightElem.style.backgroundColor = color;
    } else {
        $('highlight[high_anno_id=' +currentAnnotationId + ']').each(function(){
            $(this).css('background-color', color);
        })
    }

    cleanDuplicates(highlightElem.parentNode);
    constructJsonObject();
    $('div.option_menu').hide('fast');
}

function closeAnnotationBox() {
    /**
     * Hides annotation box and clears their contents.
     * */

    $('#annotation_panel_title').html('');
    $('#date_info').html('');
    $('#text_area').val('');
    $('div#annotation_panel').hide();

    activateHighlightEvents();
}

function openAddAnnotation(mouse) {
    /**
     * Opens annotation box with initial values.
     * */
    closeAnnotationBox();

    $('#annotation_panel_title').html(langAddNewNote);      // Can be sent from server in user language.
    $('#date_info').html('<i class="icon icon-pencil"></i> ' + langAnnotationInfoText);
    $('#date_info').attr("");
    $('#text_area').val("");

    var textArea = document.getElementById('text_area');
    textArea.focus();

    $('div#annotation_panel').css({
        position: 'absolute',
        top: mouse.pageY - 40 + 'px',
        left: mouse.pageX - 20 + 'px'
    }).show('fast');
    $('#annotation_remove_but').hide();
    activateShowAnnotation();
}

function showAnnotation(mouse, data) {
	$('#annotation_panel_title').html(data.message);
    $('#date_info').html('<i class="icon icon-time"></i> ' + data.time);
    $('#date_info').attr("title", data.last_updated);
    $('#text_area').val(data.annotation);

    var textArea = document.getElementById('text_area');
    textArea.focus();
    moveCaretToEnd(textArea);

    $('div#annotation_panel').css({
        position: 'absolute',
        top: mouse.pageY - 40 + 'px',
        left: mouse.pageX - 20 + 'px'
    }).show('fast');

    $("highlight").tooltip("hide");
    $('#annotation_remove_but').show();

    activateShowAnnotation();
}

function getAndShowAnnotation(mouse) {
    /**
     * Gets the corresponding annotation and shows the annotation box.
     * */
    closeAnnotationBox();
    $.ajax({
        type: 'POST',
        url: '/youraccount/getannotation',
        data: {
            'path': location.pathname,
            'id': currentAnnotationId
        },
        dataType: 'json',
        success: function(data) {
        	showAnnotation(mouse, data);
        }
    });
}

function removeAnnotation(annotationId) {
    /**
     * Removes the annotation with the given id.
     * */
	$("div.tooltip").remove();
    var htmlCode = $('div.highlightable').html();

    elem = $('highlight[high_anno_id=' +annotationId + ']')
    elem.removeClass('has_annotation').tooltip('destroy');
    addHighlightTooltip(elem[0], 'hover', 'mouse');

    annotationTooltipOptions.deleteTooltipWithId(annotationId);
    $.ajax({
        type: 'POST',
        url: '/youraccount/removeannotation',
        dataType: 'json',
        data: {
            'path': location.pathname,
            'id': annotationId
        },
        success: function(data) {
            if (data) {
                if (undoStack.lastOperationRecord() == 'DeletedHighlight') {
                    undoStack.recordDeletedHighlight(htmlCode, annotationId, data.annotation, data.last_updated);
                } else if (undoStack.lastOperationRecord() == 'RemoveAll') {
                    undoStack.recordLastRemoved(annotationId, data.annotation, data.last_updated);
                }
            }
        }
    });
}

function highlightMouseover(mouse) {
    /**
     * Defines the operations when the mouse is over an highlight
     * element.
     * */
    if (objectMouseOn.style.backgroundColor == 'transparent') {
        return;
    }

	tooltipTopPos = mouse.pageY;
	tooltipLeftPos = mouse.pageX;
}

function activateShowAnnotation() {
    /**
     * Activates click event on highlight with has_annotation class to
     * continue its work after creating new highlight.
     * */
    $('highlight.has_annotation').die('click');
    $('highlight.has_annotation').live('click', function(mouse) {
    	$("#annotation_panel").hide();
        currentAnnotationId = $(this).attr('high_anno_id');
        getAndShowAnnotation(mouse);
    });
}

function addAnnotationTooltip(elem, annotationId, annotationText) {
	 elem.tooltip({
         html: true,
         trigger: 'hover',
         placement: 'mouse',
         title: '<table id="table-anno-tooltip" class="anno-options-tooltip"> \
                     <tr id="row-anno-tooltip"> \
                         <td high_anno_id="' + annotationId + '" onclick="clickAnnotationEdit(this, event)" id="col-anno-tooltip-left"> \
         					<i id="icon-anno-tooltip" class="icon icon-white icon-edit" high_anno_id="'+ annotationId +'"></i> \
                         </td> \
                         <td id="col-anno-tooltip-right"> \
                             <span>' + annotationText +'</span> \
                         </td> \
                     </tr> \
                 </table>',
         delay: {
             show: 250,
             hide: 2000
         }
     });
}

function addHighlightTooltip(elem, triggerP, placementP) {
	highlightId = $(elem).attr('high_anno_id');
	var title = '\
		<div id="edit_menu_link_1" class="option_menu_text_container" high_anno_id="' + highlightId + '" onclick="optionMenuTextContainerClick(this, event)"> \
			<span class="option_menu_text" id="add"><i class="icon icon-pencil"></i> ' + langAddAnnotation + '</span> \
        </div> \
        <div id="edit_menu_link_2" class="option_menu_text_container" high_anno_id="' + highlightId + '" onclick="optionMenuTextContainerClick(this, event)"> \
            <span class="option_menu_text" id="remove"><i class="icon icon-trash"></i> ' + langDelete + '</span>\
        </div>'

	$(elem).tooltip({
        html: true,
        trigger: triggerP,
        placement: placementP,
        title: '<div class="anno-options-tooltip" high_anno_id="' + highlightId + '">' + title + colorContent + '</div>',
        delay: {
            show: 250,
            hide: 2000
        }
	});

	return elem;
}

function activateHighlightEvents() {
    /**
     * Activates events of highlight elements to continue its work after
     * creating new highlight.
     * */

	$("highlight:not(.has_annotation)").each(function(){
		addHighlightTooltip(this, 'hover', 'mouse');
	});

//	$("highlight:not(.has_annotation)").die('mousemove');
//	$("highlight:not(.has_annotation)").live('mousemove', function(mouse) {
//        objectMouseOn = this;
//        highlightMouseover(mouse);
//    });

//	$("highlight:not(.has_annotation)").die('mouseenter');
//	$("highlight:not(.has_annotation)").live('mouseenter', function() {
//        $('div.option_menu').hide();
//    });

	$("highlight").die('mousemove');
	$("highlight").live('mousemove', function(mouse) {
        objectMouseOn = this;
        highlightMouseover(mouse);
    });

	$("highlight").die('mouseenter');
	$("highlight").live('mouseenter', function() {
        $('div.option_menu').hide();
    });
}

function deleteHighlight(object) {
    /**
     * Deletes an highlight object.
     * */
	$("div.tooltip").remove();
    if ($(object).hasClass('has_annotation')) {
        removeAnnotation($(object).attr('high_anno_id'));
    } else if (undoStack.lastOperationRecord() == 'DeletedHighlight') {
        undoStack.recordDeletedHighlight($('div.highlightable').html(), 0, '', '');
    }
    tagRemover(object);
}

function tagRemover(element) {
    /**
     * Removes the outer tag of given element.
     *
     * Aim is to combine child text nodes at borders of the deleted node with
     * the neighbor text nodes.
     * */
    var parent = element.parentNode;

    if (!element.children.length) {
		if (element.nextSibling && element.nextSibling.nodeType == 3) {
			element.innerHTML += $([element.nextSibling]).text();
			$(element.nextSibling).remove();
		}

		if (element.previousSibling && element.previousSibling.nodeType == 3) {
			element.previousSibling.nodeValue += $([element]).text();
			$(element).remove();
			return ;
		}
	} else {
		// Check if there will be any neighbor text nodes after modifications.
		if (element.nextSibling && element.nextSibling.nodeType == 3 && element.lastChild.nodeType == 3) {
			element.lastChild.nodeValue += $([element.nextSibling]).text();
			$(element.nextSibling).remove();
		}

		if (element.previousSibling && element.previousSibling.nodeType == 3 && element.firstChild.nodeType == 3) {
			element.previousSibling.nodeValue += $([element.firstChild]).text();
			$(element.firstChild).remove();
		}
    }

	$(element).before($(element).html());
	$(element).remove();
}

function moveCaretToEnd(element) {
    /**
     * Moves caret to the end of the text area of an annotation box.
     * */
    if(typeof element.selectionStart == "number") {
        element.selectionStart = element.selectionEnd = element.value.length;
    }
    else if(typeof element.createTextRange != "undefined") {
        element.focus();
        var range = element.createTextRange();
        range.collapse(false);
        range.select();
    }
}

function toggleAnnotationFromHighlight(annotationId, value) {
    /**
     * On add and remove annotation cases, simply updates indexes by setting
     * given 'value' to 'a' value of the corresponding entry.
     * */
    var obj = $('[high_anno_id=' +currentAnnotationId + ']')[0];
    if(!obj) {
        return;
    }

    if(obj.children.length) {
        var childId = $([obj.children[0]]).attr('hl_id');
        try {
            highlightIndexes.nodes[childId].a = value;
        } catch(err) {
            constructJsonObject();
            return;
        }

    } else {
        var parentId = $([obj.parentNode]).attr('hl_id');
        try {
            var arr = highlightIndexes.leaves[parentId];
        } catch(err) {
            constructJsonObject();
            return;
        }
        for (var item in arr) {
            if (arr[item].id == annotationId) {
                highlightIndexes.leaves[parentId][item].a = value;
            }
        }
    }

    save();     // After update of highlight indexes save them.
}

$.fn.tooltip.Constructor.prototype.init = function (type, element, options) {
    var eventIn
      , eventOut

    this.type = type
    this.$element = $(element)
    this.options = this.getOptions(options)
    this.enabled = true

    if (this.options.trigger == 'click') {
      this.$element.on('click.' + this.type, this.options.selector, $.proxy(this.toggle, this))
    } else if (this.options.trigger != 'manual') {
      eventIn = this.options.trigger == 'hover' ? 'mouseenter' : 'focus'
      eventOut = this.options.trigger == 'hover' ? 'mouseleave' : 'blur'
      this.$element.on(eventIn + '.' + this.type, this.options.selector, $.proxy(this.enter, this))
      this.$element.on(eventOut + '.' + this.type, this.options.selector, $.proxy(this.leave, this))
    }

    this.options.selector ?
      (this._options = $.extend({}, this.options, { trigger: 'manual', selector: '' })) :
      this.fixTitle()

      return options;
}

$.fn.tooltip.Constructor.prototype.show = function () {
    var $tip
    , inside
    , pos
    , actualWidth
    , actualHeight
    , placement
    , tp

  if (this.hasContent() && this.enabled) {
    $tip = this.tip()
    this.setContent()

    if (this.options.animation) {
      $tip.addClass('fade')
    }

    placement = typeof this.options.placement == 'function' ?
      this.options.placement.call(this, $tip[0], this.$element[0]) :
      this.options.placement

    inside = /in/.test(placement)

    $tip
      .detach()
      .css({ top: 0, left: 0, display: 'block' })
      .insertAfter(this.$element)

    pos = this.getPosition(inside)

    actualWidth = $tip[0].offsetWidth
    actualHeight = $tip[0].offsetHeight

    switch (inside ? placement.split(' ')[1] : placement) {
      case 'bottom':
        tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - actualWidth / 2}
        break
      case 'top':
        tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2}
        break
      case 'left':
        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth}
        break
      case 'right':
        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width}
        break
      case 'mouse':
    	  tp = {top: tooltipTopPos - ($tip.height() / 2), left: tooltipLeftPos}
    	  break
    }

    if (placement == 'mouse') {
    	placement = 'right';
    }

    $tip
      .offset(tp)
      .addClass('annotation-tooltip')
      .addClass(placement)
      .addClass('in')
  }
}

function clickAnnotationEdit(elem, mouse) {
	currentAnnotationId = $(elem).attr("high_anno_id");

	var title = '\
		<div id="edit_menu_link_1" class="option_menu_text_container" high_anno_id="' + currentAnnotationId + '" onclick="optionMenuTextContainerClick(this, event)"> \
			<span class="option_menu_text" id="add"><i class="icon icon-pencil"></i> ' + langEditAnnotation + '</span> \
        </div> \
        <div id="edit_menu_link_2" class="option_menu_text_container" high_anno_id="' + currentAnnotationId + '" onclick="optionMenuTextContainerClick(this, event)"> \
            <span class="option_menu_text" id="remove"><i class="icon icon-trash"></i> ' + langDelete + '</span>\
        </div>'

	$(elem).tooltip({
        html: true,
        trigger: 'click',
        placement: 'left',
        title: '<div class="anno-options-tooltip" high_anno_id="' + currentAnnotationId + '">' + title + colorContent + '</div>',
        delay: {
            show: 250,
            hide: 2000
        },
        template: '<div id="readonly-anno-options" class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>'
	});

	$(elem).tooltip('show');

//	getAndShowAnnotation(mouse);
}
