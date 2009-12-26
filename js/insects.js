// Convenience methods
var $ = goog.dom.$;
var $$ = goog.dom.$$;

var xhrSend = function (url, callback, context, method, queryDataString) {
	// Convenience method for responding to an xhr with a listener method and some context.
	xhr = new goog.net.XhrIo();
	goog.events.listen(xhr, goog.net.EventType.COMPLETE, callback, false, context);
	xhr.send(url, method, queryDataString);
}
	
var Main = function () {
	// Encompasses the between-moves game state (we call the server on each move(
	// and updates the display after each move.
	// TODO: we need to poll for the other player's actions
	this.selectedInsectName = null;
	this.selectedInsectColor = null;
	this.targetHexID = null;
	this.currentHexID = null;
};

Main.prototype.pieceSelected = function(event) {
	// The user selected an insect, ask the server where they can move
	//TODO: img instead of li is the target
	var item = goog.dom.getAncestorByTagNameAndClass(event.target, 'LI'); 
	this.selectedInsectName = item.id.split('-')[0];
	this.selectedInsectColor = item.id.split('-')[1];
	 
	var queryData = new goog.Uri(document.URL).getQueryData();
	queryData.add('insect_name', this.selectedInsectName);
	queryData.add('insect_color', this.selectedInsectColor);
	//queryData.add('current_hex', insectColor);
	xhrSend("show_moves?" + queryData.toString(), this.showMovesResponse, this);
};

Main.prototype.showMovesResponse = function(event) {
	// Highlight the hexes that the user can move to with the selected insect
	var response = event.target.getResponseJson();
	goog.array.forEach(response.hexes, function (hexID) {
		goog.dom.classes.add($(hexID), 'available-move');
	});
};

Main.prototype.hexClicked = function (event) {
	// A hex is clicked before moving an insect there
	var hex = goog.dom.getAncestorByTagNameAndClass(event.target, 'SPAN'); 
	if (goog.dom.classes.has(hex, 'available-move')) {
		var queryData = goog.Uri.QueryData.createFromMap(new goog.structs.Map({
			insect_name: this.selectedInsectName,
			insect_color: this.selectedInsectColor,
	//		current_hex: null, // TODO: get the current hex id
			target_hex: hex.id
		}));
		this.targetHexID = hex.id;
		queryData.extend(new goog.Uri(document.URL).getQueryData());
		xhrSend("/move", this.moveResponse, this, "POST", queryData.toString());
	}
};

Main.prototype.moveResponse = function (event) {
	// Administrative work to update the board after moving
	// TODO: check success
	var response = event.target.getResponseJson();
	goog.array.forEach(response.reveal_hex_ids, function (hexID) {
		goog.dom.classes.remove($(hexID), 'hidden');
	});
	this.updateBoard(this.selectedInsectName, this.selectedInsectColor, this.currentHexID, this.targetHexID);
};

Main.prototype.updateBoard = function (insectName, insectColor, currentHexID, targetHexID) {
	// Render the changes after an insect move.
	var targetHex = $(targetHexID);
	goog.dom.classes.remove(targetHex, 'available-move');
	this.updateHexIcon(targetHex, insectName, insectColor);

	//var currentHex = $(currentHexID);
	//this.updateHexIcon(currentHex);
};

Main.prototype.updateHexIcon = function (hex, insectName, insectColor) {
	// TODO: a version that clears the insect's old space 
	newImg = '/img/' + insectName + '_' + insectColor + '.png';
	goog.array.forEach($$('img', null, hex), function (imgEl) {
		imgEl.src = newImg;
	});
	goog.dom.classes.add(hex, "insect");
};
		
Main.prototype.hexMouseOver = function (event) {
	// The event target is an image; pull the parent element, be it span or li
	var hex = goog.dom.getAncestorByTagNameAndClass(event.target, 'SPAN');
	hex = hex || goog.dom.getAncestorByTagNameAndClass(event.target, 'LI');

	goog.dom.classes.add(hex, 'mouse-over');
}
Main.prototype.hexMouseOut = function (event) {
	// The event target is an image; pull the parent element, be it span or li
	var hex = goog.dom.getAncestorByTagNameAndClass(event.target, 'SPAN');
	hex = hex || goog.dom.getAncestorByTagNameAndClass(event.target, 'LI');

	goog.dom.classes.remove(hex, 'mouse-over');
}

var main = new Main();

// Listeners (must come after page load).
goog.array.forEach($$('li', null, $('white-pieces')), function (piece) {
	goog.events.listen(piece, goog.events.EventType.CLICK, main.pieceSelected, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
goog.array.forEach($$('li', null, $('black-pieces')), function (piece) {
	goog.events.listen(piece, goog.events.EventType.CLICK, main.pieceSelected, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
goog.array.forEach($$('span', 'hex'), function (hex) {
	goog.events.listen(hex, goog.events.EventType.CLICK, main.hexClicked, false, main);
	goog.events.listen(hex, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(hex, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
