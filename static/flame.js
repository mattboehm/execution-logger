var fmt = d3.time.format("%Y-%m-%dT%H:%M:%S.%L");
WIDTH = 500;
function parse(ts){
    return fmt.parse(ts.substring(0, ts.length - 3));
}

function onFunctionClick(call){
  flameChart.zoomToCall(call);
}

var dom = React.DOM;

//Simple summary view of a single function call
//props: call
var FunctionCall = React.createClass({
  displayName: "FunctionCall",
  onClick: function(){
    onFunctionClick(this.props.call);
  },
  render: function(){
    var filename_parts = this.props.call.file_name.split("/");
    var short_filename = ".../" + filename_parts[filename_parts.length - 1];
    return dom.div(
      {className: "func-call", onClick: this.onClick, key: this.props.call.id},
      dom.span(null, this.props.call.name),
      "(",
      dom.span({className: "args"}, this.props.call.args.replace(/^None$/, "")),
      "): ",
      dom.span({className: "retval"}, this.props.call.retval),
      dom.span({className: "filename", title: this.props.call.file_name}, short_filename)
    );
  },
});

//List of FunctionCalls
//props: calls
//contains: FunctionCall
var FunctionCallList = React.createClass({
  displayName: "FunctionCallList",
  render: function(){
    var rows = mori.map(
      function(call){
        return React.createElement(
          FunctionCall,
          {call: call}
        )
      },
      this.props.calls
    )
    return dom.div(
      {},
      mori.intoArray(rows)
    );
  },
});

//A textbox with a label that does something on change
//props: label, onChange
var TextFilter = React.createClass({
  displayName: "TextFilter",
  handleChange: function(){
    if (this.props.onChange){
      this.props.onChange(this.refs.inputBox.getDOMNode().value);
    }
  },
  render: function(){
      return dom.label(
        {},
        this.props.label,
        dom.input(
          {
            type: "text",
            onChange: this.handleChange,
            ref: "inputBox"
          }
        )
      );
  },
});

//A list of function calls with an input box that can be used to filter them
//props: calls
//contains: TextFilter, FunctionCallList
var FilterableFunctionCallList = React.createClass({
  displayName: "FilterableFunctionCallList",
  handleFileFilterChange: function(filterVal){
    var self = this;
    this.setState({
      fileFilterText: filterVal,
      filteredCalls: mori.filter(
        function(call){
          console.log("filter", call, filterVal, self.state.funcFilterText);
          return call.file_name.indexOf(filterVal) !== -1 && call.name.indexOf(self.state.funcFilterText) !== -1;
        },
        this.props.calls
      )
    });
  },
  handleFuncFilterChange: function(filterVal){
    var self = this;
    this.setState({
      funcFilterText: filterVal,
      filteredCalls: mori.filter(
        function(call){
          return call.file_name.indexOf(self.state.fileFilterText) !== -1 && call.name.indexOf(filterVal) !== -1;
        },
        this.props.calls
      )
    });
  },
  getInitialState: function(){
    return {
      fileFilterText: "",
      funcFilterText: "",
      filteredCalls: this.props.calls
    };
  },
  render: function(){
    return dom.div(
      {},
      React.createElement(TextFilter, {label: "File name", onChange: this.handleFileFilterChange}),
      React.createElement(TextFilter, {label: "Func Name", onChange: this.handleFuncFilterChange}),
      React.createElement(FunctionCallList, {calls: this.state.filteredCalls})
      );
  },
});

