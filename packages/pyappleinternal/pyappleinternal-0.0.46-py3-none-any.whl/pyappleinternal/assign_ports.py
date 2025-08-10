import json
import os
import fcntl
import socket
import time
from contextlib import contextmanager

class PortManager:
    def __init__(self):
        self.lock_file = "/tmp/port_manager.lock"
        self.data_file = "/tmp/port_manager.json"
        self._init_data_file()
        self._last_allocated_port = 10021  # 仅作为查找起点优化

    def _init_data_file(self):
        if not os.path.exists(self.data_file):
            with self._lock():
                with open(self.data_file, 'w') as f:
                    json.dump({"allocated": {}}, f)

    @contextmanager
    def _lock(self):
        lock_fd = open(self.lock_file, 'w')
        start_time = time.time()
        while True:
            try:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except (BlockingIOError, PermissionError):
                if time.time() - start_time > 1:
                    raise TimeoutError("Could not acquire lock within 1 second")
                time.sleep(0.1)
        try:
            yield
        finally:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()

    def _port_available(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.1)
            return s.connect_ex(('localhost', port)) != 0

    def _is_port_allocated(self, data, port):
        return any(port in apps.values() for apps in data['allocated'].values())

    def allocate_port(self, task_id, udid, start_port=10022, end_port=19999):
        with self._lock():
            with open(self.data_file, 'r+') as f:
                data = json.load(f)
                
                if task_id in data['allocated'] and udid in data['allocated'][task_id]:
                    return data['allocated'][task_id][udid]

                # 从上次分配位置开始查找
                port = self._last_allocated_port + 1 if self._last_allocated_port + 1 >= start_port else start_port
                while port <= end_port:
                    if not self._is_port_allocated(data, port) and self._port_available(port):
                        data['allocated'].setdefault(task_id, {})[udid] = port
                        self._last_allocated_port = port
                        f.seek(0)
                        json.dump(data, f)
                        f.truncate()
                        return port
                    port += 1

                # 如果后面没找到，从头开始找
                port = start_port
                while port <= min(self._last_allocated_port, end_port):
                    if not self._is_port_allocated(data, port) and self._port_available(port):
                        data['allocated'].setdefault(task_id, {})[udid] = port
                        self._last_allocated_port = port
                        f.seek(0)
                        json.dump(data, f)
                        f.truncate()
                        return port
                    port += 1

                raise RuntimeError("No available ports")

    def deallocate_port(self, task_id, udid):
        with self._lock():
            with open(self.data_file, 'r+') as f:
                data = json.load(f)
                
                if task_id not in data['allocated'] or udid not in data['allocated'][task_id]:
                    return False
                
                del data['allocated'][task_id][udid]
                if not data['allocated'][task_id]:
                    del data['allocated'][task_id]
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                return True

    def clear_task_ports(self, task_id):
        with self._lock():
            with open(self.data_file, 'r+') as f:
                data = json.load(f)
                
                if task_id not in data['allocated']:
                    return False
                
                del data['allocated'][task_id]
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                return True

    def scan_ports(self, start=10000, end=19999, step=1):
        return [port for port in range(start, end + 1, step) if self._port_available(port)]
