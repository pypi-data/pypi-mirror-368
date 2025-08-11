#!/usr/bin/env python3
"""
Demo de experiencia de usuario - Kairoz Python SDK
Este script simula cómo un desarrollador real usaría el módulo de tracing
en una aplicación de chatbot con IA.
"""

import os
import time
import random
from typing import Dict, List, Any

# Configurar el path para importar el SDK
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'kairoz'))

from tracking import (
    initialize_tracking,
    trace,
    add_score,
    track_llm_call
)

# Configuración del SDK
API_KEY = os.getenv("KAIROZ_API_KEY", "")
BASE_URL = os.getenv("KAIROZ_API_URL", "http://localhost:3002")

# Inicializar el tracking
initialize_tracking(API_KEY, BASE_URL)

print("🚀 Kairoz Python SDK - Demo de Experiencia de Usuario")
print("=" * 60)
print("Simulando una aplicación de chatbot con IA...")
print()

# Simulación de base de datos de usuarios
users_db = {
    "user_123": {"name": "Ana García", "plan": "premium"},
    "user_456": {"name": "Carlos López", "plan": "free"},
    "user_789": {"name": "María Rodríguez", "plan": "premium"}
}

# Simulación de diferentes modelos de IA
models = {
    "gpt-4": {"cost_per_token": 0.00003, "quality": "high"},
    "gpt-3.5-turbo": {"cost_per_token": 0.000002, "quality": "medium"},
    "claude-3": {"cost_per_token": 0.000015, "quality": "high"}
}

@track_llm_call("generate_response")
def call_ai_model(model: str, prompt: str, user_context: Dict) -> Dict[str, Any]:
    """Simula una llamada a un modelo de IA."""
    print(f"  🤖 Llamando al modelo {model}...")
    
    # Simular tiempo de procesamiento
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    
    # Simular respuesta del modelo
    responses = [
        "¡Hola! Estoy aquí para ayudarte. ¿En qué puedo asistirte hoy?",
        "Entiendo tu pregunta. Basándome en la información disponible...",
        "Esa es una excelente pregunta. Te puedo ayudar con eso.",
        "Permíteme analizar tu solicitud y darte una respuesta detallada."
    ]
    
    response = random.choice(responses)
    tokens_used = random.randint(50, 200)
    
    return {
        "response": response,
        "model": model,
        "tokens_used": tokens_used,
        "processing_time": processing_time,
        "cost": tokens_used * models[model]["cost_per_token"]
    }

def process_user_message(user_id: str, message: str, session_id: str) -> Dict[str, Any]:
    """Procesa un mensaje de usuario completo con tracing."""
    
    user_info = users_db.get(user_id, {"name": "Usuario Desconocido", "plan": "free"})
    
    # Crear una traza para toda la conversación
    with trace(
        name="chat_conversation",
        user_id=user_id,
        session_id=session_id,
        metadata={
            "user_name": user_info["name"],
            "user_plan": user_info["plan"],
            "message_length": len(message)
        },
        tags=["chatbot", "conversation", user_info["plan"]]
    ) as chat_trace:
        
        print(f"💬 Procesando mensaje de {user_info['name']} ({user_info['plan']})")
        print(f"   Mensaje: '{message}'")
        
        # Paso 1: Análisis del mensaje
        with chat_trace.span("message_analysis") as analysis_span:
            print("  🔍 Analizando mensaje...")
            time.sleep(0.2)
            
            # Simular análisis de sentimiento y intención
            sentiment = random.choice(["positive", "neutral", "negative"])
            intent = random.choice(["question", "request", "complaint", "compliment"])
            
            analysis_result = {
                "sentiment": sentiment,
                "intent": intent,
                "language": "es",
                "complexity": random.choice(["simple", "medium", "complex"])
            }
            
            analysis_span.update(
                output=analysis_result,
                metadata={"analysis_time": 0.2}
            )
        
        # Paso 2: Selección del modelo basado en el plan del usuario
        model_selection = "gpt-4" if user_info["plan"] == "premium" else "gpt-3.5-turbo"
        
        # Paso 3: Generación de respuesta con el modelo de IA
        with chat_trace.generation(
            name="ai_response_generation",
            model=model_selection,
            input_data={
                "user_message": message,
                "user_context": user_info,
                "analysis": analysis_result
            },
            metadata={
                "model_selection_reason": f"User plan: {user_info['plan']}",
                "expected_quality": models[model_selection]["quality"]
            }
        ) as generation:
            
            # Llamar al modelo de IA (decorado con @track_llm_call)
            ai_result = call_ai_model(model_selection, message, user_info)
            
            generation.update(
                output=ai_result["response"],
                usage={
                    "prompt_tokens": random.randint(20, 50),
                    "completion_tokens": ai_result["tokens_used"],
                    "total_tokens": ai_result["tokens_used"] + random.randint(20, 50)
                }
            )
        
        # Paso 4: Post-procesamiento
        with chat_trace.span("response_postprocessing") as postprocess_span:
            print("  ⚙️ Post-procesando respuesta...")
            time.sleep(0.1)
            
            # Simular filtros de seguridad y personalización
            final_response = ai_result["response"]
            if user_info["plan"] == "premium":
                final_response += " (Respuesta mejorada para usuario Premium)"
            
            postprocess_span.update(
                output=final_response,
                metadata={
                    "safety_check": "passed",
                    "personalization": user_info["plan"] == "premium"
                }
            )
        
        # Paso 5: Logging de métricas
        total_cost = ai_result["cost"]
        response_time = ai_result["processing_time"] + 0.3  # análisis + post-procesamiento
        
        print(f"  ✅ Respuesta generada en {response_time:.2f}s")
        print(f"     Costo: ${total_cost:.6f}")
        print(f"     Respuesta: '{final_response}'")
        print()
        
        return {
            "response": final_response,
            "metadata": {
                "user_id": user_id,
                "session_id": session_id,
                "model_used": model_selection,
                "response_time": response_time,
                "cost": total_cost,
                "sentiment": sentiment,
                "intent": intent
            }
        }

