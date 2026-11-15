
import random

COMMON_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80,
    88, 110, 119, 123, 137, 138, 139, 143, 161, 179,
    194, 389, 427, 443, 445, 465, 500, 512, 513, 514,
    515, 520, 548, 554, 587, 636, 989, 990, 993, 995,
    1080, 1433, 1521, 2049, 2082, 2083, 2086, 2087,
    2181, 1111, 2222, 3333, 4444, 5555, 6666
]

ADDITIONAL_PORTS = random.sample(range(10000, 60000), 50)

BASE_PORTS = sorted(set(COMMON_PORTS + ADDITIONAL_PORTS))

SERVICE_PORTS = {
    "SSH": {22},
    "FTP": {20, 21},
    "HTTP": {80}
}

def generate_ports(enabled_services=None):
    ports = set(BASE_PORTS)

    if enabled_services is not None:
        for service, service_ports in SERVICE_PORTS.items():
            if not enabled_services.get(service, True):
                ports.difference_update(service_ports)

    return sorted(ports)
