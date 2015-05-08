var fmt = d3.time.format("%Y-%m-%dT%H:%M:%S.%L");
WIDTH = 500;
function parse(ts){
    return fmt.parse(ts.substring(0, ts.length - 3));
}
var tree;
function Tree(data){
    function getCall(id){
        return data.calls[id-1];
    }
    function ancestors(call){
        result = [call];
        cur_call = call;
        while(cur_call.parent_id !== null){
            cur_call = getCall(cur_call.parent_id);
            result.push(cur_call);
        }
        return result;
    }
    var time = d3.scale.linear()
        .domain([0, data.total_seconds])
        .range([0, WIDTH]);
    var calls;
    function draw(){
        calls = d3.select("#fc").selectAll(".call")
            .data(data.calls);

        calls.enter().append("rect")
            .attr("data-retval", function(d){return d.retval;})
            .attr("x", function(d){return time(d.call_time)})
            .attr("width", function(d){return time(d.ret_time - d.call_time)})
            .attr("height", 30)
            .attr("y", function(d){return d.depth * 40});

        calls.attr("class", function(d){
                var cls = "call";
                if(d.hovered){
                    cls += " hovered";
                }
                return cls;
            });
        calls.on("mouseover", function(d){
            data.calls.forEach(function(call){
                call.hovered = false;    
            });
            var anc = ancestors(d);
            var info = d3.select("#info-panel").html("");
            for(var i=anc.length-1;i>=0;i--){
                var call = anc[i];
                call.hovered = true;
                info.append("p").text(call.name + "(" + "): " + call.retval);
            }
            draw();

        });
    }
    draw();
    return {
        calls: calls
    };
}
var onLoad = function(){
    //var tree;
    d3.json("/flame.json", function(error, json){
        if(error){console.error(error);}
        tree = Tree(json);
        //tree.forEach(function(node, depth){console.log(node, depth)});
        //tree.forEach(function(node, depth, parent_node){
            //if (parent_node){
                //container = parent_node.elt;
            //} else {
                //container = d3.select("#fc");
            //}
            //node.elt = container.append("svg:g")
            //node.elt.attr("width", node.width + "%");
            //node.elt.attr("transform", "matrix("+node.width/100+" 0 0 1 "+node.x_offset*container.node().getBBox().width/100 +", 40)");
            //node.elt.append("svg:rect").attr("width", "100%").attr("class", "call").attr("height", "39");
            
        //});
    });
}();
