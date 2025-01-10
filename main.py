Life 2



Certainly! Here is the first code snippet:
Snippet 1: Node Class Definition
import socket
import threading
import time
import json
import logging
from queue import PriorityQueue
from cryptography.fernet import Fernet

# Configuration
NODE_ID = f"Node-{socket.gethostname()}"
PORT = 12345
MASTER_NODE_IP = "192.168.1.1"  # Replace with your server's IP
HEARTBEAT_INTERVAL = 5  # Seconds

# Task Definitions
TASK_TYPE_REGISTER = "register"
TASK_TYPE_EXECUTE = "execute"
TASK_TYPE_STATUS = "status"
TASK_TYPE_PING = "ping"

# Status Codes
STATUS_IDLE = "idle"
STATUS_BUSY = "busy"
STATUS_ERROR = "error"

# Encryption Key (Replace with a secure key)
encryption_key = b'your_secret_key' 
cipher = Fernet(encryption_key)

# Logging Configuration
logging.basicConfig(filename='node.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Node:
    def __init__(self, node_id, master_ip, port):
        self.node_id = node_id
        self.master_ip = master_ip
        self.port = port
        self.status = STATUS_IDLE
        self.task_queue = PriorityQueue()
        self.queue_lock = threading.Lock()
        self.cipher = cipher

    def listen_for_tasks(self):
        """Listen for incoming tasks from the network."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(5)
        logging.info(f"{self.node_id} listening for tasks on port {self.port}")

        while True:
            try:
                conn, addr = server_socket.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    if data:
                        # Decrypt the received data
                        encrypted_data = data.encode()
                        decrypted_data = self.cipher.decrypt(encrypted_data).decode()
                        task = json.loads(decrypted_data)
                        logging.info(f"Received task: {task}")
                        self.handle_task(task)
            except Exception as e:
                logging.error(f"Error accepting connection: {e}")


    def send_task(self, task, destination_ip):
        """Send a task to another node."""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((destination_ip, self.port))
            # Encrypt the task data
            encrypted_data = self.cipher.encrypt(json.dumps(task).encode()).decode()
            client_socket.send(encrypted_data.encode())
            client_socket.close()
        except Exception as e:
            logging.error(f"Failed to send task to {destination_ip}: {e}")

    def handle_task(self, task):
        """Handle incoming tasks."""
        if task.get("type") == TASK_TYPE_EXECUTE:
            with self.queue_lock:
                self.task_queue.put((task.get("priority", 0), task))  # Prioritize tasks
        elif task.get("type") == TASK_TYPE_STATUS:
            self.send_status(task.get("sender"))
        elif task.get("type") == TASK_TYPE_PING:
            # Respond to ping requests
            self.send_task({"type": "pong", "node": self.node_id}, task.get("sender"))
        elif task.get("type") == "execute_command":  # Example: Custom task type
            # Process custom commands (e.g., control peripherals)
            command = task.get("command")
            if command == "toggle_led":
                # Simulate toggling an LED
                print("Toggling LED") 
            elif command == "get_sensor_data":
                # Simulate reading sensor data
                sensor_data = {"temperature": 25, "humidity": 50}
                result = {"status": "completed", "id": task.get("id"), "node": self.node_id, "data": sensor_data}
                return result 
        else:
            logging.warning(f"Unknown task type: {task.get('type')}")


    def execute_task(self, task):
        """Execute a given task."""
        try:
            task_id = task.get("id")
            logging.info(f"Executing task {task_id} on {self.node_id}")
            self.status = STATUS_BUSY

            # Simulate task execution (replace with actual task logic)
            time.sleep(task.get("execution_time", 2)) 

            result = {"status": "completed", "id": task_id, "node": self.node_id}
            self.global_tasks[task_id] = result
            logging.info(f"Task {task_id} completed")
            return result
        except Exception as e:
            logging.error(f"Error executing task: {e}")
            return {"status": "failed", "id": task_id, "node": self.node_id, "error": str(e)}
        finally:
            self.status = STATUS_IDLE

    def send_status(self, destination_ip):
        """Send node status to another node."""
        status_data = {"type": "status", "node": self.node_id, "status": self.status}
        self.send_task(status_data, destination_ip)




    def register_node(self):
        """Register this node with the master node."""
        if self.master_ip:
            task = {"type": "register", "node": self.node_id}
            self.send_task(task, self.master_ip)

    def heartbeat(self):
        """Send heartbeat signal to the master node."""
        if self.master_ip:
            self.send_task({"type": "heartbeat", "node": self.node_id}, self.master_ip)

    def run(self):
        self.register_node()
        threading.Thread(target=self.listen_for_tasks, daemon=True).start()
        threading.Thread(target=self.task_manager, daemon=True).start()

        while True:
            self.heartbeat()
            time.sleep(HEARTBEAT_INTERVAL)

