var sigInst, canvas, $GP

var config={};

function GetQueryStringParams(sParam,defaultVal) {
    var sPageURL = ""+window.location;//.search.substring(1);//This might be causing error in Safari?
    if (sPageURL.indexOf("?")==-1) return defaultVal;
    sPageURL=sPageURL.substr(sPageURL.indexOf("?")+1);    
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return sParameterName[1];
        }
    }
    return defaultVal;
}


jQuery.getJSON(GetQueryStringParams("config","config.json"), function(data, textStatus, jqXHR) {
	config=data;
	$(document).ready(setupGUI(config));
});


Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};


function resetScale() {
    sigInst.position(0,0,1).draw();
}


function initSigma(config) {
	var data=config.data
	
    var drawProps, graphProps, mouseProps;

    drawProps=config.sigma.drawingProperties;
    graphProps=config.sigma.graphProperties;
    mouseProps=config.sigma.mouseProperties;
    var a = sigma.init(document.getElementById("sigma-canvas")).drawingProperties(drawProps).graphProperties(graphProps).mouseProperties(mouseProps);
    sigInst = a;
    a.active = !1;
    a.neighbors = {};
    a.detail = !1;


    dataReady = function() {//This is called as soon as data is loaded
		a.clusters = {};

		a.iterNodes(
			function (b) { //This is where we populate the array used for the group select box

				// note: index may not be consistent for all nodes. Should calculate each time. 
				 // alert(JSON.stringify(b.attr.attributes[5].val));
				// alert(b.x);
				a.clusters[b.color] || (a.clusters[b.color] = []);
				a.clusters[b.color].push(b.id);//SAH: push id not label
			}
		
		);

		a.iterEdges(function (b) {
		    b.hidden = !$GP.show_edges();
		});
	
		a.bind("upnodes", function (a) {
		    nodeActive(a.content[0])
		});

		a.draw();
		configSigmaElements(config);
	}

    if (data.indexOf("gexf")>0 || data.indexOf("xml")>0)
        a.parseGexf(data,dataReady);
    else
	    a.parseJson(data,dataReady);
    gexf = sigmaInst = null;
}


function setupGUI(config) {
	$GP = {
		calculating: !1,
		showgroup: !1
	};
    $GP.intro = $("#intro");
    $GP.info = $("#attributepane");
    $GP.info_donnees = $GP.info.find(".nodeattributes");
    $GP.info_name = $GP.info.find(".name");
    $GP.info_preview = $GP.info.find(".preview");
    $GP.info_link = $GP.info.find(".link");
    $GP.info_data = $GP.info.find(".data");
    $GP.info_close = $GP.info.find(".returntext");
    $GP.info_p = $GP.info.find(".p");
    $GP.info_close.click(nodeNormal);
    $GP.search = new Search($("#search"));
    $GP.cluster = new Cluster($("#attributeselect"));
    $GP.show_illegal = function() {return document.getElementById("show_illegal").checked};
    $GP.show_edges = function() {return document.getElementById("show_edges").checked};
    config.GP=$GP;
    initSigma(config);
}


function configSigmaElements(config) {
	$GP=config.GP;
    let sorted_keys = Object.keys(sigInst.clusters).sort((x, y)=>sigInst.clusters[x].length - sigInst.clusters[y].length)

    var a = [],
        b,x=0;
    for (b of sorted_keys) {
        a.push('<div style="line-height:12px"><a href="#' + b + '"><div style="width:40px;height:12px;border:1px solid #1b1b1b; margin-right: 4px; vertical-align: bottom; ;background:' + b + ';display:inline-block"></div> Level ' + (x++) + ' (' + sigInst.clusters[b].length + ' videos)</a></div>');
    }

    $GP.cluster.content(a.join(""));
    b = {
        minWidth: 400,
        maxWidth: 800,
        maxHeight: 600
    };
    $("a.fb").fancybox(b);
    $("#zoom").find("div.z").each(function () {
        var a = $(this),
            b = a.attr("rel");
        a.click(function () {
			if (b == "center") {
				resetScale();
			} else {
		        var a = sigInst._core;
	            sigInst.zoomTo(a.domElements.nodes.width / 2, a.domElements.nodes.height / 2, a.mousecaptor.ratio * ("in" == b ? 1.5 : 0.5));		
			}

        })
    });

    $('#show_edges').bind('change', function() {
        let hide = !$GP.show_edges();
		sigInst.iterEdges(function (b) {
		    b.hidden = hide;
		});
		sigInst.draw(2, 2, 2, 2);
    });

    $(document).bind('keydown', function(a) {
        // esc button close info window
        if (a.which == 27) {
            $GP.info_close.trigger('click');
            $GP.search.clean();
        }
    });

    a = window.location.hash.substr(1);
    if (0 < a.length) {
        $GP.search.exactMatch = !0, $GP.search.search(a)
        $GP.search.clean();
    }
}


