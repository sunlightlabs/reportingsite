( function () {
var tableId = 1140208;
var hashData;

var quarters = ['2006q1', '2006q2', '2006q3', '2006q4', '2007q1', '2007q2', '2007q3', '2007q4',
                '2008q1', '2008q2', '2008q3', '2008q4', '2009q1', '2009q2', '2009q3', '2009q4',
                '2010q1', '2010q2', '2010q3', '2010q4', '2011q1'];

var quarter = quarters[0];

var mapColors = ['#F1EEF6', '#D4B9DA', '#C994C7', '#DF65B0', '#DD1C77', '#980043' ]

var highlightColor = 'FFFF10'

var getFillColor = function (val) {
    if (val < 24.8) {
        return mapColors[0];
    }
    if (val < 67.6) {
        return mapColors[1];
    }
    if (val < 136.3) {
        return mapColors[2];
    }
    if (val < 243.8) {
        return mapColors[3];
    }
    if (val < 467.4) {
        return mapColors[4];
    }
    return mapColors[5];
};

Overlay.prototype = new google.maps.OverlayView();
Overlay.prototype.onAdd = function() { }
Overlay.prototype.onRemove = function() { }
Overlay.prototype.draw = function() { }
function Overlay(options) { this.setValues(options); }


var InfoBox = function () {
    this.content = '';
    this.setContent = function (content) {
        this.content = content;
    }
    this.open = function () {
        $("#countyInfo").html(this.content);
    }
    this.close = function () {
        this.content = '';
        this.open();
    }
}


var highlightedFips;
var table;
var fipsRowIndexes = {};


var drawTable = function (rows) {
    var fips;
    var rowToHighlight;

    var cssClassNames = {
        'selectedTableRow': 'highlight',
        'oddTableRow': 'odd',
        'tableRow': 'even',
        'headerRow': 'headerRow'
    };
    var options = {'showRowNumber': false, 'cssClassNames': cssClassNames};

    var data = new google.visualization.DataTable();
    data.addColumn('string', 'County');
    data.addColumn('string', 'State');
    data.addColumn('number', 'SARs per capita');
    data.addColumn('number', 'FIPS');
    data.addRows(rows.length);
    rows.sort(function (a, b) {
            return b[1] - a[1];
    });
    for (i=0, il=rows.length; i<il; i++) {
        data.setCell(i, 0, fipsData[rows[i][0]]['county']);
        data.setCell(i, 1, fipsData[rows[i][0]]['state']);
        data.setCell(i, 2, rows[i][1]);
        data.setCell(i, 3, rows[i][0]);
        fipsRowIndexes[rows[i][0]] = i;
    }

    var view = new google.visualization.DataView(data, options);
    view.setColumns([0, 1, 2]);
    //view.setOptions({'cssClassNames': cssClassNames});
    table = new google.visualization.Table(document.getElementById('table_div'));
    table.draw(view, options);

    google.visualization.events.addListener(table, 'select', function() {
        var row = table.getSelection()[0].row;
        fips = data.getValue(row, 3);
        highlightedFips = fips;
        populateInfoBox(fips);
        clearStrokes(fips);
        overlays[fips].setOptions({strokeWeight: 2,
                                   strokeOpacity: 1,
                                   strokeColor: highlightColor});
        changeHash();
    });
    if (highlightedFips != undefined) {
        highlightTableRow(highlightedFips);
    }
}

var clearStrokes = function (toExclude) {
    for (i in overlays) {
        if (i == toExclude) {
            continue;
        }
        overlays[i].setOptions({strokeWeight: 0,
                                strokeOpacity: 0,
                                strokeColor: null});
    }
}

var highlightTableRow = function (fips) {
    highlightedFips = fips;
    table.setSelection([{row: fipsRowIndexes[highlightedFips]}]);
};


var populateInfoBox = function (fips) {
    if (fipsData[fips].hasOwnProperty('timeline')) {
        var url = chartUrl(fips, fipsData[fips]['timeline'], 225, 130)
        content = makeInfoboxContent(fips, url);
        infobox.setContent(content);
        infobox.open(map);
    } 
    else {
        var url = fipsUrl(fips);
        $.ajax({dataType: 'jsonp',
                url: fipsUrl(fips),
                jsonp: 'jsonCallback',
                data: {},
                success: function (data) {
                    fipsData[fips]['timeline'] = data['table']['rows'][0];
                    var url = chartUrl(fips, fipsData[fips]['timeline'], 225, 130)
                    content = makeInfoboxContent(fips, url);
                    infobox.setContent(content);
                    infobox.open(map);
                }

            });
    }
};





var qUrl = function (quarter) {
    var url = encodeURI("http://www.google.com/fusiontables/api/query/?sql=SELECT 'FIPS', '" + quarter + "' FROM " + tableId);
    return url;
}

var fipsData = {}

var fipsUrl = function (fips) {
    var url = "http://www.google.com/fusiontables/api/query/?sql=SELECT ";
    var qLen = quarters.length
    for (i=0; i<qLen; i++) {
        url += "'" + quarters[i] + "'";
        if (i !== qLen-1) {
            url += ',';
        }
    }
    url += " FROM " + tableId + " WHERE 'FIPS' = '" + fips + "'";
    return encodeURI(url);
};

var geometryUrl = encodeURI("http://www.google.com/fusiontables/api/query/?sql=SELECT 'FIPS', 'County', 'State', 'geometry' FROM " + tableId);

var chartUrl = function (fips, timeline, width, height) {
    if (!fipsData[fips].hasOwnProperty('chartUrl')) {
        var max = 1085.8;
        var url = encodeURI("https://chart.googleapis.com/chart?chxt=x,y&chxl=0:|2006|2011&cht=lc&chs=" + width + "x" + height + "&chd=t:" + timeline.join(',') + '&chxr=1,0,' + max + '&chds=0,' + max);
        url += '&chco=2A5F63'; // line color
        url += '&chf=c,s,EFEFEF|bg,s,EFEFEF'; // background color
        url += '&chem=y;s=cm_size;ds=0;d=disk,4,4,4,4,' + highlightColor + ',000000;dp=' + quarters.indexOf(quarter); // dot for current quarter
        return url;
        fipsData[fips]['chartUrl'] = url;
    }
    return fipsData[fips]['chartUrl'];
};

var makePopupContent = function (fips, chartUrl) {
    var data = fipsData[fips];
    var content = '<div class="popup"><h1>' + data['county'] + ', ' + data['state'] + '</h1>';
    content += '<img src="' + chartUrl + '"/>';
    content += '</div>';
    return content;
};

var currentFips;
var currentChartUrl;

var makeInfoboxContent = function (fips, chartUrl) {
    currentFips = fips;

    var qtrIndex = quarters.indexOf(quarter);
    chartUrl = chartUrl.replace(/dp=\d+/, 'dp=' + qtrIndex);
    currentChartUrl = chartUrl;

    var data = fipsData[fips];
    //var th = '<thead><tr><th>Yr.</th><th>Qtr.</th><th>Value</th></tr></thead>';
    var th = '<thead><tr><th>Year</th><th>Quarter</th><th>SARs per capita</th></tr></thead>';
    var content = '<h1>' + data['county'] + ', ' + data['state'] + '</h1>';
    content += '<img style="height:130px;width:225px;" src="' + chartUrl + '"/>';
    //content += '<table style="float: left; margin-right: 15px;">' + th + '<tbody>';
    content += '<table>' + th + '<tbody>';

    var klass = 'even';
    var year;
    var q;

    for (i=quarters.length-1; i >= 0; i--) {
        if (i % 2 === 0) {
            klass = 'even';
        } else {
            klass = 'odd';
        }
        q = quarters[i];
        if (q === quarter) {
            klass += ' highlight';
        }
        year = q.split('q')[0];
        q = q.split('q')[1];
        content += '<tr id="' + quarters[i] + '" class="qtr ' + klass + '"><td>' + year + '</td><td>' + q + '</td><td>' + data['timeline'][i] + '</tr>';
        /*
        if (quarters[i] === '2008q4') {
            content += '</tbody></table><table>' + th + '<tbody>';
        }
        */
    }
    content += '</tbody></table>';
    content += '</div>';
    return content;
}


var mapStyle = [
      {
        featureType: "all",
        elementType: "all",
        stylers: [
            { hue: "#ffa200" }
        ]
      },
      {
        featureType: "all",
        elementType: "labels",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "poi",
        elementType: "all",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "road",
        elementType: "all",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "transit",
        elementType: "all",
        stylers: [
          { visibility: "off" }
        ]
      },{
        featureType: "administrative",
        elementType: "geometry",
        stylers: [
          { visibility: "on" },
          { lightness: 41 }
        ]
      }
    ];

var mapType = new google.maps.StyledMapType(mapStyle, {name: 'mapStyle'});

var options = {
    zoom: 4,
    center: new google.maps.LatLng(38.9, -97.2),
    mapTypeControl: false,
    panControl: false,
    streetViewControl: false,
    zoomControlOptions: {
        style: google.maps.ZoomControlStyle.SMALL
    },
    mapTypeId: google.maps.MapTypeId.ROADMAP
}
var map = new google.maps.Map(document.getElementById("map_canvas"), options);
var OverLayMap = new Overlay( { map: map } );
map.mapTypes.set('mapStyle', mapType);
map.setMapTypeId('mapStyle');
var infobox = new InfoBox();
var overlays = {};
var qData = {};

var createMap = function () {
    $.ajax({dataType: 'jsonp',
            url: geometryUrl,
            jsonp: 'jsonCallback',
            data: {},
            success: function (data) {
                table = data['table'];
                rows = table['rows'];
                hashData = parseHash();

                for (i=0, il=rows.length; i<il; i++) {
                    row = rows[i];

                    fips = row[0];
                    county = row[1];
                    state = row[2];
                    geometry = row[3];
                    var coords = [];

                    fipsData[fips] = {county: county,
                                      state: state}

                    if (geometry['coordinates'] != undefined) {
                        for (j=0, jl=geometry['coordinates'].length; j<jl; j++) {
                            for (p=0, pl=geometry['coordinates'][j].length; p<pl; p++) {
                                var point = geometry['coordinates'][j][p];
                                coords.push(new google.maps.LatLng(point[1], point[0]));
                            }
                        }
                    }

                    var countyMap = new google.maps.Polygon({
                        paths: coords,
                        strokeColor: "#FF0000",
                        strokeOpacity: 0,
                        strokeWeight: 0,
                        fillColor: "#FFFFFF",
                        fillOpacity: 0
                    });

                    overlays[fips] = countyMap;
                    countyMap.setMap(map);
                }

                if (hashData != undefined) {
                    if (hashData['quarter'] != undefined && hashData['year'] != undefined) {
                        quarter = hashData['year'] + 'q' + hashData['quarter'];
                    }
                    if (hashData['fips'] != undefined) {
                        highlightedFips = hashData['fips'];
                        populateInfoBox(hashData['fips']);
                    }
                    if (hashData['zoom'] != undefined) {
                        map.setZoom(parseInt(hashData['zoom']));
                    }
                    if (hashData['lat'] != undefined && hashData['lng'] != undefined) {
                        map.setCenter(new google.maps.LatLng(parseFloat(hashData['lat']), parseFloat(hashData['lng'])));
                    }
                }
                updateMap(quarter);
            }

        });

        var dragEndListener = google.maps.event.addListener(map, 'dragend', function (event) {
                changeHash();
            });

        var zoomListener = google.maps.event.addListener(map, 'zoom_changed', function (event) {
                changeHash();
            });


}

var showMap = function (rows) {
    var row;
    var county;
    var state;
    var fips;
    var geometry;
    var countyMap;

    for (i in overlays) {
        overlays[i].setMap(null);
        google.maps.event.clearListeners(overlays[i], 'click');
    }

    for (i=0, il=rows.length; i<il; i++) {
        row = rows[i];

        fips = row[0];
        val = row[1]

        countyMap = overlays[fips];
        if (highlightedFips == fips) {
            countyMap.setOptions({fillOpacity: 1,
                                  strokeWeight: 2,
                                  strokeOpacity: 1,
                                  strokeColor: highlightColor,
                                  fillColor: getFillColor(val)
                                });
        }
        else {
            countyMap.setOptions({fillOpacity: 1,
                                  strokeWeight: 0,
                                  strokeOpacity: 0,
                                  fillColor: getFillColor(val)
                                });
        }

        var listenerAction = (function (fips, map, countyMap) {
            return function (event) {
                var content = ''
                populateInfoBox(fips);
                highlightTableRow(fips);
                countyMap.setOptions({strokeWeight: 2,
                                      strokeOpacity: 1,
                                      strokeColor: highlightColor});
                clearStrokes(fips);
                changeHash();
            }
        })(fips, map, countyMap);

        var mouseoverListenerAction = (function (fips, overlay) {
            return function (event) {
                var data = fipsData[fips];
                var projection = overlay.getProjection();
                var pos = projection.fromLatLngToContainerPixel(event.latLng);
                $("#tooltip").html(data['county'] + ', ' + data['state']);
                $("#tooltip").css({'top': pos.y + 275 + 'px', //pos.y + 'px',
                                   'left': pos.x + 25 + 'px'}); //pos.x + 'px'});
                $("#tooltip").show();
            }
        })(fips, OverLayMap);


        countyMap.setMap(map);

        var clickListener = google.maps.event.addListener(countyMap, 'click', listenerAction);
        var mouseoverListener = google.maps.event.addListener(countyMap, 'mouseover', mouseoverListenerAction);
        var mouseoutListener = google.maps.event.addListener(countyMap, 'mouseout', function (event) {
                $("#tooltip").hide();
            });

    }

}

var updateMap = function (quarter) {
    var table;
    var rows;

    $("#currQuarter").html(formatQuarter(quarter));

    if (qData.hasOwnProperty(quarter)) {
        showMap(qData[quarter]);
        drawTable(qData[quarter]);
    } 
    else {
        $.ajax({dataType: 'jsonp',
                url: qUrl(quarter),
                jsonp: 'jsonCallback',
                data: {},
                success: function (data) {
                    qData[quarter] = data['table']['rows'];
                    showMap(qData[quarter])
                    drawTable(qData[quarter]);
                }
            })
    }

};

var formatQuarter = function (q) {
    var pieces = q.split('q');
    var year = pieces[0];
    var qtr = pieces[1];
    var fullQtr;
    switch (qtr) {
        case '1':
            fullQtr = 'First';
            break;
        case '2':
            fullQtr = 'Second';
            break;
        case '3':
            fullQtr = 'Third';
            break;
        case '4':
            fullQtr = 'Fourth';
            break;
    }
    return year + ', ' + fullQtr + ' Quarter';
}


var content;

$("#nextQ").bind('click', function () {
    var currIndex = quarters.indexOf(quarter);
    var nextIndex = currIndex + 1;
    if (nextIndex < quarters.length) {
        quarter = quarters[nextIndex];
        updateMap(quarter);
        if (currentFips !== undefined) {
            content = makeInfoboxContent(currentFips, currentChartUrl);
            infobox.setContent(content);
            infobox.open(map);
        }
    }
    changeHash();
});

$("#prevQ").bind('click', function () {
    var currIndex = quarters.indexOf(quarter);
    var prevIndex = currIndex - 1;
    if (prevIndex >= 0) {
        quarter = quarters[prevIndex];
        updateMap(quarter);
        if (currentFips !== undefined) {
            content = makeInfoboxContent(currentFips, currentChartUrl);
            infobox.setContent(content);
            infobox.open(map);
        }
    }
    changeHash();
});

$(".qtr").live('click', function () {
    quarter = $(this).attr('id');
    updateMap(quarter);
    if (currentFips !== undefined) {
        content = makeInfoboxContent(currentFips, currentChartUrl);
        infobox.setContent(content);
        infobox.open(map);
    }
    changeHash();
});

$(".qtr").live('mouseover mouseout', function (e) {
    if (e.type == 'mouseover') {
        $(this).addClass('hover');
    } else {
        $(this).removeClass('hover');
    }
});

var parseHash = function () {
    var s;
    var loc = window.parent.location.href;
    var pieces = loc.split('#');
    if (pieces.length == 1) {
        return;
    }
    var hash = pieces[1];
    var parts = hash.split('&');
    data = {};
    for (i=0, il=parts.length; i<parts.length; i++) {
        s = parts[i].split('=');
        if (s.length != 2) {
            continue;
        }
        switch (s[0]) {
            case 'q':
                data['quarter'] = s[1];
                break;
            case 'y':
                data['year'] = s[1];
                break;
            case 'f':
                data['fips'] = s[1];
                break;
            case 'z':
                data['zoom'] = s[1];
                break;
            case 'lat':
                data['lat'] = s[1];
                break;
            case 'lng':
                data['lng'] = s[1];
                break;
        }
    }
    return data;
};


var changeHash = function () {
    var base, 
        qPieces, 
        hash, 
        center = map.getCenter(),
        lat, 
        lng;
    lat = center.lat();
    lng = center.lng();

    base = window.parent.location.href.split('#')[0];
    qPieces = quarter.split('q');
    hash = 'q=' + qPieces[1] + '&y=' + qPieces[0] + '&z=' + map.getZoom() + '&lat=' + lat + '&lng=' + lng;
    if (highlightedFips != undefined) {
        hash += '&f=' + highlightedFips;
    }
    window.parent.location = base + '#' + hash;
}


$(document).ready(function () {
    createMap();
});


})();
