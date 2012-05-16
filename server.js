// Define the module, and then spawn a new 'ls' statement
var child_process = require('child_process');
var url = require('url');
var querystring = require('querystring');

function exe_cmd (response, cmd) {
  console.log(cmd);
  var ls = child_process.exec(cmd, function(error,stdout,stderr) {
      response.writeHead(200, {'Content-Type': 'text/plain'});
      response.end(stdout);

      if (error !== null) {
        console.log('exec error: ' + error);
      }
  });
}

var http = require('http');
http.createServer(function (req, res) {
  var url_info = url.parse(req.url);
  if (url_info.pathname == '/exe_cmd') {
    var params = querystring.unescape(req.url)
    var index_string = 'exe_cmd?cmd=';
    var cmd = params.slice(params.indexOf(index_string)+index_string.length);
    exe_cmd(res, cmd);  
  } else {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World\n');
  }
  
}).listen(process.env.PORT || 8080, "0.0.0.0");

console.log("server started on 8080 port.")