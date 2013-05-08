$(document).ready(function() {
    /**
     *   'highlightIndexes' variable keeps highlights on window in json format. Updated after
     *  every operation and sent to server. It is saved in serialized format to reduce
     *  space requirement.
     *
     *   An example entry:
     *   {
     *   "leaves":{"43":[{"s":22,"e":35,"a":0,"id":"2","n":0,"c":"rgb(255, 255, 0)"}],
     *             "73":[{"s":357,"e":406,"a":1,"id":"0","n":0,"c":"rgb(255, 255, 0)"}]},
     *   "nodes":{"57":{"c":"rgb(255, 255, 0)","id":"1","a":0}}
     *   }
     *
     *   'leaves' key corresponds to highlight elements around text nodes. It has
     *   keys as numbers which are ids of each dom element. These ids are assigned
     *   when highlight mode is on. For the highlight nodes around text nodes, their
     *   parent nodes are used as keys i.e 43, 73. Highlight nodes under them are listed
     *   in dictionary format.
     *     * 's' denotes start position,
     *     * 'e' denotes end position,
     *     * 'a' denotes whether that highlight element has an annotation. if yes 1, otherwise 0 values are used.
     *     * 'id' denotes id 'high_anno_id' attr value of the highlight nodes. It is used to keep track of
     *     seperated highlight nodes which are result of a selection. For example, the user makes a selection starting
     *     from a <p> element and ending to another <div>. There are more than one highlight nodes as a result
     *     of this selection. This value is also used for annotation id.
     *     * 'n' denotes the child number that the indices are valid on.
     *     * 'c' denotes the color.
     *
     *   'nodes' key corresponds to a node level highlighting information. For nodes, there is no need to save indices,
     *   it is enough to keep color information, since each node will have a unique identifier (57 in example above)
     *   and they will be highlighted directly. The 'c', 'id', and 'a' keys have same meanings as above.
     *
     * */

    // "Id of a highlight" phare denotes 'high_anno_id' attribute value.

    highlightIndexes = {};
    highlightID = 0;                    // Next 'high_anno_id' value for highlight nodes.
    selectionStyleSheet = null;         // StyleSheet of selection
    highlightState = 0;                 // Normal highlightState, highlighting and annotations are not allowed.
    highlightColor = $(document.getElementsByClassName("color")[0]).css('background-color');    // Sets default color.
    realHighlightArea = $('div.highlightable').get(0);
    undoStack = {
        'operationRecord': [],
        'highlightStack': [],
        'deletedHighlightStack': [],
        'removeAllStack': [],
        'insertedNoteStack': [],
        'deletedNoteStack': [],
        'editedNoteStack': [],
        'addOperationRecord': function(operation) {
            /**
             * Adds new operation record
             * */
            this.operationRecord.push(operation);
            $('button#undo').removeClass('disabled');
            return this.operationRecord;
        },
        'recordHighlight': function(htmlCode) {
            /**
             * Stores current html code of the highlightable area before each highlight operation.
             * */
            this.highlightStack.push(htmlCode);
            return this.highlightStack;
        },
        'recordDeletedHighlight': function(htmlCode, annotationId, annotation, lastUpdated) {
            /**
             * Keeps html code of the highlightable area and
             * the ID, content and last update time of the deleted
             * annotation to achieve undo after deleting an highlight
             * */
            this.deletedHighlightStack.push([annotationId, annotation, lastUpdated, htmlCode]);
        },
        'lastOperationRecord': function() {
            /**
             * Returns the last operation record
             * */
            return this.operationRecord[this.operationRecord.length - 1];
        },
        'recordRemoveAll': function(htmlCode) {
            /**
             * Keeps html code and an empty array (contains arrays of
             * deleted hightlights) to achieve undo after clicked
             * remove all.
             * */
            this.removeAllStack.push([htmlCode, []]);
            return this.removeAllStack;
        },
        'recordLastRemoved': function(id, annotation, date) {
            /**
             * Adds the removed higlights to last element of
             * removeAllStack. It must be called when last operation
             * record is "removeAll" to work proper.
             * */
            this.removeAllStack[this.removeAllStack.length - 1][1].push([id, annotation, date]);
            return this.removeAllStack;
        },
        'recordInsertNote': function(id) {
            /**
             * Keeps id of highlight to achieve undo after
             * a node inserted.
             * */
            this.insertedNoteStack.push([id]);
            return this.insertedNoteStack;
        },
        'recordDeletedNote': function(id, text, date) {
            /**
             * Keeps id, content and last update time of the deleted
             * annotation to achieve undo after removing a note.
             * */
            this.deletedNoteStack.push([id, text, date]);
            return this.deletedNoteStack;
        },
        'recordEditedNote': function(id, text, date) {
            /**
             * Keeps id, content and last update time of the deleted
             * annotation to achieve undo after editing an highlight
             * */
            this.editedNoteStack.push([id, text, date]);
            return this.editedNoteStack;
        },
        'undo': function() {
            /**
             * Performs correspoing undo operation and saves the
             * current highlights.
             * */
            if (!this.operationRecord.length) {
                return;
            }
            var operation = this.operationRecord.pop();
            this['undo' + operation]();
            if (this.operationRecord.length == 0) {
            	$('button#undo').addClass('disabled');
            }
            constructJsonObject();
        },
        'undoHighlight': function() {
            /**
             * To undo an highlight, it just replaces the html code of
             * highlight with the top of the highlightStack.
             * */
            $('div.highlightable').html(this.highlightStack.pop());
            this.recoverAnnotationTooltips();
        },
        'undoInsertedNote': function() {
            /**
             * To undo an inserted note, it removes the annotation with
             * corresponding ID.
             * */
            var element = this.insertedNoteStack.pop();
            removeAnnotation(element[0]);
        },
        'undoDeletedNote': function() {
            /**
             * To undo an deleted note, sends corresponding note information
             * to insertDeletedNote function to insert it back to database.
             * */
            var element = this.deletedNoteStack.pop();
            this.insertDeletedNote(element);
        },
        'undoDeletedHighlight': function() {
            /**
             * To undo an deleted highlight, it replaces the html code
             * of highlight area with the top of the
             * deletedHighlightStack and sends that element to
             * insertDeletedNote if corresponding highligt contains an
             * annotation.
             * */
            var element = this.deletedHighlightStack.pop();
            $('div.highlightable').html(element[3]);
            if (element[1] != '') {
                this.insertDeletedNote(element);
            }
            this.recoverAnnotationTooltips();
        },
        'undoRemoveAll': function() {
            /**
             * To undo "Remove All", it replaces the html code of
             * highlight area with the top of the removeAllStack and
             * sends each deleted highlight to insertDeletedNote
             * function.
             * */
            var element = this.removeAllStack.pop();
            $('div.highlightable').html(element[0]);
            for (var i = 0; i < element[1].length; i++) {
                this.insertDeletedNote([element[1][i][0], element[1][i][1], element[1][i][2]]);
            }
        },
        'undoEditedNote': function() {
            /**
             * To undo an edited note, sends corresponding note information
             * to insertDeletedNote function to update it.
             * */
            var element = this.editedNoteStack.pop();
            this.insertDeletedNote(element);
        },
        'insertDeletedNote': function(element) {
            /**
             * Sends annotation information to the server to save or edit the
             * corresponding annotation.
             * */
            var form = {
                'path': location.pathname,
                'annotation': element[1],
                'id': element[0],
                'last_updated': element[2]
            };

            var selector = 'highlight[high_anno_id=' + element[0] + ']';

            $(selector).addClass('has_annotation');
            $(selector).tooltip('destroy');
            addAnnotationTooltip($(selector), element[0], element[1]);

            annotationTooltipOptions.addNewTooltip(element[0], element[1]);
            $.ajax({
                type: 'POST',
                url: '/youraccount/saveannotation',
                dataType: 'json',
                data: form,
                success: function(data) {
                }
            });
        },

        'recoverAnnotationTooltips' : function() {
        	var tooltips = annotationTooltipOptions.getWholeList();

        	for (var id in tooltips) {
        		addAnnotationTooltip($("highlight[high_anno_id=" + id + "]"), id, tooltips[id]);
        	}
        }
    };

    // Hide html elements that will be used as pop-ups.
    $('#color_palette').hide();
    $('#palette_but').hide();
    $('div.option_menu').hide();
    $('div.highlight_menu_edit').hide();

    $(document.getElementsByClassName("color")[0]).addClass('selected_color');

    $('#color_palette').draggable({
    	handle: "#color_palette_header"
	});

    $('#palette_but').click(function(){
        var pos = $('div.highlightable').offset();
        pos.right = parseInt($('div.highlightable').css('width'));
        $("div#color_palette").css("left", pos.right);
        $("div#color_palette").css("top", pos.top - 250);
        $("div#color_palette").fadeIn("fast");
        $(this).hide();
    });

    $("#close_color_palette_button").click(function() {
        $('#color_palette').fadeOut("fast");
        $("#palette_but").fadeIn("fast");
    });

    $("#undo").click(function() {
        undoStack.undo();
        closeAnnotationBox();
    });

    $("#remove_all").click(function() {
    	$("div.tooltip").remove();
        undoStack.addOperationRecord('RemoveAll');
        undoStack.recordRemoveAll($('div.highlightable').html());
        $('highlight').each(function() {
            if ($(this).hasClass('has_annotation')) {
                removeAnnotation($(this).attr('high_anno_id'));
            }
            tagRemover(this);
        });
        constructJsonObject();
        closeAnnotationBox();
    });

    /**
     * When highlight image is clicked, go back to server and get user's previous
     * highlights that made on that record. After getting options, rearrange the
     * context html based on highlights.
     * */
    $('img#activate_highlight').click(function() {
        if (!highlightState) {
            highlightState = 1;
            $.ajax({
                type: 'POST',
                url: '/youraccount/loadhighlights',
                data: {
                    'path': location.pathname
                },
                dataType: 'json',
                success: function(data) {
                    var jsonFormat;
                    if (!data.highlights_from_server) {
                        return;
                    } else if (data.msg != '') {
                        var msg = confirm(data.msg);
                        if (msg) {
                            jsonFormat = JSON.parse(data.highlights_from_server);
                            loadHighlights(jsonFormat);
                        } else {
                            removeHighlights();
                        }
                    } else {
                        var jsonFormat = JSON.parse(data.highlights_from_server);
                        loadHighlights(jsonFormat);
                    }
                    activateHighlightEvents();

                    annotations = JSON.parse(data.annotations);
                    // Pull all of the user annotations into annotationCache
                    // and reate tooltip for each annotation.

                    $("highlight.has_annotation").each(function(){
                    	var annotationID = $(this).attr('high_anno_id');
                    	annotationTooltipOptions.addNewTooltip(annotationID, annotations[annotationID]);
                    	addAnnotationTooltip($(this), annotationID, annotations[annotationID]);
                    });
                }

            });

            changeSelectionStyle(highlightColor);

            var pos = $('div.highlightable').offset();
            pos.right = parseInt($('div.highlightable').css('width'));
            $("div#color_palette").css("left", pos.right);
            $("div#color_palette").css("top", pos.top - 250);
            $("div#color_palette").fadeIn("fast");

            $('div.highlightable').css('border', '2px solid orange');
            $('div.highlightable:not(.anno-options-tooltip)').mouseup(function() {
                if (colorizeSelection(highlightColor) != -1) {
                	constructJsonObject();
                    deselector();
                    activateHighlightEvents();
                    activateShowAnnotation();
                }
            });
            $(this).removeClass("unchecked")
            $(this).addClass("checked")

            var i = 0;
            $('div.highlightable').find('*').each(function(){
                $(this).attr('hl_id', i);
                i++;
            });

        } else {
            highlightState = 0;
            $('div.highlightable').css('border', '');
            $('div.highlightable').unbind('mouseup');
            $('#palette_but').hide();
            closeColorPalette();
        }
    });

    $('div.color').click(function() {
        $('.selected_color').removeClass('selected_color');
        highlightColor = $(this).css('background-color');
        changeSelectionStyle(highlightColor);
        $(this).addClass('selected_color');
    });

    $('button#save_highlights').click(function() {
        constructJsonObject();
    });
});

