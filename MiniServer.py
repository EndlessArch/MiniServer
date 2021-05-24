# import http.server
# import socketserver

# PORT = 80

# Handler = http.server.SimpleHTTPRequestHandler

# with socketserver.TCPServer(("", PORT), Handler) as httpd:
#    print("localhost:", PORT)
#    httpd.serve_forever()

import os
import re
import sys

import http.server

PORT = 80
regex = re.compile(
   r"\{{2}\s*[a-zA-Z0-9_]+\s*(?:\(\s*(?:(?:[a-zA-Z0-9_]+\s*\,\s*){0,}[a-zA-Z0-9_]+\s*)?\))?\s*\}{2}")

r_target_source_dir = ""

def setServerSourceDirectory(_rhs: str) -> None:
   if (_rhs != "" or _rhs != ".") and not _rhs.endswith('/'):
      _rhs += '/'

   r_target_source_dir = _rhs

def getServerSourceDirectory() -> str:
   return r_target_source_dir

def add(par1: int, par2: int, par3: int) -> int:
   return par1 + par2 + par3

### {{ VAR }} -> VAR
### {{ FUNC() }} -> FUNC()
def getSourceConverted(fileName: str) -> str:
   try:
      
      with open(os.path.join(getServerSourceDirectory(), fileName), "r") as file_sources:
         file_lines: str = file_sources.read()

         search_result = list(dict.fromkeys(regex.findall(file_lines))) # delete duplicated search results

         print(str(len(search_result)) + " key found.")

         for cs in search_result:
            try:
               key_str = str(cs[2:-2]).strip() # remind '{{ }}'
               key_val: str = ""

               # TODO: Parameter-available function
               if key_str.endswith(')'): # -> function
                  try:
                     instant_it = key_str.find("(")
                     function_name = key_str[:instant_it]

                     if key_str[instant_it + 1] == ')':
                        key_val = str(globals()[function_name]())
                     else:

                        # function_args: list = list()

                        # instant_num: int = instant_str.find(",");
                        # # ( ~ )
                        # instant_str: str = key_str[it + 1:-1]

                        # while instant_num != -1:
                        #    instant_par_val_str = instant_str[:instant_num]
                        #    instant_str =

                        # print(key_str[:instant_it])
                        # print(instant_num)
                        # print(instant_str)

                        # print(instant_str)

                        # # key_val = str(globals()[key_str[:-2]]())
                        # key_val = str(globals()[function_name](function_args))

                        print("Couldn't call function with parameters(cannot find out the type of the arguments): \"",
                              function_name, "\"")
                  except Exception:
                     print("Failed to find/run function \"" + key_str + "\"")
               else: # -> variable
                  key_val = str(globals()[key_str])

               print(key_str + ":\"" + key_val + "\"")
               file_lines = file_lines.replace(str(cs), key_val)
            except KeyError:
               print("No any key found.\nSearched \"" + cs + "\" with key, \"" + key_str + "\"")

         return file_lines

   except FileNotFoundError:
      print("Failed to find source \"" + fileName + "\"")
      return None

def convertAndSendFile(self: http.server.CGIHTTPRequestHandler, target_file_name: str) -> None:
   print("Sending \"" + (getServerSourceDirectory() + target_file_name) + "\"...")

   self.wfile.write(bytes(getSourceConverted(target_file_name), "UTF-8"))

class cRequestHandler(http.server.CGIHTTPRequestHandler):

   def do_HEAD(self) -> None:
      print("HEAD")

   def do_POST(self) -> None:
      print("POST")

   def do_GET(self) -> None:
      
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
