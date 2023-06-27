import os
import time
import test_CoT

ATAK_IP = os.getenv('ATAK_IP', 'xx.xx.xx.xx')
ATAK_PORT = int(os.getenv('ATAK_PORT', '8087'))
ATAK_PROTO = os.getenv('ATAK_PROTO', 'TCP')

params_1 = {  # 
    "lat": 54.3883867,
    "lon": -0.95603719,
    "uid": "Test",
    "hae": 10.0,
    "identity": "hostile",
    "dimension": "land-unit",
    "entity": "military",
    "type": "U-C"
#    "type": "U-C-R-H"
}

for i in range(0, 10):
    params_1["lat"] = params_1["lat"] + i/10000.0
    params_1["lon"] = params_1["lon"] + i/10000.0
    print("Params:\n" + str(params_1))
    cot = test_CoT.CursorOnTarget()
    cot_xml = cot.atoms(params_1)

    print("\nXML message:")
    print(cot_xml)

    print("\nPushing to ATAK...")
    if ATAK_PROTO == "TCP":
        sent = cot.pushTCP(ATAK_IP, ATAK_PORT, cot_xml)
    else:
        sent = cot.pushUDP(ATAK_IP, ATAK_PORT, cot_xml)
    print(str(sent) + " bytes sent to " + ATAK_IP + " on port " + str(ATAK_PORT))
    time.sleep(2)