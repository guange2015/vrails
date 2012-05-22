var net =require('net');
var child_process = require('child_process');

var server = net.createServer(function(socket){
  console.log('server connected.');
  socket.on('end', function(){
    console.log('server disconnected.')
  });
  var ls ;
  socket.on('data',function(data){
    console.log(data.toString());
    var params = JSON.parse(data);
    ls = child_process.spawn(params.cmd,params.args,{cwd:params.cwd});
    ls.stdout.on('data', console_stdout);
    ls.stderr.on('data', console_stderr);
    ls.on('exit',console_exit);
  });

  function console_stdout(data) {
    console.log('stdout: ' + data);
    socket.write(data);
  };

  function console_stderr(data) {
    console.log('stderr: ' + data);
    socket.write(data);
  };

  function console_exit(code) {
    console.log('child process exited with code ' + code);
    if (code==0) {
      socket.end('execute successed.\n');  
    } else {
      socket.end('execute error code '+code+'\n');  
    }
    
  };
});

server.listen(8000);
	