function removeHighlights() {
    /**
     * Removes all of the annotations and highlights before loading them.
     * */
    $.post('/youraccount/savehighlights', {
        'highlights_to_be_saved': JSON.stringify({}),
        'path': location.pathname
    }, function(data) {});

    annotationTooltipOptions.deleteWholeList();

    $.ajax({
        type: 'POST',
        url: '/youraccount/removeannotation',
        dataType: 'json',
        data: {
            'path': location.pathname,
            'id': ""
        },
        success: function(data) {}
    });

    $("highlight").each(function() {
        tagRemover(this);
    });
}

function changeSelectionStyle(color) {
    /**
     * Changes the style of the selection corresponding to given color.
     * */
    if (!selectionStyleSheet) {
        var styleSheet = document.createElement('style');
        document.getElementsByTagName('head')[0].appendChild(styleSheet);
        selectionStyleSheet = document.styleSheets[document.styleSheets.length - 1];
    }

    removeSelectionStyle();

    try {
        selectionStyleSheet.insertRule('.highlightable *::-moz-selection { background: ' + color + '; }', 0); //firefox
    }
    catch (err) {}
    try {
        selectionStyleSheet.insertRule('.highlightable *::selection { background: ' + color + '; }', 0); //explorer, chrome, opera
    }
    catch (err) {}
    try {
        selectionStyleSheet.insertRule('.highlightable *::-webkit-selection { background: ' + color + '; }', 0);
    }
    catch (err) {}
}

