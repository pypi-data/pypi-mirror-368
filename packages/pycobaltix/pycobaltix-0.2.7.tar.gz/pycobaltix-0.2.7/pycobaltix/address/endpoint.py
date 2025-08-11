from enum import Enum


class NaverEndpoint(str, Enum):
    static_map = "https://maps.apigw.ntruss.com/map-static/v2/raster"
    directions_5 = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
    directions_15 = "https://maps.apigw.ntruss.com/map-direction-15/v1/driving"
    geocoding = "https://maps.apigw.ntruss.com/map-geocode/v2/geocode"
    reverse_geocoding = "https://maps.apigw.ntruss.com/map-reversegeocode/v2/gc"
