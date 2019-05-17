
import math

def GPSPosition_GlobalA(lat, longi):
    global burstId
    bId = burstId & 0x03

    lat = int(round(lat * 60*60*1000))
    longi = int(round(longi * 60*60*1000))

    #post 8900/can/send?networkId=SW&id=0x&msg=
    if abs(lat) > 536870912 or abs(longi) > 1073741824:
        raise Exception("Longitude or Latitude out of range")

    valid = 0

    lat_part = valid << 31 | (lat if lat>=0 else lat+(1<<30))
    lat_msg = lat_part << 16 | bId << 11 #burst ID
    checksum = getCheckSum(lat_msg, 6, 0x261, checksumbitnumber=11)
    lat_msg = lat_msg | checksum  #checksum
    lat_msg_hex = "{:0=12X}".format(lat_msg)

    longi_part = valid << 31 | (longi if longi >= 0 else longi + (1 << 31))
    longi_msg = longi_part << 16 | bId << 11  #burst ID
    checksum = getCheckSum(longi_msg, 6, 0x262, checksumbitnumber=11)
    longi_msg = longi_msg | checksum  #checksum
    longi_msg_hex = "{:0=12X}".format(longi_msg)

    #whole_part = lat_part < 32 | longi_part
    #msg = "{:0=16X}".format(whole_part)
    print(lat_msg_hex)
    return [("HS", lat_msg_hex, "261", "GPSLatitude"), ("HS", longi_msg_hex, "262", "GPSLongitude")]


def getCheckSum(bytess, numberofbytes, can_id, checksumbitnumber=11):
    #return 0  #use 0 at this time - same with real TCP.

    if numberofbytes < 2:
        raise Exception("number of bytes less than 2. Bytes is {:0=4X}".format(bytess))
    if checksumbitnumber <= 0:
        return bytess

    checksumbytes = int(math.ceil(checksumbitnumber/8.0))
    checksummod = checksumbitnumber%8

    sumofbytes = 0
    for i in range(checksumbytes, numberofbytes):
        sumofbytes += (bytess >> (8*i)) & 0xFF

    if checksummod > 0:
        sumofbytes += ((bytess >> (8*(checksumbytes - 1))) & 0xF8) >> checksummod

    sumofbytes += can_id

    return sumofbytes

def GPSPosition_GlobalB(lat, longi):
    lat = int(round(lat * 60*60*1000))
    longi = int(round(longi * 60*60*1000))

    #post 8900/can/send?networkId=SW&id=0x&msg=
    if abs(lat) > 536870912 or abs(longi) > 1073741824:
        raise Exception("Longitude or Latitude out of range")

    valid = 0

    lat_part = valid << 30 | (lat if lat>=0 else lat+(1<<30))
    longi_part = valid << 31 | (longi if longi>=0 else longi+(1<<31))

    # 64 bit = 30 bit + 34; 34 bit = 31 bit + 3
    body = lat_part << 34 | longi_part << 3


    body_hex = "{:0=16X}".format(body)

    #GPSQltyMets_CAN5_MSG01
    GPSQM_PPSAbsHdgErrEst = 1 #degree
    GPSQM_PPSAbsVelErrEst_Inv = 0
    GPSQM_PPSPstnDilutnPrcsn = 20 #meters
    GPSQM_PPSPstnDilutnPrcsn_Inv = 0
    GPSQM_PPSMode = 0
    GPSQM_PPSAbsVelErrEst = 10 #km/h
    GPSQM_PPS2DAbsPstnErrEst = 10 #m
    GPSQM_PPS3DAbsPstnErrEst = 10 #m
    GPSQM_PPS2DAbsPstnErrEst_Inv = 0
    GPSQM_PPS3DAbsPstnErrEst_Inv = 0
    GPSQM_PPSMode_Inv = 0

    body_quality = GPSQM_PPSAbsHdgErrEst << 57 | GPSQM_PPSAbsVelErrEst_Inv << 56 | \
                   GPSQM_PPSPstnDilutnPrcsn << 46 | GPSQM_PPSPstnDilutnPrcsn_Inv << 45 | \
                   GPSQM_PPSMode << 42 | \
                   GPSQM_PPSAbsVelErrEst << 37 | GPSQM_PPS2DAbsPstnErrEst << 27 | \
                   GPSQM_PPS3DAbsPstnErrEst << 17 | GPSQM_PPS2DAbsPstnErrEst_Inv << 16 | \
                   GPSQM_PPS3DAbsPstnErrEst_Inv << 15 | \
                   GPSQM_PPSMode_Inv << 14
    body_quality_hex = "{:0=16X}".format(body_quality)

    body_quality_hex = "01028000C8008000" #hard code to the one got from vehicle spy

    return [("HS", body_quality_hex, "269", "GPSQltyMets"),
            ("HS", body_hex, "26A", "GPSLatitudeLongitude")]

burstId = 0
GPSPosition_GlobalA(42.519329, -83.028832)
GPSPosition_GlobalA(33.78258, -84.391217)
GPSPosition_GlobalA(42.51748, -83.028689)
GPSPosition_GlobalA(42.528715, -83.013424)