function removeSelectionStyle() {
    /**
     * Removes all the rules in the selectionStyleSheet.
     * */
    if (selectionStyleSheet.cssRules) { // all browsers, except IE before version 9
        while(selectionStyleSheet.cssRules.length > 0) {
            selectionStyleSheet.deleteRule(0);
        }
    } else { // Internet Explorer before version 9
        for (var i = 0; i < selectionStyleSheet.rules.length; i++) {
            selectionStyleSheet.removeRule(0);
        }
    }
}

function constructJsonObject() {
    /**
     * Generates a JSON string represents the current structure of
     * the highlight and annotations.
     * */

	$("div.tooltip").remove();

    highlightIndexes.leaves = {};
    highlightIndexes.nodes = {};
    var visited = [];
    $('highlight').each(function(){
        if ($(this).children().length) {
            var hasAnnotation = $(this).hasClass('has_annotation') ? 1 : 0;
            var id = $(this).attr('high_anno_id');
            $(this).children().each(function(){
                var key = $(this).attr('hl_id');
                highlightIndexes.nodes[key] = {};
                highlightIndexes.nodes[key].c = this.parentNode.style.backgroundColor;
                highlightIndexes.nodes[key].id = id;
                highlightIndexes.nodes[key].a = hasAnnotation;
            });
        } else {
            var parentHighlightId = $([this.parentNode]).attr('hl_id');
            if (parentHighlightId != -1) {
                highlightIndexes.leaves[parentHighlightId] = getHighlightIndexes(this.parentNode);

                var visitedNode = {};
                visitedNode.node = this.parentNode;
                visitedNode.id = parentHighlightId;
                visited.push(visitedNode);
                $([this.parentNode]).attr('hl_id', -1);
            }
        }
    });

    for (var item in visited) {
        $([visited[item]['node']]).attr('hl_id', visited[item]['id']);
    }

    save();             // After each update simply save the changes.
}

