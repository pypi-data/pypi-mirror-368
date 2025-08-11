#!/usr/bin/env python3
"""
Demo simple usando un modelo de Anthropic con el tracing del SDK de Kairoz.
Realiza una request REAL al API de Anthropic (Messages API) y mapea usage
para que el dashboard muestre tokens y costo (incluido prompt caching si aplica).

Requisitos:
- Exportar ANTHROPIC_API_KEY en el entorno.
- Paquete `anthropic` instalado: `pip install anthropic`
"""
import os
import time
import random
from typing import Dict, Any

# Asegurar import del SDK local
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'kairoz'))

from tracking import initialize_tracking, trace

API_KEY = os.getenv("KAIROZ_API_KEY", "")
BASE_URL = os.getenv("KAIROZ_API_URL", "http://localhost:3002")

# Inicializar tracking
initialize_tracking(API_KEY, BASE_URL)

ANTHROPIC_MODEL = "claude-opus-4-20250514"
ANTHROPIC_API_KEY = ""


def anthropic_call(prompt: str) -> Dict[str, Any]:
    """Llama al API real de Anthropic y retorna output + usage normalizado."""
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "Falta ANTHROPIC_API_KEY en el entorno. Exportá la clave para continuar."
        )
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "El paquete 'anthropic' no está instalado. Ejecutá: pip install anthropic"
        )

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Mensajes API (Claude 3)
    resp = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=256,
        temperature=0.2,
        messages=[
            {"role": "user", "content": prompt},
        ],
        # Podrías agregar system, metadata, etc.
    )

    # Extraer texto (concatenar bloques)
    output_text = "".join([
        block.text for block in (resp.content or []) if getattr(block, "type", None) == "text"
    ]) or str(resp)

    # Mapear usage a camelCase para la API (u puede ser modelo Pydantic, no dict)
    u = getattr(resp, "usage", None)

    def get_u(field: str):
        if u is None:
            return None
        # Pydantic model attributes
        val = getattr(u, field, None)
        if val is not None:
            return val
        # Dict fallback
        if isinstance(u, dict):
            return u.get(field)
        return None

    input_tokens = get_u("input_tokens")
    output_tokens = get_u("output_tokens")
    cache_read = get_u("cache_read_input_tokens")
    cache_create = get_u("cache_creation_input_tokens")

    usage_norm = {
        "promptTokens": input_tokens,
        "completionTokens": output_tokens,
        "totalTokens": (input_tokens or 0) + (output_tokens or 0),
        "cacheReadTokens": cache_read,
        "cacheWriteTokens": cache_create,
        "model": ANTHROPIC_MODEL,
    }

    return {"output": output_text, "usage": usage_norm}


def main():
    user_id = "anthropic_user_1"
    session_id = f"session_{int(time.time())}"
    prompt = "Resumí en 3 puntos las ventajas de usar embeddings multimodales."

    print("🚀 Demo Anthropic + Trace (Kairoz SDK)")
    print("=" * 60)

    with trace(
        name="anthropic_simple_trace",
        user_id=user_id,
        session_id=session_id,
        metadata={"provider": "anthropic"},
        tags=["demo", "anthropic"],
    ) as t:
        # Una única generation
        with t.generation(
            name="anthropic_generation",
            model=ANTHROPIC_MODEL,
            input_data={"prompt": prompt},
            metadata={"temperature": 0.2},
        ) as gen:
            print(f"🤖 Modelo: {ANTHROPIC_MODEL}")
            print(f"📝 Prompt: {prompt}")
            start = time.time()
            result = anthropic_call(prompt)
            duration = time.time() - start

            # Actualizar la generation con la respuesta y el uso
            gen.update(
                output=result["output"],
                usage=result["usage"],
            )

            print(f"✅ Listo en {duration:.2f}s")
            print("🧮 Tokens:", result["usage"])  # se verán también en el dashboard

    print("\nListo. Abrí el dashboard y seleccioná la Generation para ver latencia, tokens y costo.")


if __name__ == "__main__":
    main()
