#!/usr/bin/env python

#standard library imports

import os
import sys

#network sniffing imports
from scapy.all import get_if_hwaddr
from scapy.layers.inet import IP, TCP
from scapy.layers.l2 import Ether

#internal imports
from ContElements.Context.PacketFlowKey import PacketFlowKey
from ContElements.Context.PacketDirection import PacketDirection

#modifying the path to import a sibling
#by going up to the parent directory
sys.path.append(os.path.realpath('..'))

from ContFreeElements.PacketTime import PacketTime



#Barks like a dog, bytes like a dog.    
class Barks:
    """Extracts features from the traffic related to the bytes in a flow.

    Attributes:
        total_bytes_sent (int): A cummalitve value of the bytes sent.
        total_bytes_received (int): A cummalitve value of the bytes received.
        total_forward_header_bytes (int): A cummalitve value of the bytes sent in the forward direction of the flow.
        total_reverse_header_bytes (int): A cummalitve value of the bytes sent in the reverse direction of the flow.
        row (int) : The row number.

    """
    
    total_bytes_received = 0
    total_bytes_sent = 0
    
    total_forward_header_bytes = 0
    total_reverse_header_bytes = 0

    row = 0

    def __init__(self, feature):
        self.feature = feature
        Barks.row += 1

    def get_bytes_sent(self) -> int:
        """Calculates the amount bytes sent from the machine being used to run DoHlyzer.

        Returns:
            int: The amount of bytes.

        """
        feat = self.feature
        interface = get_if_hwaddr(self.feature.interface)

        return sum(len(packet) for packet, _ in  \
            feat.packets if packet.src == interface)

    def get_sent_rate(self) -> int:
        """Calculates the rate of the bytes being sent in the current flow.

        Returns:
            float: The bytes/sec sent.

        """
        sent = self.get_bytes_sent()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = -1
        else:
            rate = sent / duration

        return rate


    def get_total_bytes_sent(self) -> int:
        """Calculates the cummalative total bytes sent.

        Returns:
            int: The total amount of bytes

        """        
        if Barks.row == 1:
            Barks.total_bytes_sent = self.get_bytes_sent() - self.get_bytes_sent()
        else:
            Barks.total_bytes_sent += self.get_bytes_sent()

        return Barks.total_bytes_sent

    def get_bytes_received(self) -> int:
        """Calculates the amount bytes received.
        
        Returns:
            int: The amount of bytes.

        """
        packets = self.feature.packets
        interface = get_if_hwaddr(self.feature.interface)

        return sum(len(packet) for packet, _ in \
            packets if packet.src != interface)

    def get_received_rate(self) -> int:
        """Calculates the rate of the bytes being received in the current flow.

        Returns:
            float: The bytes/sec received.

        """
        received = self.get_bytes_received()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = -1
        else:
            rate = received / duration

        return rate

    def get_total_bytes_received(self) -> int:
        """Calculates the total bytes received in the sniffing session.

        Returns:
            int: The total amount of bytes

        """    
        if Barks.row == 1:
            Barks.total_bytes_received = self.get_bytes_received() - self.get_bytes_received()
        else:
            Barks.total_bytes_received += self.get_bytes_received()

        return Barks.total_bytes_received

    def get_forward_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the same direction as the flow.
        
        Returns:
            int: The amount of bytes.
            
        """
        def header_size(packet):
            res = len(Ether()) + len(IP())
            if packet.proto == 6:
                res += len(TCP())
            return res

        packets = self.feature.packets

        return sum(header_size(packet) for packet, direction \
            in packets if direction == PacketDirection.FORWARD)

    def get_forward_rate(self) -> int:
        """Calculates the rate of the bytes being going forward
        in the current flow.

        Returns:
            float: The bytes/sec forward.

        """
        forward = self.get_forward_header_bytes()
        duration = PacketTime(self.feature).get_duration()

        if duration > 0:
            rate = forward / duration
        else:
            rate = -1

        return rate

    def get_total_forward_bytes(self) -> int:
        """Calculates the total bytes in the header going forward.

        Returns:
            int: The total amount of bytes

        """

        if Barks.row == 1:
            Barks.total_forward_header_bytes = self.get_forward_header_bytes() \
                - self.get_forward_header_bytes()
        else:
            Barks.total_forward_header_bytes += self.get_forward_header_bytes()


        return Barks.total_forward_header_bytes


    def get_reverse_header_bytes(self) -> int:
        """Calculates the amount of header bytes in the header sent in the opposite direction as the flow.
        
        Returns:
            int: The amount of bytes.
            
        """
        def header_size(packet):
            res = len(Ether()) + len(IP())
            if packet.proto == 6:
                res += len(TCP())
            return res

        packets = self.feature.packets

        return sum(header_size(packet) for packet, direction \
            in packets if direction == PacketDirection.REVERSE)

    def get_total_reverse_bytes(self) -> int:
        """Calculates the total reverse header bytes

        Returns:
            int: The total amount of bytes

        """        
        if Barks.row == 1:
            Barks.total_reverse_header_bytes = self.get_reverse_header_bytes() - self.get_reverse_header_bytes()
        else:
            Barks.total_reverse_header_bytes += self.get_reverse_header_bytes()

        return Barks.total_reverse_header_bytes

    def get_reverse_rate(self) -> int:
        """Calculates the rate of the bytes being going reverse
        in the current flow.

        Returns:
            float: The bytes/sec reverse.

        """
        reverse = self.get_reverse_header_bytes()
        duration = PacketTime(self.feature).get_duration()

        if duration == 0:
            rate = -1
        else:
            rate = reverse / duration

        return rate


    def get_header_in_out_ratio(self) -> float:
        """Calculates the ratio of foward traffic over reverse traffic.

        Returns:
            float: The ratio over reverse traffic.
            If the reverse header bytes is 0 this returns -1 to avoid
            a possible division by 0.

        """
        reverse_header_bytes = self.get_reverse_header_bytes()
        forward_header_bytes = self.get_forward_header_bytes()

        ratio = -1
        if reverse_header_bytes != 0:
            ratio = forward_header_bytes/reverse_header_bytes
        
        return ratio

    def get_total_header_in_out_ratio(self) -> float:
        """Calculates the ratio of foward traffic over reverse traffic.

        Returns:
            float: The ratio over reverse traffic.
            If the reverse header bytes is 0 this returns -1 to avoid /
            a possible division by 0.

        """
        reverse_header_bytes = Barks.total_reverse_header_bytes
        forward_header_bytes = Barks.total_forward_header_bytes

        ratio = -1
        if reverse_header_bytes != 0:
            ratio = forward_header_bytes/reverse_header_bytes
        
        return ratio

    def get_initial_ttl(self) -> int:
        """Obtains the initial time-to-live value.

        Returns:
            int: The initial ttl value in seconds.

        """
        feat = self.feature
        return [packet['IP'].ttl for packet, _ in  \
            feat.packets][0]