function save() {
    var jsonText = "";
    if (!jQuery.isEmptyObject(highlightIndexes.nodes) || !jQuery.isEmptyObject(highlightIndexes.leaves)) {
        jsonText = JSON.stringify(highlightIndexes);
    }

    $.post('/youraccount/savehighlights', {
        'highlights_to_be_saved': jsonText,
        'path': location.pathname
    }, function(data) {});
}

function loadHighlights(indexes)
{
    /**
     * Reconstructs the page acording to indexes stored in database.
     * */
    var dummyRange, highlightElem;
    // For elements
    for (var node in indexes['nodes']) {
        var element = $('[hl_id = "' + node +'"]')[0];
        dummyRange = document.createRange();
        dummyRange.selectNode(element);

        highlightElem = document.createElement('highlight');
        highlightElem.style.backgroundColor = indexes['nodes'][node].c;
        $([highlightElem]).attr('high_anno_id', indexes['nodes'][node].id);

        if (indexes['nodes'][node].a) {
            $([highlightElem]).addClass('has_annotation');
        }
        dummyRange.surroundContents(highlightElem);
        cleanEmptyNodeAround(highlightElem);
        var numericId = parseInt(indexes['nodes'][node].id)
        highlightID = (numericId >= highlightID) ? numericId + 1 : highlightID;
    }

    if (!jQuery.isEmptyObject(indexes['nodes'])) {
        cleanDuplicates(realHighlightArea);
        eliminateInsideHighlightElems(realHighlightArea);
    }

    // For text nodes
    for (var item in indexes['leaves']) {
        var parent = $('[hl_id = "' + item +'"]')[0];
        var highlights = indexes['leaves'][item];

        for (var elem in highlights) {
            dummyRange = document.createRange();
            dummyRange.setStart(parent.childNodes[highlights[elem].n], highlights[elem].s);
            dummyRange.setEnd(parent.childNodes[highlights[elem].n], highlights[elem].e);

            highlightElem = document.createElement('highlight');
            highlightElem.style.backgroundColor = highlights[elem].c;
            $([highlightElem]).attr('high_anno_id', highlights[elem].id);

            if (highlights[elem].a) {
                $([highlightElem]).addClass('has_annotation');
            }
            dummyRange.surroundContents(highlightElem);
            cleanEmptyNodeAround(highlightElem);
            var numericId = parseInt(highlights[elem].id) ;
            highlightID = (numericId >= highlightID) ? numericId + 1 : highlightID;

            var emptyText = highlightElem.previousSibling;
            if(emptyText && emptyText.nodeType == 3 && emptyText.nodeValue == "")
                highlightElem.parentNode.removeChild(emptyText);
        }
    }
}

