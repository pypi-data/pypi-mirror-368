from .mapping import EXTENSIONS
class Mime_Extension_NotFound(Exception): pass
def find(mime):
	try:
		return EXTENSIONS[mime]
	except KeyError:
		raise Mime_Extension_NotFound()