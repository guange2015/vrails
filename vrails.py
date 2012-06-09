#coding=utf-8
import sublime, sublime_plugin
import urllib  
import urllib2  
import threading  
import functools
import os
import socket
import json 

# don't configure this, use menu -> Tools->vrails->settings
REMOTE_SERVER = "localhost:8080"
REMOTE_PROJECT_ROOT ='./'
TEST_COMMAND = 'rspec spec --drb'

class SocketRemoteRunApiCall(threading.Thread):  
    def __init__(self,finish_callback, cmd, timeout):    
      super(SocketRemoteRunApiCall,self).__init__()
      self.timeout = timeout  
      self.result = None  
      self.finish_callback = finish_callback
      self.cmd = cmd

    def output_log(self,log):
      sublime.set_timeout(functools.partial(self.finish_callback, log), 1) 

    def run(self):
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      host = REMOTE_SERVER.split(':')[0]
      port = int(REMOTE_SERVER.split(':')[1])

      try:
        s.connect((host, port))
        params = {'cwd':'/mnt/hgfs/projects/Demo',\
                  'cmd':'bundle',\
                  'args':'install -V'}
        send_data = json.dumps(self.cmd)
        s.sendall(send_data)
        data = s.recv(1024)
        while data:
          self.output_log(data)
          data = s.recv(1024)
      except Exception, e:
        self.output_log(str(e))
      finally:
        s.close()

class RemoteRunApiCall(threading.Thread):  
    def __init__(self,finish_callback, cmd, timeout):    
      super(RemoteRunApiCall,self).__init__()
      self.timeout = timeout  
      self.result = None  
      self.finish_callback = finish_callback
      self.cmd = cmd

    def output_log(self,log):
      sublime.set_timeout(functools.partial(self.finish_callback, "finished!!!\n"+log+"\n"), 1) 

    def run(self):
      data = self.cmd
      req_url = REMOTE_SERVER +'exe_cmd?'+data
       
      try:  
          request = urllib2.Request(req_url, \
                      headers={"User-Agent": "Sublime Prefixr"})  
          
          http_file = urllib2.urlopen(request, timeout=self.timeout)  
          self.result = http_file.read()  
          self.output_log(self.result)
          return
      except (urllib2.HTTPError) as (e):  
          self.result = '%s: HTTP error %s contacting API' % (__name__, str(e.code))  
      except (urllib2.URLError) as (e):  
          self.result = '%s: URL error %s contacting API' % (__name__, str(e.reason)) 

      log = self.result + "\n" + req_url
      self.output_log(log)

class BaseRemoteRunCommand(sublime_plugin.TextCommand):
  thread = None
  def run(self,edit,cmd=None):
    _settings = sublime.load_settings("vrails.sublime-settings")
    global REMOTE_SERVER; REMOTE_SERVER = _settings.get("remote_server")
    global REMOTE_PROJECT_ROOT; REMOTE_PROJECT_ROOT = _settings.get("remote_project_root")
    global TEST_COMMAND; TEST_COMMAND = _settings.get("test_command")
    self.args = cmd
    self.output_view = None
    self.show_tests_panel()
    self.run_command()
    

  def run_command(self):
    pass

  def show_tests_panel(self):
    if self.output_view is None:
      self.output_view = sublime.active_window().get_output_panel("tests")
    self.clear_test_view()
    sublime.active_window().run_command("show_panel", {"panel": "output.tests"})

  def clear_test_view(self):
    self.output_view.set_read_only(False)
    edit = self.output_view.begin_edit()
    self.output_view.erase(edit, sublime.Region(0, self.output_view.size()))
    self.output_view.end_edit(edit)
    self.output_view.set_read_only(True)

  def append_data(self, data):
    str = data.decode("utf-8")
    str = str.replace('\r\n', '\n').replace('\r', '\n')

    selection_was_at_end = (len(self.output_view.sel()) == 1
      and self.output_view.sel()[0]
        == sublime.Region(self.output_view.size()))
    self.output_view.set_read_only(False)
    edit = self.output_view.begin_edit()
    self.output_view.insert(edit, self.output_view.size(), str)
    if selection_was_at_end:
      self.output_view.show(self.output_view.size())
    self.output_view.end_edit(edit)
    self.output_view.set_read_only(True)

