> **Acceso remoto habilitado.** Puerto expuesto en `0.0.0.0:5433`.
> **Usuario por defecto:** `ialab` (acceso remoto: sin restriccion de host)

---

## Conectar desde WSL (local)

```bash
docker exec -it ia-postgres psql -U ialab -d ialab
# Password: 123456
