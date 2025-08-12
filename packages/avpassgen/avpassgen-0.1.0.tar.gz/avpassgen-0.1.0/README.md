**Qué es**: librería y CLI que captura **video** y **audio** en tiempo real, mezcla esa entropía con el **CSPRNG del sistema** (HKDF) y genera **contraseñas seguras**.

> No es determinista por diseño (tipo LavaRand). Puedes activar una sal determinista solo para pruebas.

## Instalación

```bash
pip install -e .[cli]
```

En Windows/macOS/Linux deben existir dispositivos de **cámara** y/o **micrófono** accesibles. Si alguno falla, la librería cae en **OS randomness** igualmente.

## Uso rápido (CLI)

```bash
avpassgen --length 24 --count 3 --duration 3
```

## Uso en código

```python
from avpassgen import generate_passwords, AvPassGenConfig

cfg = AvPassGenConfig(duration_s=3.0, use_video=True, use_audio=True)
passwords = generate_passwords(length=24, count=5, cfg=cfg)
print(passwords)
```

## Seguridad
- Mezcla entropía A/V con `os.urandom()` vía **HKDF-SHA256**.
- Verifica heurísticamente la entropía (umbral configurable).
- Para **login reproducible**, usa en su lugar una librería **determinista** (imagen+frase) o activa `deterministic_salt` sabiendo que entonces será repetible.

## Limitaciones
- `sounddevice` requiere PortAudio (ruedas precompiladas suelen estar disponibles).
- En entornos sin dispositivos, la entropía provendrá del OS.
- Las estimaciones de entropía son heurísticas; para producción, añade baterías de tests (NIST SP 800-90B).
