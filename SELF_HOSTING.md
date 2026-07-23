# Self-host Aqosoul AzwarAI

This setup runs the Streamlit application in one container and Caddy in another. Caddy obtains and renews a public TLS certificate automatically when the domain points to the server and ports 80/443 are reachable.

## Requirements

- A Linux server with a public IP (Ubuntu or Debian recommended)
- Docker Engine with the Compose plugin
- DNS control for `azwarai.com`
- Inbound TCP ports 80 and 443; UDP 443 is optional but enables HTTP/3

## 1. Configure DNS

Create an `A` record:

```text
Type: A
Name: aqosoul
Value: YOUR_SERVER_PUBLIC_IPV4
TTL: Auto
```

Add an `AAAA` record only when the server has working public IPv6. Remove proxying during initial certificate setup if your DNS provider's proxy causes validation problems.

## 2. Install and start

On the server:

```bash
git clone https://github.com/AzwarMehmood/Solubility_Prediction_App.git
cd Solubility_Prediction_App
cp .env.example .env
docker compose up -d --build
```

If you use UFW:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

Do not expose port 8501 publicly. Compose binds it to server localhost for diagnostics; internet traffic enters through Caddy.

## 3. Verify

```bash
docker compose ps
docker compose logs --tail=100 app
docker compose logs --tail=100 caddy
curl -I https://aqosoul.azwarai.com
```

## Update

```bash
git pull --ff-only
docker compose up -d --build
docker image prune -f
```

## Stop or roll back

Stop without deleting certificate data:

```bash
docker compose down
```

To roll back, check out a known-good Git commit and rebuild. Do not add `--volumes` to `docker compose down` unless you intentionally want to remove Caddy's certificate state.

## Home-network considerations

If the server is physically at home, forward router ports 80 and 443 to the server. Carrier-grade NAT may prevent inbound hosting; in that case use a VPS or a tunnel service. Use a DHCP reservation/static LAN address so router forwarding does not break.
