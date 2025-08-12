from __future__ import annotations
import typer
from .api import generate_passwords, AvPassGenConfig

app = typer.Typer(add_completion=False, help="Generate passwords from real-time audio/video entropy.")

@app.command()
def gen(
    length: int = typer.Option(20, help="Longitud de cada contraseña"),
    count: int = typer.Option(1, help="Cantidad de contraseñas"),
    duration: float = typer.Option(2.0, help="Segundos de captura"),
    video: bool = typer.Option(True, help="Usar cámara"),
    audio: bool = typer.Option(True, help="Usar micrófono"),
    video_device: int = typer.Option(0, help="Índice de cámara"),
    samplerate: int = typer.Option(16000, help="Frecuencia de muestreo de audio"),
    channels: int = typer.Option(1, help="Canales de audio"),
    min_entropy_bits: int = typer.Option(256, help="Umbral heurístico de entropía"),
    charset: str = typer.Option("base64url", help="base64url | alnum | alnum+sym"),
    deterministic: bool = typer.Option(False, help="Usar sal determinista (para pruebas)"),
):
    salt = b"avpassgen-test" if deterministic else None
    cfg = AvPassGenConfig(
        duration_s=duration,
        use_video=video,
        use_audio=audio,
        video_device=video_device,
        audio_samplerate=samplerate,
        audio_channels=channels,
        min_entropy_bits=min_entropy_bits,
        deterministic_salt=salt,
    )
    pwds = generate_passwords(length=length, count=count, charset=charset, cfg=cfg)
    for p in pwds:
        typer.echo(p)

if __name__ == "__main__":
    app()
