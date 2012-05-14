import sublime, sublime_plugin
import urllib  
import urllib2  
import threading  

event1 = threading.Event()

class RemoteRunApiCall(threading.Thread):  
    def __init__(self,view, timeout):    
        self.timeout = timeout  
        self.result = None  
        
        self.view = view
        threading.Thread.__init__(self)  
  
    def run(self):  
        try:  
            data = urllib.urlencode({'cmd': 'rspec', 'args':'spec'})  
            request = urllib2.Request('http://localhost:8080/exe_cmd?'+data,  
                headers={"User-Agent": "Sublime Prefixr"})  
            
            http_file = urllib2.urlopen(request, timeout=self.timeout)  
            self.result = http_file.read()  
            event1.clear()
            return  
  
        except (urllib2.HTTPError) as (e):  
            err = '%s: HTTP error %s contacting API' % (__name__, str(e.code))  
        except (urllib2.URLError) as (e):  
            err = '%s: URL error %s contacting API' % (__name__, str(e.reason))  
  
        sublime.error_message(err)  
        self.result = False  

    

output_view = None
class RemoteRunCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    thread = RemoteRunApiCall(self.view, 5)
    thread.start()
    thread.join()
    self.output(thread.result)
  
  def show_output_view(self):
      global output_view
      if not output_view:
          output_view = self.view.window().get_output_panel("evalsel")
      self.view.window().run_command('show_panel', {'panel': 'output.evalsel'})

  def output(self, info):
    global output_view
    self.show_output_view()
    output_view.set_read_only(False)
    edit = output_view.begin_edit()
     
    output_view.insert(edit, output_view.size(), info)
    self.scroll_to_view_end()
 
    output_view.end_edit(edit)
    output_view.set_read_only(True)
    self.show_output_view()