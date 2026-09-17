# Copyright (c) 2026 Dobot
# Licensed under the MIT License

"""
TCP connection manager

Provides general TCP connection functionality with auto-reconnect and connection state monitoring
"""

import socket
import threading
import logging
import time
from typing import Optional, Callable
from .exceptions import ConnectionError

logger = logging.getLogger("dobot_sdk")


class DobotConnection:
    """
    TCP connection manager
    
    Responsible for establishing and maintaining TCP connections with the robot, supporting:
    - Receive timeout settings
    - Auto-reconnect mechanism
    - Exponential backoff reconnect strategy
    - Connection state change callback
    """
    
    def __init__(self, ip: str, port: int, buffer_size: int = 144000):
        """
        Initialize connection
        
        Args:
            ip: Robot IP address
            port: Port number (29999 or 30004)
            buffer_size: Receive buffer size
        """
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        self._socket: Optional[socket.socket] = None
        self._lock = threading.Lock()
        self._connected = False
        
        # Timeout settings
        self._connect_timeout = 5.0      # Connection timeout (seconds)
        self._receive_timeout = 10.0     # Receive timeout (seconds)
        
        # Auto-reconnect settings
        self._auto_reconnect = False     # Whether auto-reconnect is enabled
        self._reconnect_running = False  # Whether reconnect thread is running
        self._reconnect_thread = None    # Reconnect thread
        self._reconnect_callback = None  # Connection state callback function
        
        # Exponential backoff parameters
        self._min_reconnect_delay = 1    # Minimum reconnect delay (seconds)
        self._max_reconnect_delay = 30   # Maximum reconnect delay (seconds)
        self._reconnect_attempts = 0     # Current reconnect attempt count
        
        # Validate port
        if port not in [29999, 30004, 30005, 30006]:
            raise ValueError(f"Invalid port: {port}. Must be 29999, 30004, 30005, or 30006")
    
    def set_timeout(self, connect_timeout: float = None, receive_timeout: float = None):
        """
        Set timeout values
        
        Args:
            connect_timeout: Connection timeout (seconds), default 5 seconds
            receive_timeout: Receive timeout (seconds), default 10 seconds
        """
        if connect_timeout is not None:
            self._connect_timeout = connect_timeout
        if receive_timeout is not None:
            self._receive_timeout = receive_timeout
    
    def enable_auto_reconnect(self, enable: bool = True, callback: Callable[[bool], None] = None):
        """
        Enable/disable auto-reconnect
        
        Args:
            enable: Whether to enable auto-reconnect
            callback: Connection state change callback function, receives a boolean parameter indicating connection state
        """
        self._auto_reconnect = enable
        self._reconnect_callback = callback
        
        if enable and not self._reconnect_running and not self._connected:
            self._start_reconnect_loop()
    
    def _start_reconnect_loop(self):
        """Start reconnect loop thread"""
        if self._reconnect_running:
            return
        
        self._reconnect_running = True
        self._reconnect_thread = threading.Thread(
            target=self._reconnect_loop,
            daemon=True
        )
        self._reconnect_thread.start()
        logger.info(f"Auto-reconnect started: {self.ip}:{self.port}")
    
    def _stop_reconnect_loop(self):
        """Stop reconnect loop thread"""
        self._reconnect_running = False
        if self._reconnect_thread:
            self._reconnect_thread.join(timeout=2.0)
            self._reconnect_thread = None
        self._reconnect_attempts = 0
        logger.info(f"Auto-reconnect stopped: {self.ip}:{self.port}")
    
    def _reconnect_loop(self):
        """Reconnect loop with exponential backoff strategy"""
        while self._reconnect_running:
            try:
                # Calculate exponential backoff delay
                delay = min(
                    self._min_reconnect_delay * (2 ** self._reconnect_attempts),
                    self._max_reconnect_delay
                )
                
                logger.info(f"Waiting {delay:.1f}s before reconnect attempt: {self.ip}:{self.port}")
                time.sleep(delay)
                
                if not self._reconnect_running:
                    break
                
                # Attempt to reconnect
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._socket.settimeout(self._connect_timeout)
                self._socket.connect((self.ip, self.port))
                
                # Set receive buffer and timeout
                self._socket.setsockopt(
                    socket.SOL_SOCKET, 
                    socket.SO_RCVBUF, 
                    self.buffer_size
                )
                self._socket.settimeout(self._receive_timeout)
                
                self._connected = True
                self._reconnect_attempts = 0  # Reset reconnect counter
                
                logger.info(f"TCP reconnect successful: {self.ip}:{self.port}")
                
                # Call connect success callback
                if self._reconnect_callback:
                    try:
                        self._reconnect_callback(True)
                    except Exception as e:
                        logger.error(f"Connect success callback failed: {str(e)}")
                
                # Reconnect successful, exit reconnect loop
                self._stop_reconnect_loop()
                
            except socket.timeout:
                self._reconnect_attempts += 1
                logger.warning(f"Reconnect timeout ({self._reconnect_attempts} times): {self.ip}:{self.port}")
                
            except socket.error as e:
                self._reconnect_attempts += 1
                logger.warning(f"Reconnect failed ({self._reconnect_attempts} times): {self.ip}:{self.port} - {str(e)}")
                
            except Exception as e:
                self._reconnect_attempts += 1
                logger.error(f"Reconnect exception ({self._reconnect_attempts} times): {self.ip}:{self.port} - {str(e)}")
    
    def connect(self, timeout: float = None):
        """
        Establish TCP connection
        
        Args:
            timeout: Connection timeout (seconds), defaults to value set during initialization
            
        Raises:
            ConnectionError: Raised when connection fails
        """
        actual_timeout = timeout if timeout is not None else self._connect_timeout
        
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(actual_timeout)
            self._socket.connect((self.ip, self.port))
            
            # Set receive buffer and timeout
            self._socket.setsockopt(
                socket.SOL_SOCKET, 
                socket.SO_RCVBUF, 
                self.buffer_size
            )
            self._socket.settimeout(self._receive_timeout)
            
            self._connected = True
            self._reconnect_attempts = 0  # Reset reconnect counter
            
            logger.info(f"TCP connection successful: {self.ip}:{self.port}")
            
            # Call connect success callback
            if self._reconnect_callback:
                try:
                    self._reconnect_callback(True)
                except Exception as e:
                    logger.error(f"Connect success callback failed: {str(e)}")
            
        except socket.timeout:
            logger.error(f"TCP connection timeout: {self.ip}:{self.port}")
            self._trigger_disconnect_callback()
            raise ConnectionError("Connection timeout", ip=self.ip, port=self.port)
        except socket.error as e:
            logger.error(f"TCP connection failed: {self.ip}:{self.port} - {str(e)}")
            self._trigger_disconnect_callback()
            raise ConnectionError(f"Connection failed: {str(e)}", ip=self.ip, port=self.port)
    
    def _trigger_disconnect_callback(self, force: bool = False):
        """
        Trigger disconnect callback
        
        Args:
            force: Whether to force callback trigger (without checking connection state)
        """
        if self._reconnect_callback and (force or self._connected):
            try:
                self._reconnect_callback(False)
            except Exception as e:
                logger.error(f"Disconnect callback failed: {str(e)}")
    
    def disconnect(self):
        """Close connection"""
        # Stop auto-reconnect
        self._stop_reconnect_loop()
        
        if self._socket:
            try:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
                logger.info(f"TCP connection disconnected: {self.ip}:{self.port}")
            except Exception as e:
                logger.warning(f"Error during TCP disconnect: {str(e)}")
            finally:
                self._socket = None
                self._connected = False
                # Force trigger disconnect callback (user-initiated disconnect)
                self._trigger_disconnect_callback(force=True)
    
    def send_text(self, text: str):
        """
        Send text command (for Dashboard)
        
        Args:
            text: Command string to send
        """
        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to robot")
        
        try:
            # Send directly encoded, add newline
            command = text if text.endswith('\n') else text + '\n'
            self._socket.send(command.encode('utf-8'))
            logger.debug(f"Send command: {text.strip()}")
        except Exception as e:
            self._connected = False
            logger.error(f"Send command failed: {text.strip()} - {str(e)}")
            self._trigger_disconnect_callback()
            
            # If auto-reconnect is enabled, start reconnect loop
            if self._auto_reconnect and not self._reconnect_running:
                self._start_reconnect_loop()
            
            raise ConnectionError(f"Send failed {str(e)}")
    
    def receive_text(self, buffer_size: int = 1024) -> str:
        """
        Receive text response (for Dashboard)
        
        Args:
            buffer_size: Receive buffer size
            
        Returns:
            str: Received string
        """
        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to robot")
        
        try:
            data = self._socket.recv(buffer_size)
            if not data:
                raise ConnectionError("Connection closed")
            
            response = data.decode('utf-8').strip()
            logger.debug(f"Receive response: {response}")
            return response
        except socket.timeout:
            self._connected = False
            logger.error(f"Receive response timeout: {self.ip}:{self.port}")
            self._trigger_disconnect_callback()
            
            # If auto-reconnect is enabled, start reconnect loop
            if self._auto_reconnect and not self._reconnect_running:
                self._start_reconnect_loop()
            
            raise ConnectionError("Receive timeout")
        except Exception as e:
            self._connected = False
            logger.error(f"Receive response failed: {str(e)}")
            self._trigger_disconnect_callback()
            
            # If auto-reconnect is enabled, start reconnect loop
            if self._auto_reconnect and not self._reconnect_running:
                self._start_reconnect_loop()
            
            raise ConnectionError(f"Receive failed: {str(e)}")
    
    def receive_bytes(self, buffer_size: int = 144000) -> bytes:
        """
        Receive raw bytes (for Feedback)
        
        Args:
            buffer_size: Receive buffer size
            
        Returns:
            bytes: Received raw bytes
        """
        if not self._connected or not self._socket:
            raise ConnectionError("Not connected to robot")
        
        try:
            data = self._socket.recv(buffer_size)
            if not data:
                raise ConnectionError("Connection closed")
            
            logger.debug(f"Receive byte data: {len(data)} bytes")
            return data
        except socket.timeout:
            self._connected = False
            logger.error(f"Receive byte data timeout: {self.ip}:{self.port}")
            self._trigger_disconnect_callback()
            
            # If auto-reconnect is enabled, start reconnect loop
            if self._auto_reconnect and not self._reconnect_running:
                self._start_reconnect_loop()
            
            raise ConnectionError("Receive timeout")
        except Exception as e:
            self._connected = False
            logger.error(f"Receive byte data failed: {str(e)}")
            self._trigger_disconnect_callback()
            
            # If auto-reconnect is enabled, start reconnect loop
            if self._auto_reconnect and not self._reconnect_running:
                self._start_reconnect_loop()
            
            raise ConnectionError(f"Receive failed: {str(e)}")
    
    def send_receive_text(self, text: str, recv_size: int = 1024) -> str:
        """
        Send and receive response (thread-safe)
        
        Args:
            text: String to send
            recv_size: Receive buffer size
            
        Returns:
            str: Received response
        """
        with self._lock:
            self.send_text(text)
            return self.receive_text(recv_size)
    
    @property
    def is_connected(self) -> bool:
        """Check connection status"""
        return self._connected
    
    @property
    def reconnect_enabled(self) -> bool:
        """Check if auto-reconnect is enabled"""
        return self._auto_reconnect
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
        return False
    
    def __del__(self):
        """Destructor"""
        self.disconnect()
