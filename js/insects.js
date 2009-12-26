// Convenience methods
var $ = goog.dom.$;
var $$ = goog.dom.$$;


var pieceSelected = function(event) {
	// The user selected a piece, ask the server where they can move
	//TODO: img instead of li is the target
	var item = goog.dom.getAncestorByTagNameAndClass(event.target, 'LI'); 
	var insectName = item.id.split('-')[0];
	var insectColor = item.id.split('-')[1];
	 
	var queryData = new goog.Uri(document.URL).getQueryData();
	queryData.add('insect_name', insectName);
	queryData.add('insect_color', insectColor);
	goog.net.XhrIo.send("show_moves?" + queryData.toString(), showMovesResponse);
};

var showMovesResponse = function(event) {
	// Highlight the hexes that the user can move to with the selected piece
	var response = event.target.getResponseJson();
	goog.array.forEach(response.hexes, function (hexID) {
		goog.dom.classes.add($(hexID), 'available-move');
	});
};

var hexClicked = function(event) {
	var hex = goog.dom.getAncestorByTagNameAndClass(event.target, 'SPAN'); 
	if (goog.dom.classes.has(hex, 'available-move')) {
		var queryData = goog.Uri.QueryData.createFromMap(new goog.structs.Map({
			insect_name: 'ant',
			insect_color: 'white',
			target_hex: '3-3'
		}));
		queryData.extend(new goog.Uri(document.URL).getQueryData());
		goog.net.XhrIo.send("/move", moveResponse, "POST", queryData.toString());
	}
}

var moveResponse = function (event) {
	// TODO: check success
	var response = event.target.getResponseJson();
	goog.array.forEach(response.reveal_hex_ids, function (hexID) {
		goog.dom.classes.remove($(hexID), 'hidden');
	});
};
		
// Listeners
goog.array.forEach($$('li', null, $('white-pieces')), function (piece) {
	goog.events.listen(piece, 'click', pieceSelected);
});
goog.array.forEach($$('span', 'hex'), function (hex) {
	goog.events.listen(hex, 'click', hexClicked);
});