class RunRemoteTestCommand(BaseRemoteRunCommand):
  def getRemoteThread(self):
    text = TEST_COMMAND.strip()
    l = text.split(' ')
    cmd = l.pop(0)
    params = {'cwd':REMOTE_PROJECT_ROOT,\
                'cmd':cmd,\
                'args':l}
    return SocketRemoteRunApiCall(self.append_data, params, 60)

  def run_command(self):
    self.thread = self.getRemoteThread()
    self.thread.start()

class RunRemoteTestAtLineCommand(BaseRemoteRunCommand):
  def getRemoteThread(self):
    current_file = self.get_current_file_path()
    cmd = 'rspec'
    args = 'spec'
    if current_file:
      args = '%s --line %d' % (current_file, self.get_line_no())
    args = ('%s --drb' % args).split(' ')

    params = {'cwd':REMOTE_PROJECT_ROOT,\
                'cmd':cmd,\
                'args':args}
    print params
    return SocketRemoteRunApiCall(self.append_data, params, 60)

  def get_line_no(self):
    return self.view.rowcol(self.view.sel()[0].begin())[0]+1

  def get_current_file_path(self):
    split_path = self.view.file_name().split('/spec/')
    path = None
    if len(split_path)>1:
      path = os.path.join('spec',split_path[-1])
    return path

  def run_command(self):
    self.thread = self.getRemoteThread()
    self.thread.start()

class RunRemoteCmdCommand(BaseRemoteRunCommand):
  def getRemoteThread(self,text):
    text = text.strip()
    l = text.split(' ')
    cmd = l.pop(0)
    params = {'cwd':REMOTE_PROJECT_ROOT,\
                'cmd':cmd,\
                'args':l}
    return SocketRemoteRunApiCall(self.append_data, params, 60)

  def run_command(self):
    # self.thread = self.getRemoteThread()
    # self.thread.start()
    if self.args:
      self.onDone(self.args)
    else:
      sublime.active_window().show_input_panel('Enter a command:','',
      self.onDone, None, None)

  def onDone(self,text):
    self.show_tests_panel()
    self.thread = self.getRemoteThread(text)
    self.thread.start()

class StartRemoteRailsCommand(BaseRemoteRunCommand):
  def getRemoteThread(self,text):
    text = text.strip()
    l = text.split(' ')
    cmd = l.pop(0)
    params = {'cwd':REMOTE_PROJECT_ROOT,\
                'cmd':'starts',\
                'args':l}
    return SocketRemoteRunApiCall(self.append_data, params, 60)

  def run_command(self):
    self.thread = self.getRemoteThread('')
    self.thread.start()

  def show_tests_panel(self):
    if self.output_view is None:
      self.output_view = sublime.active_window().get_output_panel("rails")
    # self.clear_test_view()
    sublime.active_window().run_command("show_panel", {"panel": "output.rails"})

class OpenVrailsSettingsFile(sublime_plugin.TextCommand):
  def run(self, edit):
    _settings = os.path.join(sublime.packages_path(),"vrails", "vrails.sublime-settings")
    sublime.active_window().open_file(_settings)

class TouchOnSave(sublime_plugin.EventListener):
  def on_post_save(self,view):
    _settings = sublime.load_settings("vrails.sublime-settings")
    touch_on_save = _settings.get("touch_on_save")
    
    if touch_on_save == "true"
      path = view.file_name()
      print "file:"+path
      fold_path = view.window().folders()[0]
      if path.startswith(fold_path):
        cmd = {'cmd':'touch ' + path[len(fold_path)+1:].replace('\\','/')}
        view.run_command('run_remote_cmd',cmd)
