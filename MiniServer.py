# import http.server
# import socketserver

# PORT = 80

# Handler = http.server.SimpleHTTPRequestHandler

# with socketserver.TCPServer(("", PORT), Handler) as httpd:
#    print("localhost:", PORT)
#    httpd.serve_forever()

import re
import sys

import http.server

PORT = 80
regex = re.compile(r"\{\{\s*\S+?\s*\}\}")

r_target_source_dir = ""

def setServerSourceDirectory(_rhs: str):
   if (_rhs != "" or _rhs != ".") and not _rhs.endswith('/'):
      _rhs += '/'

   r_target_source_dir = _rhs

def getServerSourceDirectory():
   return r_target_source_dir

### {{ VAR }} -> VAR
### {{ FUNC() }} -> FUNC()
def getSourceConverted(sourceDir: str):
   try:
      with open(getServerSourceDirectory() + sourceDir, "r") as file_sources:
         file_lines = file_sources.read()

         search_result = list(dict.fromkeys(regex.findall(file_lines))) # delete duplicated search results

         print(len(search_result) + " found.")

         for cs in search_result:
            try:
               key_str = str(cs[2:-2]).strip() # remind '{{ }}'
               
               # TODO: Parameter-available function
               if key_str.endswith(')'): # -> function
                  try:
                     print(key_str[:-2] + "()")
                     key_str = str(globals()[key_str[:-2]]())
                  except Exception:
                     print("Failed to find/run function \"" + key_str[:-2] + "\"")
               else: # -> variable
                  key_str = str(globals()[key_str])

               print(str(cs) + ":" + key_str)
               file_lines = file_lines.replace(str(cs), key_str)
            except KeyError:
               print("No any key found.\nSearched \"" + cs + "\" with key, \"" + key_str + "\"")

            return file_lines

         return None
   except FileNotFoundError:
      print("Failed to find source \"" + sourceDir + "\"")
      return None

def convertAndSendFile(self: http.server.CGIHTTPRequestHandler, target_file_dest: str):
   print("Sending \"" + (getServerSourceDirectory() + target_file_dest) + "\"...")

   self.wfile.write(bytes(getSourceConverted(target_file_dest), "UTF-8"))

class cRequestHandler(http.server.CGIHTTPRequestHandler):

   def do_HEAD(self):
      print("HEAD")

   def do_POST(self):
      print("POST")

   def do_GET(self):
      
      self.send_response(200, "OK")
      self.send_header("Content-Type", 'html')
      self.end_headers()

      target_file_name = "index.html"
      
      convertAndSendFile(self, target_file_name)

server_addr = ('', PORT)
httpd = http.server.HTTPServer(server_addr, cRequestHandler)
try:
   print("Port on", PORT)
   httpd.serve_forever()
except KeyboardInterrupt:
   print("Interrupt")
   sys.exit()