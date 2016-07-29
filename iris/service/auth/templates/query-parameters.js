var extractQueryParameters = function() {
    /**
    *
    * Parses the query string and returns a dictionary of
    *   paramName -> [paramValue(s)]
    *
    * Source:
    *   http://stackoverflow.com/questions/901115/how-can-i-get-query-string-values-in-javascript/21152762#21152762
    * Modified to our needs
    *
    */
    var qd = {};
    window.location.search.substr(1).split("&").forEach(
        function(item) {
            var k = item.split("=")[0],
                v = decodeURIComponent(item.split("=")[1]);
            if (k in qd) {
                qd[k].push(v);
            } else {
                qd[k] = [v,];
            }
        }
    );
    return qd;
};
var getQueryParameter = function(param, fromParams) {
    /**
    *
    * Returns the value of 'param' in 'fromParams'.
    * 'fromParams' is expected to be of the form 'extractQueryParameters' returns.
    *
    * If the value-array length is 1, the actual value is returned.
    * The complete array containing all values for that parameter is returned otherwise.
    *
    */
    if (fromParams.hasOwnProperty(param)) {
        if (fromParams[param].length === 1) {
            return fromParams[param][0];
        } else {
            return fromParams[param];
        }
    }
    return null;
};
