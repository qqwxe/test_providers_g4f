import g4f
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

TEST_PROMPT = "hello, how are u?"

MODELS = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4o-mini",
    "claude-3-haiku",
    "gemini-pro",
]

EXCLUDE_PROVIDERS = {
    "Openai", "OpenAI", "NeedsAuth", "Anthropic", "AnyProvider", 
    "Azure", "BingCreateImages", "BackendApi", "ApiAirforce", "ARTA",
    "You", "BlackForestLabs", "Chatai", "Flux1Dev", "BaseProvider"
}

def get_available_providers():
    """Получить список доступных провайдеров"""
    providers = []
    for name in dir(g4f.Provider):
        if name.startswith("_") or not name:
            continue
        if any(exc in name for exc in EXCLUDE_PROVIDERS):
            continue
        try:
            prov = getattr(g4f.Provider, name)
            providers.append((name, prov))
        except Exception:
            continue
    return providers

def test_provider_model(provider_name, provider, model):
    """Тестировать конкретную комбинацию провайдер+модель"""
    try:
        start_time = time.time()
        response = g4f.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": TEST_PROMPT}],
            provider=provider,
            temperature=0.2,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response and len(response.strip()) > 0:
            return {
                "provider": provider_name,
                "model": model,
                "status": "SUCCESS",
                "response_length": len(response.strip()),
                "time": round(elapsed, 2),
                "response_preview": response.strip()[:100] + "..." if len(response.strip()) > 100 else response.strip()
            }
        else:
            return {
                "provider": provider_name,
                "model": model,
                "status": "EMPTY_RESPONSE",
                "time": round(elapsed, 2)
            }
    except Exception as e:
        return {
            "provider": provider_name,
            "model": model,
            "status": "ERROR",
            "error": str(e)[:200]
        }

def test_default_g4f():
    """Тестировать дефолтный g4f без указания провайдера"""
    try:
        start_time = time.time()
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            temperature=0.2,
            timeout=30
        )
        elapsed = time.time() - start_time
        
        if response and len(response.strip()) > 0:
            return {
                "provider": "DEFAULT_G4F",
                "model": "gpt-3.5-turbo",
                "status": "SUCCESS",
                "response_length": len(response.strip()),
                "time": round(elapsed, 2),
                "response_preview": response.strip()[:100] + "..." if len(response.strip()) > 100 else response.strip()
            }
        else:
            return {
                "provider": "DEFAULT_G4F",
                "model": "gpt-3.5-turbo",
                "status": "EMPTY_RESPONSE",
                "time": round(elapsed, 2)
            }
    except Exception as e:
        return {
            "provider": "DEFAULT_G4F",
            "model": "gpt-3.5-turbo",
            "status": "ERROR",
            "error": str(e)[:200]
        }

def main():
    print("🔍 G4F Provider & Model Tester")
    print("=" * 50)
    
    providers = get_available_providers()
    print(f"📋 Найдено провайдеров для тестирования: {len(providers)}")
    print(f"🎯 Модели для тестирования: {', '.join(MODELS)}")
    print()
    
    print("🧪 Тестирую дефолтный g4f...")
    default_result = test_default_g4f()
    print(f"   {default_result['status']}: {default_result.get('response_preview', default_result.get('error', ''))}")
    print()
    
    tasks = []
    for provider_name, provider in providers:
        for model in MODELS:
            tasks.append((provider_name, provider, model))
    
    print(f"🚀 Запускаю {len(tasks)} тестов...")
    print()
    
    results = []
    successful = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {
            executor.submit(test_provider_model, pname, prov, model): (pname, model)
            for pname, prov, model in tasks
        }
        
        completed = 0
        for future in as_completed(future_to_task, timeout=300):
            pname, model = future_to_task[future]
            try:
                result = future.result(timeout=35)
                results.append(result)
                
                if result["status"] == "SUCCESS":
                    successful.append(result)
                    print(f"✅ {pname} + {model}: {result['time']}s - {result['response_preview']}")
                else:
                    print(f"❌ {pname} + {model}: {result['status']} - {result.get('error', '')}")
                
                completed += 1
                if completed % 10 == 0:
                    print(f"   Прогресс: {completed}/{len(tasks)}")
                    
            except Exception as e:
                print(f"⚠️  {pname} + {model}: TIMEOUT/ERROR - {str(e)[:100]}")
    
    print()
    print("📊 RESULTS:")
    print("=" * 50)
    
    if successful:
        print(f"✅ Рабочих комбинаций: {len(successful)}")
        print()
        
        successful.sort(key=lambda x: x['time'])
        
        print("🏆 ТОП-10 БЫСТРЫХ И РАБОЧИХ:")
        for i, result in enumerate(successful[:10], 1):
            print(f"{i:2d}. {result['provider']:20} + {result['model']:15} ({result['time']:4.1f}s)")
        
        print()
        print("🔧 КОД ДЛЯ ПЛАГИНА:")
        print("priority_providers = [")
        for result in successful[:7]:
            print(f'    "{result["provider"]}",  # {result["time"]}s')
        print("]")
        
        print()
        print("models_fallback = [")
        
        model_counts = {}
        for result in successful:
            model = result["model"]
            model_counts[model] = model_counts.get(model, 0) + 1
        
        sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
        for model, count in sorted_models[:4]:
            print(f'    "{model}",  # работает у {count} провайдеров')
        print("]")
        
    else:
        print("❌ Рабочих комбинаций не найдено!")
        if default_result["status"] == "SUCCESS":
            print("💡 Но дефолтный g4f работает - используйте provider=None")
    
    with open("g4f_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "default_g4f": default_result,
            "all_results": results,
            "successful": successful,
            "total_tested": len(tasks),
            "success_rate": len(successful) / len(tasks) * 100 if tasks else 0
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Полные результаты сохранены в g4f_test_results.json")

if __name__ == "__main__":
    main()
