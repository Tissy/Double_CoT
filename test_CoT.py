import datetime as dt
import uuid
import xml.etree.ElementTree as ET
import socket
import logging

logger = logging.getLogger("django")

ID = {
    "pending": "p",
    "unknown": "u",
    "assumed-friend": "a",
    "friend": "f",
    "neutral": "n",
    "suspect": "s",
    "hostile": "h",
    "joker": "j",
    "faker": "f",
    "none": "o",
    "other": "x"
}
DIM = {
    "space": "P",
    "air": "A",
    "land-unit": "G",
    "land-equipment": "G",
    "land-installation": "G",
    "sea-surface": "S",
    "sea-subsurface": "U",
    "subsurface": "U",
    "other": "X"
}
TYPE = {
    "A0": "SUAPCF----", # - NA
    "A2": "SUAPCF----", # - Small
    "A3": "SUAPCF----", # - Large
    "A4": "SUAPCF----", # - High Vortex
    "A5": "SUAPCF----", # - Heavy
    "A6": "SUAPCF----", # - High Perf
    "A7": "SUAPCH----", # - Rotary Wing - = 'a-f-A-C-H'
    "B0": "SUAPC-----", # - NA
    "B1": "SUAPC-----", # - Glider
    "B2": "SUAPCL----", # - Lighter-than-air
    "B3": "SUAPC-----", # - Para
    "B4": "SUAPC-----", # - Ultra Light
    "B5": "SUAPC-----", # - NA
    "B6": "SUAPMFQ---", # - UAV
    "B7": "SUPPL-----", # - Space
    "C0": "SUGP------", # - NA
    "C1": "SUGP------", # - Emergency Vehicle
    "C2": "SUGP------", # - Service Vehicle
    "C3": "SUGP------", # - Obstruction
    "DRONE (RPV/UAV)": "M-H-Q"
}

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"

class CursorOnTarget:

    @staticmethod
    def atoms(unit):
        timer = dt.datetime
        now = timer.utcnow()
        zulu = now.strftime(DATETIME_FMT)
        stale_part = now.minute + 1
        if stale_part > 59:
            stale_part = stale_part - 60
        stale_now = now.replace(minute=stale_part)
        stale = stale_now.strftime(DATETIME_FMT)

        unit_id = ID[unit["identity"]] or ID["none"]
    
        cot_type = "a-" + unit_id + "-" + DIM[unit["dimension"]]

        if "type" in unit:
          cot_type = cot_type + "-" + unit["type"]

        if "uid" in unit:
          cot_id = unit["uid"]
        else:
          cot_id = uuid.uuid4().get_hex()

        # Event fields
        event_attr = {
            "version": "2.0",
            "uid": cot_id,
            "how": "m-g",
            "time": zulu,
            "start": zulu,
            "stale": stale,
            "type": cot_type
        }

        # Point fields
        point_attr = {
            "lat": str(unit["lat"]),
            "lon": str(unit["lon"]),
            "hae": str(unit["hae"]),
            "ce": "9999999.0",    #unit["ce"],
            "le": "9999999.0"     #unit["le"]
        }



#        try:
#            # UNIT CONVERT: altitude ft to meters
#            point_attr['hae'] = '%.2f' % (0.3048 * int(plane['altitude']))
#        except KeyError:
#            pass

        cot = ET.Element('event', attrib=event_attr)
        ET.SubElement(cot, 'detail')
        ET.SubElement(cot, 'point', attrib=point_attr)
    
        cot_1_xml = '<?xml version="1.0"?>' + ET.tostring(cot, encoding='unicode')
        return cot_1_xml
        
        cot_2_xml = '<?xml version="1.0"?>' + ET.tostring(cot, encoding='unicode')
        return cot_2_xml

    @staticmethod
    def pushUDP(ip_address, port, cot_1_xml):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sent = sock.sendto(bytes(cot_1_xml, 'utf-8'), (ip_address, port))
        return sent

    @staticmethod
    def pushTCP(ip_address, port, cot_1_xml):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn = sock.connect((ip_address, port))
        return sock.send(bytes(cot_1_xml, 'utf-8'))