function Search(a) {
    this.input = a.find("input[name=search]");
    this.state = a.find(".state");
    this.results = a.find(".results");
    this.exactMatch = !1;
    this.lastSearch = "";
    this.searching = !1;
    var b = this;
    this.input.focus(function () {
        var a = $(this);
        a.data("focus") || (a.data("focus", !0), a.removeClass("empty"));
        b.clean()
    });
    this.input.keydown(function (a) {
        if (13 == a.which) return b.state.addClass("searching"), b.search(b.input.val()), !1
    });
    this.state.click(function () {
        var a = b.input.val();
        b.searching && a == b.lastSearch ? b.close() : (b.state.addClass("searching"), b.search(a))
    });
    this.dom = a;
    this.close = function () {
        this.state.removeClass("searching");
        this.results.hide();
        this.searching = !1;
        this.input.val("");//SAH -- let's erase string when we close
        nodeNormal()
    };
    this.clean = function () {
        this.results.empty().hide();
        this.state.removeClass("searching");
        this.input.val("");
    };
    this.search = function (a) {
        var b = !1,
            c = [],
            b = this.exactMatch ? ("^" + a + "$").toLowerCase() : a.toLowerCase(),
            g = RegExp(b);
        this.exactMatch = !1;
        this.searching = !0;
        this.lastSearch = a;
        this.results.empty();
        if (2 >= a.length) this.results.html("<i>You must search for a name with a minimum of 3 letters.</i>");
        else {
            sigInst.iterNodes(function (a) {
                if (g.test(a.label.toLowerCase()) || g.test(a.id)) {
                    c.push({id: a.id, name: a.label});
                }
            });
            c.length ? (b = !0, nodeActive(c[0].id)) : b = showCluster(a);
            a = ["<b>Search Results: </b>"];
            if (1 < c.length) for (var d = 0, h = c.length; d < h; d++) a.push('<a href="#' + c[d].id + '" onclick="nodeActive(\'' + c[d].id + "')\">" + c[d].name + "</a>");
            0 == c.length && !b && a.push("<i>No results found.</i>");
            1 < a.length && this.results.html(a.join(""));
           }
        if(c.length!=1) this.results.show();
        if(c.length==1) this.results.hide();   
    }
}


function Cluster(a) {
    this.cluster = a;
    this.display = !0;
    this.list = this.cluster.find(".list");
    this.list.empty();

    this.content = function (a) {
        this.list.html(a);
        this.list.find("a").click(function () {
            var a = $(this).attr("href").substr(1);
            showCluster(a)
        })
    };

    this.list.show();
}


function nodeNormal() {
    !0 != $GP.calculating && !1 != sigInst.detail && ($GP.calculating = !0, sigInst.detail = !0, $GP.info.delay(400).animate({width:'hide'},350), sigInst.iterEdges(function (a) {
        a.attr.color = !1;
        a.hidden = !$GP.show_edges()
    }), sigInst.iterNodes(function (a) {
        a.hidden = !1;
        a.attr.color = !1;
        a.attr.lineWidth = !1;
        a.attr.size = !1
    }), resetScale(), sigInst.draw(2, 2, 2, 2), sigInst.neighbors = {}, sigInst.active = !1, $GP.calculating = !1, window.location.hash = "")
}