function getHighlightIndexes(node) {
    /**
     * For the given node containing text nodes as well, it calculates indexes of
     * highlight nodes and contructs 'leaves' key of the json object.
     * */

    var isEmptyBeforeHighlight = false;
    var indexes = [];
    var ind = 0;
    var textLen = 0;
    var children = node.childNodes;
    for(var i = 0, child; child = children[i]; i++) {
    	if (child.nodeType == 1 && child.tagName.toLowerCase() == 'highlight' && !child.children.length) {
            indexes[ind] = {};
            if (isEmptyBeforeHighlight) {
                indexes[ind].s = children[i-1].nodeValue.length;
                indexes[ind].n = i ?  (i - 1) : 0;
                isEmptyBeforeHighlight = false;
            } else {
                indexes[ind].s = 0;
                indexes[ind].n = i;
            }
            indexes[ind].e = indexes[ind].s + $([child]).text().length;
            indexes[ind].a = $([child]).hasClass('has_annotation') ? 1 : 0;
            indexes[ind].id = $([child]).attr('high_anno_id');
            indexes[ind++].c = child.style.backgroundColor;
            textLen = 0;
        } else if (child.nodeType == 3) {
            isEmptyBeforeHighlight = true;
        } else if (child.nodeType == 1) {
            isEmptyBeforeHighlight = false;
        }
    }
    return indexes;
}

/**
 *
 *    Highlight Functions
 *
 **/

function highlightDomTree(node, realRange) {
    /**
     * Highlights the nodes descendant of the given node, if they are in selection
     * (realRange). For each node, constructs a range object and check whether its
     * border is outside or they intersects or overlaps.
     * If there is an intersection, give another chance to that node's children.
     *
     * The aim is keeping the 'highlight' elements with minimum depth in DOM tree.
     * Also, a 'highlight' element does not contain any other 'highlight' elements.
     * */
    var children = node.childNodes;
    var dummyRange;
    for (var i = 0, child; child = children[i]; i++) {
        if (child.nodeType == 1 && child.tagName.toLowerCase() == 'highlight') {
            continue;
        } else if (child.nodeType == 3 && $.trim(child.nodeValue) == "") {
            continue;
        }

        dummyRange = document.createRange();
        dummyRange.selectNode(child);

        if ($.trim(dummyRange.toString()) == "") continue;

        var startEnd = dummyRange.compareBoundaryPoints(Range.START_TO_END, realRange);
        var endStart = dummyRange.compareBoundaryPoints(Range.END_TO_START, realRange);
        var startPos = dummyRange.compareBoundaryPoints(Range.START_TO_START, realRange);
        var endPos = dummyRange.compareBoundaryPoints(Range.END_TO_END, realRange);

        if (startEnd < 0 || endStart > 0) { // Outside.
            continue;
        } else if (startPos < 0) {// Intersects from left.
            highlightDomTree(child, realRange);
        } else if (endPos > 0) {// Intersects from right.
            highlightDomTree(child, realRange);
        } else {// Overlaps
            // If it does not contain another highlighted child, highlight it.
            var curr = [child];
            var highlightedNodes = $(curr).find('highlight');

            if (highlightedNodes.length) {
                highlightDomTree(child, realRange);
            } else {
                highlightNode(child, highlightColor, highlightID);
                continue;
            }
        }
    }
}

