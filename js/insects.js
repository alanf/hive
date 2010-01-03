// Convenience methods
var $ = goog.dom.$;
var $$ = goog.dom.$$;

var xhrSend = function (url, callback, context, method, queryDataString) {
	// Convenience method for responding to an xhr with a listener method and some context.
	xhr = new goog.net.XhrIo();
	goog.events.listen(xhr, goog.net.EventType.COMPLETE, callback, false, context);
	xhr.send(url, method, queryDataString);
}
	
// Functionality for updating the game
var Main = function () {
	// Encompasses the between-moves game state (we call the server on each user action)
	// Updates the display after each move.
	// TODO: we need to poll for the other player's actions
	this.selectedInsectName = null;
	this.selectedInsectColor = null;
	this.targetHexID = null;
	this.currentHexID = null;
	// The player highlighted this
};

Main.prototype.newInsectSelected = function(event) {
	// The user selected an insect not yet in play
	//TODO: img instead of li is the target
	var item = goog.dom.getAncestorByTagNameAndClass(event.target, 'LI'); 
	this.selectedInsectName = item.id.split('-')[0];
	this.selectedInsectColor = item.id.split('-')[1];
	 
	var queryData = new goog.Uri(document.URL).getQueryData();
	queryData.add('insect_name', this.selectedInsectName);
	queryData.add('insect_color', this.selectedInsectColor);
	queryData.extend(new goog.Uri(document.URL).getQueryData());
	xhrSend("show_available_placements?" + queryData.toString(), this.newInsectSelectedResponse, this);
};

Main.prototype.newInsectSelectedResponse = function(event) {
	// Highlight the hexes that the user can place a new insect on
	var response = event.target.getResponseJson();
	goog.array.forEach(response.hexes, function (hexID) {
		goog.dom.classes.add($(hexID), 'available-move');
	});
};

Main.prototype.hexClicked = function (event) {
	// This function's behavior depends on what is currently selected.
	// * if no insect or hex is selected, then the user wants to move an insect in play and we select it and call the "show moves" action.
	// * if a hex is already selected, the user wants to move an insect from one space to another and call the "move" action..
	// * if an insect is already selected, the user wants to play a new piece on the board. call the "move" action.
	var hex = goog.dom.getAncestorByTagNameAndClass(event.target, 'SPAN'); 

	// Show the possible moves of a selected insect already in play.
	if (this.currentHexID == null && goog.dom.classes.has(hex, 'insect')) {
		this.currentHexID = hex.id;	

		var queryData = new goog.Uri(document.URL).getQueryData();
		queryData.add('current_hex', this.currentHexID);
		queryData.extend(new goog.Uri(document.URL).getQueryData());
		xhrSend("show_moves?" + queryData.toString(), this.newInsectSelectedResponse, this);
	}
	// Try to move an insect from the previously selected hex to the clicked hex. 
	else if (this.currentHexID && goog.dom.classes.has(hex, 'available-move')) {
		var queryData = goog.Uri.QueryData.createFromMap(new goog.structs.Map({
			target_hex: hex.id,
			current_hex: this.currentHexID
		}));
		queryData.extend(new goog.Uri(document.URL).getQueryData());
		this.targetHexID = hex.id;
		xhrSend("/move", this.moveResponse, this, "POST", queryData.toString());
	}
	// Put a new insect into play, and describe what it is.
	else if (goog.dom.classes.has(hex, 'available-move')) {
		queryData = goog.Uri.QueryData.createFromMap(new goog.structs.Map({
			insect_name: this.selectedInsectName,
			insect_color: this.selectedInsectColor,
			target_hex: hex.id
		}));
		queryData.extend(new goog.Uri(document.URL).getQueryData());
		this.targetHexID = hex.id;
		xhrSend("/placement", this.moveResponse, this, "POST", queryData.toString());
	}	
};

Main.prototype.clearAvailableMoves = function() {
	goog.array.forEach($$('span', 'available-move'), function (hex) {
		goog.dom.classes.remove(hex, 'available-move');
	});
};

Main.prototype.moveResponse = function (event) {
	// Administrative work to update the board after moving an insect
	// TODO: check success
	var response = event.target.getResponseJson();
	if (response.insect_name) {
		this.selectedInsectName = response.insect_name;
	}
	if (response.insect_color) {
		this.selectedInsectColor = response.insect_color;
	}
	this.updateBoard(this.selectedInsectName, this.selectedInsectColor, this.currentHexID, this.targetHexID);
};

Main.prototype.updateBoard = function (insectName, insectColor, currentHexID, targetHexID) {
	// Render the changes after an insect move.
	if (currentHexID) {
		var currentHex = $(currentHexID);
		this.resetHexIcon(currentHex);
		this.currentHexID = null;
	}
	var targetHex = $(targetHexID);
	this.updateHexIcon(targetHex, insectName, insectColor);
	this.clearAvailableMoves();
};

Main.prototype.resetHexIcon = function (hex) {
	newImg = '/img/hexagon.png';
	goog.array.forEach($$('img', null, hex), function (imgEl) {
		imgEl.src = newImg;
	});
	goog.dom.classes.remove(hex, "insect");
}

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
	goog.events.listen(piece, goog.events.EventType.CLICK, main.newInsectSelected, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
goog.array.forEach($$('li', null, $('black-pieces')), function (piece) {
	goog.events.listen(piece, goog.events.EventType.CLICK, main.newInsectSelected, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(piece, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
goog.array.forEach($$('span', 'hex'), function (hex) {
	goog.events.listen(hex, goog.events.EventType.CLICK, main.hexClicked, false, main);
	goog.events.listen(hex, goog.events.EventType.MOUSEOVER, main.hexMouseOver, false, main);
	goog.events.listen(hex, goog.events.EventType.MOUSEOUT, main.hexMouseOut, false, main);
});