function nodeActive(a) {
    sigInst.neighbors = {};
    sigInst.detail = !0;
    var b = sigInst._core.graph.nodesIndex[a];
	var outgoing={},incoming={},mutual={};//SAH
    sigInst.iterEdges(function (b) {
        b.attr.lineWidth = !1;
        b.hidden = !0;
        
        n={
            name: b.label,
            colour: b.color
        };
        
   	   if (a==b.source) outgoing[b.target]=n;		//SAH
	   else if (a==b.target) incoming[b.source]=n;		//SAH
       if (a == b.source || a == b.target) sigInst.neighbors[a == b.target ? b.source : b.target] = n;
       b.hidden = !$GP.show_edges(), b.attr.color = "rgba(0, 0, 0, 1)";
    });
    var f = [];
    sigInst.iterNodes(function (a) {
        a.hidden = !0;
        a.attr.lineWidth = !1;
        a.attr.color = a.color
    });

    //SAH - Compute intersection for mutual and remove these from incoming/outgoing
    for (e in outgoing) {
        //name=outgoing[e];
        if (e in incoming) {
            mutual[e]=outgoing[e];
            delete incoming[e];
            delete outgoing[e];
        }
    }
    
    var createList=function(c) {
        var f = [];
    	var e = [], g;
        for (g in c) {
            var d = sigInst._core.graph.nodesIndex[g];
            d.hidden = !1;
            d.attr.lineWidth = !1;
            d.attr.color = c[g].colour;
            a != g && e.push({
                id: g,
                name: d.label,
                group: (c[g].name)? c[g].name:"",
                colour: c[g].colour
            })
        }
        e.sort(function (a, b) {
            var c = a.group.toLowerCase(),
                d = b.group.toLowerCase(),
                e = a.name.toLowerCase(),
                f = b.name.toLowerCase();
            return c != d ? c < d ? -1 : c > d ? 1 : 0 : e < f ? -1 : e > f ? 1 : 0
        });
        d = "";
            for (g in e) {
                c = e[g];
                f.push('<li class="membership"><a href="#' + c.id + '" onmouseover="sigInst._core.plotter.drawHoverNode(sigInst._core.graph.nodesIndex[\'' + c.id + '\'])\" onclick=\"nodeActive(\'' + c.id + '\')" onmouseout="sigInst.refresh()">' + c.name + "</a></li>");
            }
            return f;
	}

	var f=[];

    size=Object.size(mutual);
    f.push("<h2>Mututal (" + size + ")</h2>");
    (size>0)? f=f.concat(createList(mutual)) : f.push("No mutual links<br>");
    size=Object.size(incoming);
    f.push("<h2>Incoming (" + size + ")</h2>");
    (size>0)? f=f.concat(createList(incoming)) : f.push("No incoming links<br>");
    size=Object.size(outgoing);
    f.push("<h2>Outgoing (" + size + ")</h2>");
    (size>0)? f=f.concat(createList(outgoing)) : f.push("No outgoing links<br>");

    b.hidden = !1;
    b.attr.color = b.color;
    b.attr.lineWidth = 6;
    b.attr.strokeStyle = "#000000";
    sigInst.draw(2, 2, 2, 2);

    $GP.info_link.find("ul").html(f.join(""));
    $GP.info_link.find("li").each(function () {
        var a = $(this),
            b = a.attr("rel");
    });
    f = b.attr;
    if (f.attributes) {
        var img_src = '/images/preview_not_found.png';
        if (f.attributes['img_src']) {
            img_src = f.attributes['img_src'];
        }
        $GP.info_preview.html('<a href="https://www.pornhub.com/view_video.php?viewkey=' + f.attributes['hash'] + '" target="_blank"><img src="' + img_src + '"></img></a>');

        e = [];
        var h = '<span><a href="https://www.pornhub.com/view_video.php?viewkey=' + f.attributes['hash'] + '" target="_blank">see on pornhub</a></span><br/>';
        e.push(h);

        for (var attr in f.attributes) {
            if (config.custom.nodeAttributeFilter.indexOf(attr) > -1) {
                var h = '<span><strong>' + attr + ':</strong> ' + f.attributes[attr] + '</span><br/>';
                e.push(h);
            }
        }

        $GP.info_name.html("<div><span onmouseover=\"sigInst._core.plotter.drawHoverNode(sigInst._core.graph.nodesIndex['" + b.id + '\'])" onmouseout="sigInst.refresh()">' + b.label + "</span></div>");

        $GP.info_data.html(e.join("<br/>"))
    }

    if ($GP.show_illegal()) {
        $GP.info_preview.show();
    } else {
        $GP.info_preview.hide();
    }

    $GP.info_data.show();
    $GP.info_p.html("Connections:");
    $GP.info.animate({width:'show'},350);
	$GP.info_donnees.hide();
	$GP.info_donnees.show();
    sigInst.active = a;
    window.location.hash = b.id;
}


function showCluster(a) {
    var b = sigInst.clusters[a];
    if (b && 0 < b.length) {
        sigInst.detail = !0;
        b.sort();
        sigInst.iterEdges(function (a) {
            a.hidden = !$GP.show_edges();
            a.attr.lineWidth = !1;
            a.attr.color = !1
        });
        sigInst.iterNodes(function (a) {
            a.hidden = !0
        });
        for (var f = [], e = [], c = 0, g = b.length; c < g; c++) {
            var d = sigInst._core.graph.nodesIndex[b[c]];
            !0 == d.hidden && (e.push(b[c]), d.hidden = !1, d.attr.lineWidth = !1, d.attr.color = d.color, f.push('<li class="membership"><a href="#'+d.label+'" onmouseover="sigInst._core.plotter.drawHoverNode(sigInst._core.graph.nodesIndex[\'' + d.id + "'])\" onclick=\"nodeActive('" + d.id + '\')" onmouseout="sigInst.refresh()">' + d.label + "</a></li>"))
        }
        sigInst.clusters[a] = e;
        sigInst.draw(2, 2, 2, 2);
        $GP.info_name.html("<b>" + a + "</b>");
        $GP.info_data.hide();
        $GP.info_preview.hide();
        $GP.info_p.html("Group Members:");
        $GP.info_link.find("ul").html(f.join(""));
        $GP.info.animate({width:'show'},350);
        $GP.search.clean();
        return !0
    }
    return !1
}