function cleanEmptyNodeAround(node) {
    /**
     * After surrounding text with highlight node, there is an empty text node.
     * This function simply removes that empty node.
     * */
    if (node.nextSibling && node.nextSibling.nodeType == 3 && node.nextSibling.nodeValue == "") {
        node.parentNode.removeChild(node.nextSibling);
    }

    if (node.previousSibling && node.previousSibling.nodeType == 3 && node.previousSibling.nodeValue == "") {
        node.parentNode.removeChild(node.previousSibling);
    }
}

function colorizeSelection(color) {
    /**
     * When the user made a selection, colorizes the selected text with the
     * selection color.
     * */
    var dummyRange;
    var highlightElem;
    var selectionRange;
    var highlightedParents;

    if (window.getSelection) { // all browsers, except IE before version 9
        selectionRange = window.getSelection();
    } else if (document.selection && document.selection.createRange) {
        selectionRange = document.selection.createRange();
    }

    if (selectionRange.isCollapsed) {
        return -1;
    } else {
    	$('div.tooltip').remove();
        undoStack.addOperationRecord('Highlight');
        undoStack.recordHighlight($('div.highlightable').html());
        var range = selectionRange.getRangeAt(0);

        if ($.trim(range.toString()) == "") {
            return -1;
        }
        // store the start and end points of the current selection, because the selection will be removed
        var startContainer = range.startContainer;
        var startOffset = range.startOffset;
        var endContainer = range.endContainer;
        var endOffset = range.endOffset;

        // if selection is outside of the highlightable area, rearrange start and end borders
        if (!isHighlightable(startContainer, realHighlightArea)) {
            deselector();
            return -1;
        }
        if (!isHighlightable(endContainer, realHighlightArea)) {
            deselector();
            return -1;
        }

        //For opera, before modifying DOM Tree, need to remove selection.
        try {
            selectionRange.removeAllRanges();
        } catch (err) {

        }

        /**
         * Start of MathJax Control
         * */

        // Check if there is any MathJax element. If there is, make sure that
        // highlight element surrounds the whole MathJax element.
        var startContMathJaxParent = $([startContainer]).parentsUntil($('div.highlightable'), '[class*="MathJax"]');
        var endContMathJaxParent = $([endContainer]).parentsUntil($('div.highlightable'), '[class*="MathJax"]');

        if (startContMathJaxParent.length && ($(startContMathJaxParent).parentsUntil($('div.highlightable'), 'highlight')).length) {
            range.setStartAfter(startContMathJaxParent[0].parentNode.nextSibling);
            startContainer = range.startContainer;
            startContMathJaxParent = [];
        }
        if (endContMathJaxParent.length && ($(endContMathJaxParent).parentsUntil($('div.highlightable'), 'highlight')).length) {
            range.setEndBefore(endContMathJaxParent[0].parentNode.previousSibling);
            endContainer = range.endContainer;
            endContMathJaxParent = [];
        }

        if (startContMathJaxParent.length > 0 && endContMathJaxParent.length > 0) {
            if((startContMathJaxParent[0] == endContMathJaxParent[0])) {
                highlightNode(startContMathJaxParent[0], color, highlightID);
                return;
            } else {
                highlightNode(startContMathJaxParent[0], color, highlightID);
                range.setStartAfter(startContMathJaxParent[0]);

                highlightNode(endContMathJaxParent[0], color, highlightID);
                range.setEndBefore(endContMathJaxParent[0]);
            }
        } else if (startContMathJaxParent.length > 0) {
            highlightNode(startContMathJaxParent[0], color, highlightID);
            range.setStartAfter(startContMathJaxParent[0]);
        } else if (endContMathJaxParent.length > 0) {
            highlightNode(endContMathJaxParent[0], color, highlightID);
            range.setEndBefore(endContMathJaxParent[0]);
        }

        /**
         * End of MathJax Control
         * */

        // If selection starts and ends in the same element, no need extra operation.
        if (startContainer == endContainer) {
            highlightedParents = $([startContainer]).parentsUntil($('div.highlightable'), 'highlight');
            if (!highlightedParents.length) {
                highlightElem = document.createElement('highlight');
                highlightElem.style.backgroundColor = color;
                $([highlightElem]).attr('high_anno_id', highlightID);
                range.surroundContents(highlightElem);
                cleanEmptyNodeAround(highlightElem);
                cleanDuplicates(startContainer.parentNode);
                eliminateInsideHighlightElems(startContainer.parentNode);
            }
            highlightID++;
            return;
        }

        // If the selection is seperated over different nodes, need to rearrange
        // the range object(start and end points).
        // Highlight start and end text nodes manually and let the range object
        // only contains elements.
        if (startContainer.nodeType == 3) {
            range.setStartAfter(startContainer);

            highlightedParents = $([startContainer]).parentsUntil($('div.highlightable'), 'highlight');
            if (!highlightedParents.length) {
                dummyRange = document.createRange();
                dummyRange.selectNodeContents(startContainer);
                dummyRange.setStart(startContainer, startOffset);

                if ($.trim(dummyRange.toString()) != "") {
                    highlightElem = document.createElement('highlight');
                    highlightElem.style.backgroundColor = color;
                    $([highlightElem]).attr('high_anno_id', highlightID);
                    dummyRange.surroundContents(highlightElem);
                    cleanEmptyNodeAround(highlightElem);
                }
            }
        }

        if (endContainer.nodeType == 3) {
            range.setEndBefore(endContainer);

            highlightedParents = $([endContainer]).parentsUntil($('div.highlightable'), 'highlight');
            if (!highlightedParents.length) {
                dummyRange = document.createRange();
                dummyRange.selectNodeContents(endContainer);
                dummyRange.setEnd(endContainer, endOffset);

                if ($.trim(dummyRange.toString()) != "") {
                    highlightElem = document.createElement('highlight');
                    highlightElem.style.backgroundColor = color;
                    $([highlightElem]).attr('high_anno_id', highlightID);
                    dummyRange.surroundContents(highlightElem);
                    cleanEmptyNodeAround(highlightElem);
                }
            }
        }

        // Check new range object after rearrangement of start and end points.
        if (range.collapsed) {
            cleanDuplicates(startContainer.parentNode);
            highlightID++;
            return;
        }

        var commonAncestorOfBorders = range.commonAncestorContainer;
        // Highlight the remaining slements.
        highlightDomTree(commonAncestorOfBorders, range);

        // This order should be followed for proper tree contruction.
        cleanDuplicates(commonAncestorOfBorders);
        eliminateInsideHighlightElems(commonAncestorOfBorders);
        highlightID++;
    }
}

