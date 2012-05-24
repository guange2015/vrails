var net =require('net');
var child_process = require('child_process');
var rails_ps = null;

var server = net.createServer(function(socket){
  console.log('server connected.');
  socket.on('end', function(){
    console.log('server disconnected.')
  });
  var ls = null;
  
  socket.on('data',function(data){
    console.log(data.toString());
    var params = JSON.parse(data);
    ls = process(params, socket);
    if (ls) {
      ls.stdout.on('data', console_stdout);
      ls.stderr.on('data', console_stderr);
      ls.on('exit',console_exit);
    };
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

function process (params, socket) {
  var cmd = params.cmd
  if (cmd=='?') {socket.end(help()); return null;};
  if (cmd=='starts' || cmd=='stops' || cmd=='restarts') {return start_rails_cmd(params,socket)};
  return child_process.spawn(params.cmd,params.args,{cwd:params.cwd});
}

function start_rails_cmd (params,socket) {
    var ls = null;
    if (params.cmd=='starts') {
      if (rails_ps) {
        socket.end('rails server already started.\n');  
        return null;
      };
      args = params.args;
      args.unshift('server');
      ls = child_process.spawn('rails',args,{cwd:params.cwd});
      rails_ps = ls;
    } else if(params.cmd == 'stops'){
      if (rails_ps) {
        rails_ps.kill('SIGINT'); rails_ps=null;
        socket.end('rails server stoped.\n');  
      } else {
        socket.end('rails server not started.\n');  
      }
      ls = null;
    } else if(params.cmd == 'restarts'){
      socket.end('unsupport.\n');  
    }
    return ls;
  }

function help () {
  return 'starts - start the rails web server.\n' +
         'stops - stop the rails web server.\n' +
         'restarts - restart the rails web server.\n' ;
}
	
