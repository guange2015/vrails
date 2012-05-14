// Define the module, and then spawn a new 'ls' statement
var child_process = require('child_process');
var url = require('url');
var querystring = require('querystring');

function exe_cmd (response, cmd, args) {
  console.log(cmd);
  console.log(args);
  var ls = child_process.spawn(cmd, args.split(' '));
  var out_data = '';
  ls.stdout.on('data', function (data) {
    out_data += data;
  });
  ls.stdout.on('end', function(){
    console.log(out_data);
    response.writeHead(200, {'Content-Type': 'text/plain'});
    response.end(out_data);
    out_data = '';
  })
}

var http = require('http');
http.createServer(function (req, res) {
  url_info = url.parse(req.url);
  if (url_info.pathname == '/exe_cmd') {
    params = querystring.parse(req.url);
    console.log(params);
    exe_cmd(res, params['/exe_cmd?cmd'], params.args);  
  } else {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end('Hello World\n');
  }
  
}).listen(process.env.PORT || 8080, "0.0.0.0");