function highlightNode(node, color, id) {
    /**
     * Highlights the given node with given color.
     * Creates a range object with given node and simply
     * adds a 'highlight' element around it.
     *  */
    var highlightElem = document.createElement('highlight');
    highlightElem.style.backgroundColor = color;

    var dummyRange = document.createRange();
    dummyRange.selectNode(node);
    $([highlightElem]).attr('high_anno_id', id);
    dummyRange.surroundContents(highlightElem);
    cleanEmptyNodeAround(highlightElem);
}

function eliminateInsideHighlightElems(commonAncestorOfBorders) {
    /**
     * Find 'highlight' elements and starts traversing the tree from these
     * elements to up. If the 'highlight' element is the only child of its parent,
     * removes the highlight tags and inserts around parent node.
     * */
    var tmpNId;
    var domTreeChanged = false;
    var foundFlag = false;
    var tryForUpperNode = false;
    var highlightedNodes = commonAncestorOfBorders.getElementsByTagName('highlight');
    var parentOfCommonAncestor = commonAncestorOfBorders.parentNode;
    for (var i = 0, node; node = highlightedNodes[i]; i++) {
        var parent = node.parentNode;
        var allSiblingsOfNode = parent.childNodes;
        if (allSiblingsOfNode.length <= 3) {
            for (var j = 0, tmpN; tmpN = allSiblingsOfNode[j]; j++) {
                if (tmpN.nodeType == 3 && $.trim(tmpN.nodeValue) == "") {
                    continue;
                } else if (!foundFlag && tmpN.nodeType == 1 && tmpN.tagName.toLowerCase() == 'highlight') {
                    tmpNId = $([tmpN]).attr('high_anno_id');
                    foundFlag = true;
                } else {
                    foundFlag = false;
                    break;
                }
            }

            if (foundFlag && parent != realHighlightArea) {
                if(parent == commonAncestorOfBorders) {
                    tryForUpperNode = true;
                }
                parent.innerHTML = node.innerHTML;
                highlightNode(parent, node.style.backgroundColor, tmpNId);

                // parent's depth is increased by one.
                cleanDuplicates(parent.parentNode.parentNode);
                domTreeChanged = true;
                foundFlag = false;
            }
        }
    }

    if (domTreeChanged) {
        var newLimit;
        if (tryForUpperNode) {
            newLimit = parentOfCommonAncestor;
        } else {
            newLimit = commonAncestorOfBorders;
        }

        eliminateInsideHighlightElems(newLimit);
    }
}

