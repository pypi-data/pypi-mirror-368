from deepseek_mcp_client import DeepSeekClient
import asyncio

# Crear agent usando deepseek client con servidor STDIO
agent = DeepSeekClient(
    model='deepseek-chat',
    system_prompt='Eres un asistente especializado en e-commerce con acceso a MercadoLibre.',
    mcp_servers=[{
        'command': 'uv',
        'args': [
            'run',
            '--directory',
            'C:/Users/car06/OneDrive/Escritorio/proyectos/agent_market',
            'python',
            'main.py'
        ],
        'env': {
            'MERCADOLIBRE_ENV': 'production',
            'MERCADOLIBRE_HEADLESS': 'true',
            'MERCADOLIBRE_LOG_LEVEL': 'INFO',
            'MERCADOLIBRE_DB_PATH': 'C:/Users/car06/OneDrive/Escritorio/proyectos/agent_market/data/selectors_db.json'
        },
        'timeout': None  # 🚀 SIN TIMEOUT - Tiempo ilimitado
    }],
    enable_logging=True,
    enable_progress=True,
    log_level="INFO"
)

# Ejecución 
async def main():
    print("💻 Ejecutando ejemplo con servidor STDIO MCP (SIN TIMEOUT)")
    print("=" * 60)
    
    try:
        print("⏱️ Iniciando búsqueda... ")
        result = await agent.execute('Busca laptops gamer económicas calidad precio')
        
        if result.success:
            print("✅ Ejecución exitosa:")
            print(f"📄 Respuesta: {result.output}")
            print(f"🛠️ Herramientas usadas: {', '.join(result.tools_used)}")
            print(f"⏱️ Duración: {result.metadata.get('duration', 0):.2f}s")
            print(f"🔧 Servidores conectados: {result.metadata.get('servers_connected', 0)}")
            print(f"🚀 Tipo de transporte: {result.metadata.get('transport_types', [])}")
        else:
            print(f"❌ Error en la ejecución: {result.error}")
    
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        print("💡 Verifica que:")
        print("   - El directorio del proyecto existe")
        print("   - UV está instalado y configurado")
        print("   - El archivo main.py existe en la ruta especificada")
        print("   - Las variables de entorno están configuradas correctamente")
    
    finally:
        # Cerrar conexiones
        await agent.close()

if __name__ == "__main__":
    asyncio.run(main())