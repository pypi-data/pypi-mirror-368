import json
from dataencoder import quotedstr

d = {
	"gret":"HGREert",
	"ynh":"RtghretbertBHER"
}
print(quotedstr(json.dumps(d)))