//A tree of function calls-- nested divs that can be expanded/collapsed
//props: executionTree
//contains: CallTreeNode
var CallTree = React.createClass({
  displayName: "CallTree",
  render: function(){
    var self=this;
    var roots = mori.map(
      function(root){
        return React.createElement(
          CallTreeNode,
          {executionTree: self.props.executionTree, call: root}
        );
      },
      this.props.executionTree.getRoots()
    );
    return dom.div(
      {},
      mori.intoArray(roots)
      );
  },
});
var CallTreeNode = React.createClass({
  //props: executionTree, call
  displayName: "CallTreeNode",
  getInitialState: function(){
    return {expanded: false};
  },
  toggleExpand: function(evt){
    evt.stopPropagation();
    this.setState(
      {expanded: !this.state.expanded}
    );
  },
  render: function(){
    var self=this;
    var call = mori.toJs(this.props.call);

    var children = self.props.executionTree.getChildren(call.id);
    var childNodes = mori.vector();
    if (self.state.expanded){
      childNodes = mori.map(
        function(child) {
          return React.createElement(
            CallTreeNode,
            {executionTree: self.props.executionTree, call: child}
          );
        },
        children
      );
    }

    var seconds_elapsed = (call.ret_time - call.call_time).toFixed(3);
    var duration = Math.round(seconds_elapsed/60) + ":" + (seconds_elapsed % 60)
    return dom.div(
      {className: "call-tree-node", title: call.name, onClick:self.toggleExpand, key:call.id},
      dom.span({className: "func-name"}, call.name),
      "(",
      dom.span({className: "func-args"}, call.args),
      "): ",
      mori.intoArray(childNodes),
      dom.span({className: "func-retval"}, call.retval),
      dom.span({className: "duration"}, duration)
    );
  },
});


//d3 visualization for flame chart
var flameChart;
function FlameChart(data, containerSelector){
    //maps a call's filename to the class that should be put on that call
    var filenameClasses = {};
    var funcnameClasses = {};
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
    function zoomToCall(call){
        time.domain([call.call_time, call.ret_time]);
        draw();
    }
    function draw(){
        time.range([0, $(containerSelector).width()]);
        calls = d3.select(containerSelector).selectAll(".call")
            .data(data.calls);

        calls.enter().append("rect")
            .attr("data-retval", function(d){return d.retval;})
            .attr("height", 30)
        calls.transition()
            .attr("x", function(d){return time(d.call_time)})
            .attr("width", function(d){result = time(d.ret_time) - time(d.call_time); return (result > 0)? result: 0;})
            .attr("y", function(d){return d.depth * 40});

        calls.attr("class", function(d){
                var cls = "call ";
                cls += filenameClasses[d.file_name] || "";
                cls += " ";
                cls += funcnameClasses[d.name] || "";
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
            var callStack = [];
            for(var i=anc.length-1;i>=0;i--){
                var call = anc[i];
                call.hovered = true;
                callStack.push(call);
            }
            React.render(
              React.createElement(FunctionCallList, {calls: callStack}),
              document.getElementById("info-panel")
            );
            draw();

        });
        calls.on("click", function(d){
            time.domain([d.call_time, d.ret_time]);
            draw();
        });
    }
    draw();
    return {
        filenameClasses: filenameClasses,
        funcnameClasses: funcnameClasses,
        calls: calls,
        zoomToCall: zoomToCall
    };
}
//calls: vector of calls. Each call is a hashmap.
function ExecutionTree(calls){
  var getParent = mori.curry(mori.get, "parent_id");
  var parentMap = mori.groupBy(getParent, calls);

  var getId = mori.curry(mori.get, "id");
  var idMap = mori.groupBy(getId, calls);

  function _getAncestors(ancestors){
    var nextParentId = mori.get(mori.first(ancestors), "parent_id");
    if (nextParentId === null){
      return ancestors;
    } else {
      return _getAncestors(mori.conj(ancestors, self.getCall(nextParentId)));
    }
  }
  var self = {
    getCall: function(id){
      return mori.get(idMap, id);
    },
    getParent: function(id){
      var parentId = mori.get(self.getCall(id), "parent_id");
      return self.getCall(parentId);
    },
    getChildren: function(id){
      return mori.get(parentMap, id);
    },
    getAncestors: function(id){
      var call = self.getCall(id);
      if (mori.get(call, "parent_id") === null){
        return mori.list();
      } else {
        return _getAncestors(mori.list(self.getParent(id)));
      }
    },
    getRoots: function(){
      return mori.get(parentMap, null);
    }
  }
  return self;
}
var onLoad = function(){
    $('.nav-tabs a').click(function (e) {
        e.preventDefault();
        $(this).tab('show');
    });
    d3.json("/flame.json", function(error, json){
        if(error){console.error(error);}
        flameChart = FlameChart(json, "#fc");
        var etree = ExecutionTree(mori.toClj(json.calls))
        React.render(
          React.createElement(FilterableFunctionCallList, {calls: json.calls}),
          document.getElementById("left-panel")
        );
        React.render(
          React.createElement(CallTree, {executionTree: etree}),
          document.getElementById("call-tree")
        );
    });
}();