function cleanDuplicates(highlightAreaBorder) {
    /**
     * For the given node, if it has descendants with tag name 'highlight' and
     * it there are sibling highlight elements with same background color,
     * combines them.
     * */
    var node, prevSibl, nextSibl, tmp, prevSiblId, currentNodeId;
    var highlightedNodes = highlightAreaBorder.getElementsByTagName('highlight');

    // For last highlight node, search its right to eliminate empty valued text nodes.
    if(highlightedNodes)
    node = highlightedNodes[highlightedNodes.length - 1];
    nextSibl = node.nextSibling
    while (nextSibl && nextSibl.nodeType == 3 && $.trim(nextSibl.nodeValue) == "") {
        tmp = nextSibl;
        nextSibl = nextSibl.nextSibling;
        node.appendChild(tmp);
    }

    for (var i = highlightedNodes.length - 1; i > 0; i--) {
        node = highlightedNodes[i];
        prevSibl = node.previousSibling;

        currentNodeId = $([node]).attr('high_anno_id');
        prevSiblId = prevSibl ? $([prevSibl]).attr('high_anno_id') : currentNodeId; //If null just skip.
        if ($([node]).hasClass('has_annotation')) {
            if (prevSibl && $([prevSibl]).hasClass('has_annotation') && prevSiblId != currentNodeId) {
                continue;
            } else if (prevSibl && prevSibl.previousSibling &&
                $([prevSibl.previousSibling]).hasClass('has_annotation') && prevSiblId != currentNodeId) {
                continue;
            }
        }

        // Ignore empty valued next nodes and simply insert them into highlight node.
        while (prevSibl && prevSibl.nodeType == 3 && $.trim(prevSibl.nodeValue) == "") {
            tmp = prevSibl;
            prevSibl = prevSibl.previousSibling;
            node.insertBefore(tmp, node.firstChild);
        }

        if (prevSibl && prevSibl.nodeType == 1 && prevSibl.tagName.toLowerCase() == 'highlight' && prevSibl.style.backgroundColor == node.style.backgroundColor) {
            var prevChildLen = prevSibl.children.length;
            var thisChildLen = node.children.length;
            if ((prevChildLen && !thisChildLen) || (!prevChildLen && thisChildLen)) {
                continue;
            }

            var parentNode = node.parentNode;
            if ($([node]).hasClass('has_annotation')) {
                $([prevSibl]).attr('high_anno_id', currentNodeId);
                $([prevSibl]).addClass('has_annotation');
            } else if ($([prevSibl]).hasClass('has_annotation')) {
                $([node]).attr('high_anno_id', prevSiblId);
            } else if (prevSiblId > currentNodeId) {
                $([prevSibl]).attr('high_anno_id', currentNodeId);
            }
            prevSibl.innerHTML = prevSibl.innerHTML + node.innerHTML;
            parentNode.removeChild(node);
        }
    }
}

function isHighlightable(node, highlightArea) {
    /**
     * Checks whether the given node is in highlightable area.
     *
     * When the user made a text selection, simply check the start and end
     * containers of the selection.
     * */
    while (node) {
        if (node == highlightArea) {
            return true;
        }
        node = node.parentNode;
    }
    return false;
}

function deselector() {
    /**
     * Deselects the selected text.
     * */
    if (window.getSelection) {
        if (window.getSelection().empty) { // Chrome
            window.getSelection().empty();
        } else if (window.getSelection().removeAllRanges) { // Firefox
            window.getSelection().removeAllRanges();
        }
    } else if (document.selection) { // IE?
        document.selection.empty();
    }
}

function closeColorPalette() {
    $('#color_palette').fadeOut("fast");
    highlightState = 0;
    $('div.highlightable').css('border', '');
    $('div.highlightable').unbind('mouseup');

    $('highlight').each(function() {
        tagRemover(this);
    });

    $('img#activate_highlight').removeClass("checked")
    $('img#activate_highlight').addClass("unchecked")
    closeAnnotationBox();
    removeSelectionStyle();
}
