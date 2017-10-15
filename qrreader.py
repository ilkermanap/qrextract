import os
import zbar
import Image
from flask import jsonify

class QRReader:
    def __init__(self, fname):
        sc = zbar.ImageScanner()
        pil = Image.open(fname).convert("L")
        raw = pil.tobytes()
        w,h = pil.size
        self.img = zbar.Image(w,h,'Y800', raw)
        sc.scan(self.img)
        
    def __str__(self):
        cev = "<htm><pre>"
        for s in self.img:
            t = ""
            for x,y in s.location:
                t += "(%d, %d) " % (x,y)
            cev += t + " : " + s.data + " \n"
        return cev + "</pre></html>"

    def json(self):
        res = {}
        i = 0
        for s in self.img:
            res[i] = {"data": s.data, "location": (s.location[0], s.location[2]),
                          "count": s.count, "quality": s.quality, "type": "%s" % s.type, }
            i += 1            
        return jsonify(res)
