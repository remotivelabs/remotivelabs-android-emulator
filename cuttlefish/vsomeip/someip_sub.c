/* Minimal SOME/IP-SD eventgroup subscriber — no deps, builds static, runs in
 * the Android guest's "someip" netns (x86_64). Subscribes to a service's
 * eventgroup, prints the Ack/Nack and any events.
 *
 * Build (static, for the x86_64 guest):
 *     gcc -static -O2 -o someip_sub someip_sub.c
 * Run inside the guest netns:
 *     adb push someip_sub /data/local/tmp/ && adb shell chmod 755 /data/local/tmp/someip_sub
 *     adb shell ip netns exec someip /data/local/tmp/someip_sub 172.31.0.12 0x66 0x143
 *
 * Args: <client_ip> <service_hex> <eventgroup_hex> [server_ip=172.31.0.18]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/select.h>

/* 56-byte SubscribeEventgroup template (from the SOME/IP-SD wire format).
 * Patched at runtime: srv_id[28..29], eventgroup_id[38..39], client IP[48..51],
 * event port[54..55], session id[10..11]. */
static unsigned char tmpl[56] = {
  0xff,0xff,0x81,0x00, 0x00,0x00,0x00,0x30, 0x00,0x00,0x00,0x01, 0x01,0x01,0x02,0x00,
  0xc0,0x00,0x00,0x00, 0x00,0x00,0x00,0x10, 0x06,0x00,0x00,0x10, 0x00,0x66,0x00,0x01,
  0x00,0xff,0xff,0xff, 0x00,0x00,0x01,0x43, 0x00,0x00,0x00,0x0c, 0x00,0x09,0x04,0x00,
  0xac,0x1f,0x00,0x0c, 0x00,0x11,0x77,0x2d
};
#define SD_PORT 30490
#define EV_PORT 30509

int main(int argc, char **argv) {
  if (argc < 4) {
    fprintf(stderr, "usage: %s <client_ip> <service_hex> <eventgroup_hex> [server_ip]\n", argv[0]);
    return 1;
  }
  const char *client_ip = argv[1];
  unsigned service = strtoul(argv[2], 0, 0);
  unsigned eg = strtoul(argv[3], 0, 0);
  const char *server_ip = (argc > 4) ? argv[4] : "172.31.0.18";

  tmpl[28] = service >> 8;  tmpl[29] = service & 0xff;
  tmpl[38] = eg >> 8;       tmpl[39] = eg & 0xff;
  struct in_addr ca;
  if (inet_pton(AF_INET, client_ip, &ca) != 1) { fprintf(stderr, "bad client_ip\n"); return 1; }
  memcpy(&tmpl[48], &ca, 4);
  tmpl[54] = EV_PORT >> 8;  tmpl[55] = EV_PORT & 0xff;

  int one = 1;
  int sd = socket(AF_INET, SOCK_DGRAM, 0);
  setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
  struct sockaddr_in la = {0};
  la.sin_family = AF_INET; la.sin_port = htons(SD_PORT); la.sin_addr = ca;
  if (bind(sd, (void *)&la, sizeof la)) { perror("bind sd"); return 1; }
  struct sockaddr_in srv = {0};
  srv.sin_family = AF_INET; srv.sin_port = htons(SD_PORT);
  inet_pton(AF_INET, server_ip, &srv.sin_addr);

  int ev = socket(AF_INET, SOCK_DGRAM, 0);
  setsockopt(ev, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
  struct sockaddr_in ea = {0};
  ea.sin_family = AF_INET; ea.sin_port = htons(EV_PORT); ea.sin_addr = ca;
  if (bind(ev, (void *)&ea, sizeof ea)) { perror("bind ev"); return 1; }

  printf("Subscribing svc=0x%04x eg=0x%04x to %s:%d; events -> %s:%d\n",
         service, eg, server_ip, SD_PORT, client_ip, EV_PORT);
  fflush(stdout);

  unsigned session = 1;
  time_t last = 0;
  unsigned char buf[2048];
  for (;;) {
    time_t now = time(0);
    if (now - last >= 5) {                  /* (re)subscribe to refresh TTL */
      tmpl[10] = session >> 8; tmpl[11] = session & 0xff; session++;
      sendto(sd, tmpl, sizeof tmpl, 0, (void *)&srv, sizeof srv);
      last = now;
    }
    fd_set fds; FD_ZERO(&fds); FD_SET(sd, &fds); FD_SET(ev, &fds);
    int mx = sd > ev ? sd : ev;
    struct timeval tv = {1, 0};
    if (select(mx + 1, &fds, 0, 0, &tv) <= 0) continue;

    if (FD_ISSET(sd, &fds)) {               /* SD Ack/Nack */
      int n = recv(sd, buf, sizeof buf, 0);
      if (n >= 36) {
        unsigned t = buf[24];
        unsigned ttl = (buf[33] << 16) | (buf[34] << 8) | buf[35];
        const char *kind =
          t == 0x07 ? (ttl ? "SubscribeAck" : "SubscribeNACK(rejected)") :
          t == 0x06 ? (ttl ? "Subscribe"    : "StopSubscribe") :
          t == 0x01 ? (ttl ? "OfferService" : "StopOffer") :
          t == 0x00 ? "FindService" : "entry";
        printf("  SD %s (type=0x%02x ttl=%u)\n", kind, t, ttl);
      } else if (n > 0) printf("  SD response (%d bytes)\n", n);
      fflush(stdout);
    }
    if (FD_ISSET(ev, &fds)) {               /* event/notification */
      int n = recv(ev, buf, sizeof buf, 0);
      if (n >= 16) {
        unsigned svc = (buf[0] << 8) | buf[1], eid = (buf[2] << 8) | buf[3];
        printf("  EVENT svc=0x%04x id=0x%04x payload=", svc, eid);
        for (int i = 16; i < n; i++) printf("%02x", buf[i]);
        printf("\n"); fflush(stdout);
      }
    }
  }
}