def simulate_conversation_session():
    """Simula una sesión completa de conversación."""
    
    session_id = f"session_{int(time.time())}"
    user_id = random.choice(list(users_db.keys()))
    
    # Mensajes de ejemplo para simular una conversación
    conversation_messages = [
        "Hola, ¿cómo estás?",
        "¿Puedes ayudarme con información sobre el clima?",
        "Necesito ayuda para planificar un viaje",
        "¿Cuáles son las mejores prácticas para programar en Python?",
        "Gracias por tu ayuda, ha sido muy útil"
    ]
    
    print(f"🎭 Iniciando sesión de conversación: {session_id}")
    print(f"👤 Usuario: {users_db[user_id]['name']}")
    print("-" * 60)
    
    conversation_results = []
    
    for i, message in enumerate(conversation_messages):
        print(f"\n📝 Mensaje {i+1}/{len(conversation_messages)}")
        result = process_user_message(user_id, message, session_id)
        conversation_results.append(result)
        
        # Simular tiempo entre mensajes
        time.sleep(0.5)
    
    return conversation_results, session_id, user_id

def add_quality_scores(session_id: str, user_id: str, results: List[Dict]):
    """Simula la adición de scores de calidad después de la conversación."""
    
    print(f"\n⭐ Evaluando calidad de la conversación {session_id}")
    
    # Simular scores de calidad
    overall_quality = random.uniform(0.7, 0.95)
    user_satisfaction = random.uniform(0.6, 1.0)
    response_relevance = random.uniform(0.8, 0.98)
    
    # En una aplicación real, estos scores vendrían de:
    # - Feedback del usuario
    # - Sistemas de evaluación automática
    # - Análisis de métricas de engagement
    
    with trace(
        name="quality_evaluation",
        user_id=user_id,
        session_id=session_id,
        metadata={"evaluation_type": "post_conversation"}
    ) as eval_trace:
        
        # Agregar scores a nivel de sesión
        add_score("overall_quality", overall_quality, trace_id=eval_trace.trace_id, 
                 comment=f"Calidad general de la conversación")
        
        add_score("user_satisfaction", user_satisfaction, trace_id=eval_trace.trace_id,
                 comment="Satisfacción del usuario basada en feedback")
        
        add_score("response_relevance", response_relevance, trace_id=eval_trace.trace_id,
                 comment="Relevancia de las respuestas generadas")
        
        print(f"  📊 Calidad general: {overall_quality:.2f}")
        print(f"  😊 Satisfacción usuario: {user_satisfaction:.2f}")
        print(f"  🎯 Relevancia respuestas: {response_relevance:.2f}")

def simulate_error_scenario():
    """Simula un escenario con errores para ver cómo se maneja el tracing."""
    
    print(f"\n🚨 Simulando escenario con errores...")
    
    with trace(
        name="error_scenario",
        user_id="user_error",
        metadata={"scenario_type": "error_simulation"}
    ) as error_trace:
        
        try:
            with error_trace.span("risky_operation") as risky_span:
                print("  ⚠️ Ejecutando operación riesgosa...")
                
                # Simular una operación que puede fallar
                if random.random() < 0.7:  # 70% probabilidad de error
                    raise Exception("Error simulado: API externa no disponible")
                
                risky_span.update(output="Operación exitosa")
                
        except Exception as e:
            print(f"  ❌ Error capturado: {e}")
            
            # Agregar información del error al trace
            add_score("error_handled", 1.0, trace_id=error_trace.trace_id,
                     comment=f"Error manejado correctamente: {str(e)}")
            
            # En una aplicación real, aquí implementarías:
            # - Logging del error
            # - Notificaciones a sistemas de monitoreo
            # - Fallbacks o respuestas de error elegantes

def main():
    """Función principal que ejecuta todos los escenarios de demo."""
    
    print("🎬 Comenzando demo de experiencia de usuario...")
    print()
    
    # Escenario 1: Conversación normal
    print("📋 ESCENARIO 1: Conversación Normal")
    results, session_id, user_id = simulate_conversation_session()
    
    # Escenario 2: Evaluación de calidad
    print("\n📋 ESCENARIO 2: Evaluación de Calidad")
    add_quality_scores(session_id, user_id, results)
    
    # Escenario 3: Manejo de errores
    print("\n📋 ESCENARIO 3: Manejo de Errores")
    simulate_error_scenario()
    
    # Resumen final
    print("\n" + "=" * 60)
    print("🎯 RESUMEN DE LA EXPERIENCIA")
    print("=" * 60)
    print("✅ Conversación completa trackeada")
    print("✅ Métricas de rendimiento capturadas")
    print("✅ Scores de calidad agregados")
    print("✅ Manejo de errores implementado")
    print("✅ Contexto de usuario preservado")
    print()
    print("💡 OBSERVACIONES PARA MEJORAS:")
    print("- El SDK maneja bien las operaciones anidadas")
    print("- Los context managers son intuitivos de usar")
    print("- Los decoradores simplifican el tracking de funciones")
    print("- La captura de errores funciona correctamente")
    print("- Los metadatos permiten análisis detallados")
    print()
    print("🔍 Revisa los logs del servidor para ver todos los eventos enviados!")

if __name__ == "__main__":
    main()
