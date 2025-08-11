from socket import *
import os
import fcntl
import struct


# 라즈베리파이 첫번째 ip 가져오는 함수
def get_ip_from_interface(ifname):

    s = socket(AF_INET, SOCK_DGRAM)
    try:
        # SIOCGIFADDR ioctl 호출로 IP 주소 가져오기
        ip = fcntl.ioctl(
            s.fileno(),                     # 소켓 파일 디스크립터
            0x8915,                        # SIOCGIFADDR 코드 (인터페이스 주소 요청)
            struct.pack('256s', ifname[:15].encode('utf-8'))  # 인터페이스 이름 (최대 15자)
        )[20:24]                          # ioctl 반환 값 중 IP 주소 부분 (20~24바이트)
        return inet_ntoa(ip)      # 바이트 IP → 문자열 IP 변환
    except Exception as e:
        return '127.0.0.1'


# ip 검증 후 반환하는 함수
def extract_ip():

    interfaces = os.listdir('/sys/class/net/')  
    for iface in interfaces:
        if iface == 'lo':  
            continue
        ip = get_ip_from_interface(iface)  
        if ip and not ip.startswith("127."):  
            return ip  
    return '127.0.0.1'  


