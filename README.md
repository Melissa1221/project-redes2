# API de Verificación de Conectividad

Una API REST desarrollada con FastAPI para verificar la conectividad de red mediante ping y traceroute.

## Características

- 🚀 **FastAPI**: Framework moderno y de alto rendimiento
- 🔒 **Seguridad**: Lista blanca de hosts permitidos
- 📊 **Documentación automática**: Swagger UI y ReDoc
- 🧪 **Testing**: Suite de pruebas con pytest
- 🌐 **CORS**: Soporte para aplicaciones web
- ⚡ **Asíncrono**: Operaciones no bloqueantes
- 🔄 **Ping masivo**: Verificación de múltiples hosts simultáneamente

## Instalación

### Requisitos previos

- Python 3.8+
- pip

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación

```bash
# Desarrollo
python main.py

# O usando uvicorn directamente
uvicorn main:app --reload --port 8000

# Producción
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Uso

### Endpoints disponibles

#### 1. Verificación de salud
```http
GET /health
```

#### 2. Ping a un host
```http
GET /ping?host=8.8.8.8&count=4
```

#### 3. Traceroute a un host
```http
GET /traceroute?host=google.com&max_hops=30
```

#### 4. Ping masivo
```http
POST /ping/bulk?hosts=8.8.8.8&hosts=1.1.1.1&count=4
```

#### 5. Hosts permitidos
```http
GET /allowed-hosts
```

### Ejemplos de respuesta

#### Ping
```json
{
  "host": "8.8.8.8",
  "packets_transmitted": 4,
  "packets_received": 4,
  "packet_loss": 0.0,
  "min_ms": 12.5,
  "avg_ms": 15.2,
  "max_ms": 18.7,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Traceroute
```json
{
  "host": "google.com",
  "hops": [
    {
      "hop": 1,
      "host": "192.168.1.1",
      "rtt_ms": 1.2
    },
    {
      "hop": 2,
      "host": "10.0.0.1",
      "rtt_ms": 5.8
    }
  ],
  "timestamp": "2024-01-15T10:30:00"
}
```

## Documentación

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Seguridad

### Hosts permitidos

Por seguridad, solo se permite hacer ping/traceroute a una lista predefinida de hosts:

- `1.1.1.1` (Cloudflare DNS)
- `8.8.8.8` (Google DNS)
- `8.8.4.4` (Google DNS)
- `1.0.0.1` (Cloudflare DNS)
- `google.com`
- `cloudflare.com`
- `github.com`
- `stackoverflow.com`
- `python.org`
- `fastapi.tiangolo.com`

### Limitaciones

- Máximo 10 paquetes por ping
- Máximo 50 saltos para traceroute
- Máximo 5 hosts en ping masivo
- Timeout de 60 segundos para traceroute

## Testing

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con coverage
pytest --cov=. --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_ping.py::test_ping_valid_host -v
```

## Configuración para Postman

### Variables de entorno

```json
{
  "base_url": "http://localhost:8000",
  "default_host": "8.8.8.8",
  "test_count": "4"
}
```

### Colección de pruebas

Importa la colección desde `postman/connectivity-api.json` o crea manualmente:

1. **GET /health**
   - URL: `{{base_url}}/health`
   - Test: Verificar status 200 y estructura de respuesta

2. **GET /ping**
   - URL: `{{base_url}}/ping?host={{default_host}}&count={{test_count}}`
   - Test: Verificar packet_loss < 100%

3. **GET /traceroute**
   - URL: `{{base_url}}/traceroute?host={{default_host}}&max_hops=15`
   - Test: Verificar que hops sea un array

## Despliegue

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build y run

```bash
docker build -t connectivity-api .
docker run -p 8000:8000 connectivity-api
```

## Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT.