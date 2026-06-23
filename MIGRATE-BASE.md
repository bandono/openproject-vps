# OpenProject Migration Guide (Base Copy)

Full migration preserving all data, tokens, and settings.

## On OLD VPS

### 1. Save Docker Images

```bash
docker save openproject/openproject:16 -o openproject-image.tar
docker save postgres:17 -o postgres-image.tar
```

### 2. Backup Volumes

Stop containers and backup volumes:

```bash
docker compose down

docker run --rm \
  -v openproject-vps_pg_data:/pg_data \
  -v openproject-vps_op_data:/op_data \
  -v $(pwd):/backup \
  busybox \
  tar czf /backup/volumes-backup.tar.gz -C /pg_data . -C /op_data .
```

### 3. Copy to New VPS

Transfer these files:
- `openproject-image.tar`
- `postgres-image.tar`
- `volumes-backup.tar.gz`
- `docker-compose.yml`
- `.env`

---

## On NEW VPS

### 1. Load Images

```bash
docker load -i openproject-image.tar
docker load -i postgres-image.tar
```

### 2. Create Volumes

```bash
docker volume create openproject-vps_pg_data
docker volume create openproject-vps_op_data
```

### 3. Restore Data

```bash
docker run --rm \
  -v openproject-vps_pg_data:/pg_data \
  -v openproject-vps_op_data:/op_data \
  -v $(pwd):/backup \
  busybox \
  tar xzf /backup/volumes-backup.tar.gz -C /pg_data . -C /op_data .
```

### 4. Start Services

```bash
docker compose up -d
```

---

## Notes

- `docker-compose.yml` is portable — works on any VPS with Docker
- All OpenProject data lives in the Docker volumes, not in the images
- `.env` contains credentials — keep it secure
