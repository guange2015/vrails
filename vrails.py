#coding=utf-8
import sublime, sublime_plugin
import urllib  
import urllib2  
import threading  
import functools
import os

REMOTE_SERVER = "http://localhost:8080/"
REMOTE_PROJECT_ROOT ='./'
TEST_COMMAND = 'rspec spec --drb'

class RemoteRunApiCall(threading.Thread):  
    def __init__(self,finish_callback, cmd, timeout):    
        super(RemoteRunApiCall,self).__init__()
        self.timeout = timeout  
        self.result = None  
        self.finish_callback = finish_callback
        self.cmd = cmd
  
    def run(self):  
        try:  
            data = self.cmd
            print data
            request = urllib2.Request(REMOTE_SERVER\
                        +'exe_cmd?'+data, \
                        headers={"User-Agent": "Sublime Prefixr"})  
            
            http_file = urllib2.urlopen(request, timeout=self.timeout)  
            self.result = http_file.read()  
        except (urllib2.HTTPError) as (e):  
            self.result = '%s: HTTP error %s contacting API' % (__name__, str(e.code))  
        except (urllib2.URLError) as (e):  
            self.result = '%s: URL error %s contacting API' % (__name__, str(e.reason)) 

        print self.result+"\n"
        sublime.set_timeout(functools.partial(self.finish_callback, self.result+"\n"), 1) 

output_view = None
class BaseRemoteRunCommand(sublime_plugin.TextCommand):
  thread = None
  def run(self, edit):
    _settings = sublime.load_settings("vrails.sublime-settings")
    global REMOTE_SERVER; REMOTE_SERVER = _settings.get("remote_server")
    global REMOTE_PROJECT_ROOT; REMOTE_PROJECT_ROOT = _settings.get("remote_project_root")
    global TEST_COMMAND; TEST_COMMAND = _settings.get("test_command")
    self.show_tests_panel()
    self.run_command()

  def run_command(self):
    pass

  def show_tests_panel(self):
    global output_view
    if output_view is None:
      output_view = sublime.active_window().get_output_panel("tests")
    self.clear_test_view()
    sublime.active_window().run_command("show_panel", {"panel": "output.tests"})

  def clear_test_view(self):
    global output_view
    output_view.set_read_only(False)
    edit = output_view.begin_edit()
    output_view.erase(edit, sublime.Region(0, output_view.size()))
    output_view.end_edit(edit)
    output_view.set_read_only(True)

  def append_data(self, data):
    global output_view
    str = data.decode("utf-8")
    str = str.replace('\r\n', '\n').replace('\r', '\n')

    selection_was_at_end = (len(output_view.sel()) == 1
      and output_view.sel()[0]
        == sublime.Region(output_view.size()))
    output_view.set_read_only(False)
    edit = output_view.begin_edit()
    output_view.insert(edit, output_view.size(), str)
    if selection_was_at_end:
      output_view.show(output_view.size())
    output_view.end_edit(edit)
    output_view.set_read_only(True)

class RunRemoteTestCommand(BaseRemoteRunCommand):
  def getRemoteThread(self):
    cmd = data = urllib2.quote('cmd=cd '+REMOTE_PROJECT_ROOT+' && ' + TEST_COMMAND)
    return RemoteRunApiCall(self.append_data, cmd, 5)

  def run_command(self):
    self.thread = self.getRemoteThread()
    self.thread.start()

class RunRemoteCmdCommand(BaseRemoteRunCommand):
  def getRemoteThread(self,text):
    cmd = data = urllib2.quote('cmd=cd '+REMOTE_PROJECT_ROOT+' && ' + text)
    return RemoteRunApiCall(self.append_data, cmd, 15)

  def run_command(self):
    # self.thread = self.getRemoteThread()
    # self.thread.start()
    sublime.active_window().show_input_panel('Enter a command:','',
      self.onDone, None, None)

  def onDone(self,text):
    self.show_tests_panel()
    self.thread = self.getRemoteThread(text)
    self.thread.start()

class OpenVrailsSettingsFile(sublime_plugin.TextCommand):
  def run(self, edit):
    _settings = os.path.join(sublime.packages_path(),"vrails", "vrails.sublime-settings")
    sublime.active_window().open_file(_settings)