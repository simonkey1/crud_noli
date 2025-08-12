#!/usr/bin/env python
"""
Script para probar el rendimiento de los endpoints del POS
Simula condiciones de red lentas para testing
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json

class PosPerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, params: Dict = None) -> Dict:
        """
        Prueba un endpoint y mide el tiempo de respuesta
        """
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.get(url, params=params or {}) as response:
                await response.json()  # Leer respuesta completa
                duration = (time.time() - start_time) * 1000  # en ms
                
                return {
                    "endpoint": endpoint,
                    "params": params or {},
                    "status": response.status,
                    "duration_ms": round(duration, 2),
                    "success": True
                }
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return {
                "endpoint": endpoint,
                "params": params or {},
                "status": 0,
                "duration_ms": round(duration, 2),
                "success": False,
                "error": str(e)
            }
    
    async def run_performance_tests(self):
        """
        Ejecuta una suite completa de pruebas de rendimiento
        """
        print("🚀 Iniciando pruebas de rendimiento del POS...")
        
        # Configurar sesión HTTP
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            
            # Test 1: Carga inicial de productos
            print("\n📦 Test 1: Carga inicial de productos")
            for i in range(5):
                result = await self.test_endpoint(session, "/pos/products", {"limit": 30})
                self.results.append(result)
                print(f"  Intento {i+1}: {result['duration_ms']}ms")
                await asyncio.sleep(0.5)
            
            # Test 2: Búsqueda de productos
            print("\n🔍 Test 2: Búsqueda de productos")
            search_terms = ["cafe", "gr", "a", "cacao", "taza"]
            for term in search_terms:
                result = await self.test_endpoint(session, "/pos/products", {"q": term, "limit": 50})
                self.results.append(result)
                print(f"  Búsqueda '{term}': {result['duration_ms']}ms")
                await asyncio.sleep(0.3)
            
            # Test 3: Búsqueda rápida (nuevo endpoint)
            print("\n⚡ Test 3: Búsqueda rápida")
            for term in search_terms:
                result = await self.test_endpoint(session, "/pos/search", {"q": term, "limit": 20})
                self.results.append(result)
                print(f"  Búsqueda rápida '{term}': {result['duration_ms']}ms")
                await asyncio.sleep(0.3)
            
            # Test 4: Conteo de productos
            print("\n🔢 Test 4: Conteo de productos")
            for i in range(3):
                result = await self.test_endpoint(session, "/pos/products/count", {"q": ""})
                self.results.append(result)
                print(f"  Conteo {i+1}: {result['duration_ms']}ms")
                await asyncio.sleep(0.5)
            
            # Test 5: Carga bajo estrés (múltiples requests simultáneas)
            print("\n💪 Test 5: Carga bajo estrés (10 requests simultáneas)")
            tasks = []
            for i in range(10):
                task = self.test_endpoint(session, "/pos/search", {"q": "cafe", "limit": 20})
                tasks.append(task)
            
            stress_results = await asyncio.gather(*tasks)
            self.results.extend(stress_results)
            
            durations = [r['duration_ms'] for r in stress_results if r['success']]
            if durations:
                print(f"  Promedio: {statistics.mean(durations):.1f}ms")
                print(f"  Mínimo: {min(durations):.1f}ms")
                print(f"  Máximo: {max(durations):.1f}ms")
    
    def analyze_results(self):
        """
        Analiza los resultados y genera un reporte
        """
        print("\n" + "="*60)
        print("📊 ANÁLISIS DE RESULTADOS")
        print("="*60)
        
        # Filtrar resultados exitosos
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        print(f"✅ Requests exitosas: {len(successful)}")
        print(f"❌ Requests fallidas: {len(failed)}")
        
        if not successful:
            print("❌ No hay datos para analizar")
            return
        
        # Análisis por endpoint
        endpoints = {}
        for result in successful:
            endpoint = result['endpoint']
            if endpoint not in endpoints:
                endpoints[endpoint] = []
            endpoints[endpoint].append(result['duration_ms'])
        
        print("\n📈 Rendimiento por endpoint:")
        for endpoint, durations in endpoints.items():
            avg = statistics.mean(durations)
            min_d = min(durations)
            max_d = max(durations)
            p95 = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else avg
            
            print(f"\n{endpoint}:")
            print(f"  📊 Promedio: {avg:.1f}ms")
            print(f"  ⚡ Mínimo: {min_d:.1f}ms") 
            print(f"  🐌 Máximo: {max_d:.1f}ms")
            print(f"  📏 P95: {p95:.1f}ms")
            print(f"  🔢 Requests: {len(durations)}")
            
            # Alertas de rendimiento
            if avg > 1000:
                print(f"  🚨 ALERTA: Promedio muy lento (>{avg:.1f}ms)")
            elif avg > 500:
                print(f"  ⚠️  ADVERTENCIA: Promedio lento (>{avg:.1f}ms)")
            else:
                print(f"  ✅ Rendimiento bueno (<500ms)")
        
        # Estadísticas generales
        all_durations = [r['duration_ms'] for r in successful]
        print(f"\n🌟 ESTADÍSTICAS GENERALES:")
        print(f"  📊 Promedio general: {statistics.mean(all_durations):.1f}ms")
        print(f"  📏 Mediana: {statistics.median(all_durations):.1f}ms")
        print(f"  📐 Desviación estándar: {statistics.stdev(all_durations):.1f}ms")
        
        # Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        avg_general = statistics.mean(all_durations)
        if avg_general > 1000:
            print("  🚨 Rendimiento crítico - Optimización urgente requerida")
            print("  📝 Considerar: índices de BD, cache, paginación")
        elif avg_general > 500:
            print("  ⚠️  Rendimiento mejorable")
            print("  📝 Considerar: optimizar queries, agregar cache")
        else:
            print("  ✅ Rendimiento aceptable")
            print("  📝 Continuar monitoreando en producción")
    
    def save_results(self, filename: str = None):
        """
        Guarda los resultados en un archivo JSON
        """
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"performance_test_{timestamp}.json"
        
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "total_tests": len(self.results),
            "successful_tests": len([r for r in self.results if r['success']]),
            "results": self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultados guardados en: {filename}")

async def main():
    """
    Función principal
    """
    import argparse
    parser = argparse.ArgumentParser(description="Pruebas de rendimiento del POS")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base del servidor")
    parser.add_argument("--save", action="store_true", help="Guardar resultados en archivo")
    args = parser.parse_args()
    
    tester = PosPerformanceTester(args.url)
    
    try:
        await tester.run_performance_tests()
        tester.analyze_results()
        
        if args.save:
            tester.save_results()
            
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error durante las pruebas: {e}")

if __name__ == "__main__":
    print("🔬 POS Performance Tester")
    print("Asegúrate de que el servidor esté ejecutándose en localhost:8000")
    print("Para cambiar la URL usa: python performance_test.py --url http://tu-servidor.com\n")
    
    asyncio.run(main())
