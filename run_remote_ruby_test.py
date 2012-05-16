import sublime, sublime_plugin
import urllib  
import urllib2  
import threading  
import functools

class RemoteRunApiCall(threading.Thread):  
    def __init__(self,finish_callback, timeout):    
        super(RemoteRunApiCall,self).__init__()
        self.timeout = timeout  
        self.result = None  
        self.finish_callback = finish_callback
  
    def run(self):  
        try:  
            data = urllib.urlencode({'cmd': 'rspec', 'args':'spec --drb'})  
            request = urllib2.Request('http://localhost:8080/exe_cmd?'+data,  
                headers={"User-Agent": "Sublime Prefixr"})  
            
            http_file = urllib2.urlopen(request, timeout=self.timeout)  
            self.result = http_file.read()  
        except (urllib2.HTTPError) as (e):  
            self.result = '%s: HTTP error %s contacting API' % (__name__, str(e.code))  
        except (urllib2.URLError) as (e):  
            self.result = '%s: URL error %s contacting API' % (__name__, str(e.reason)) 

        sublime.set_timeout(functools.partial(self.finish_callback, self.result+"\n"), 1) 

output_view = None
class RemoteRunCommand(sublime_plugin.TextCommand):
  thread = None
  def run(self, edit):
    self.show_tests_panel()
    self.thread = RemoteRunApiCall(self.append_data, 5)
    self.thread.start()
    
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