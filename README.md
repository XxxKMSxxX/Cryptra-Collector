# Cryptra-Collector

[![CI](https://github.com/XxxKMSxxX/Cryptra-Collector/actions/workflows/ci.yml/badge.svg)](https://github.com/XxxKMSxxX/Cryptra-Collector/actions/workflows/ci.yml)
[![CD](https://github.com/XxxKMSxxX/Cryptra-Collector/actions/workflows/cd.yml/badge.svg)](https://github.com/XxxKMSxxX/Cryptra-Collector/actions/workflows/cd.yml)

## Execute

### Python

```bash
python -Bum collector ${EXCHANGE} ${CONTRACT} ${SYMBOL}
```

### health check

```bash
curl -v http://localhost:8100/health
* Host localhost:8100 was resolved.
* IPv6: ::1
* IPv4: 127.0.0.1
*   Trying [::1]:8100...
* Connected to localhost (::1) port 8100
> GET /health HTTP/1.1
> Host: localhost:8100
> User-Agent: curl/8.7.1
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 200 OK
< date: Sat, 03 Aug 2024 02:12:07 GMT
< server: uvicorn
< content-length: 15
< content-type: application/json
< 
* Connection #0 to host localhost left intact
{"status":"ok"}

---
curl -v http://localhost:8080/health
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /health HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.88.1
> Accept: */*
> 
< HTTP/1.1 200 OK
< date: Sat, 03 Aug 2024 02:12:55 GMT
< server: uvicorn
< content-length: 15
< content-type: application/json
< 
* Connection #0 to host localhost left intact
{"status":"ok"}
```

## Reference

- [【GitHub Actions】 OIDC で AWS 認証を行う](https://zenn.dev/yn26/articles/df05547c44b379)
- [【Github Actions】AWS環境へのTerraformのCI/CD](https://zenn.dev/yn26/articles/3429b834bb0e42)
