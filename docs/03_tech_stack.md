# Технологический стек — решение (Фаза 0.1)

> Статус: зафиксировано для Фазы 0–1. Пересмотр — при переходе к Фазе 5 (production).

| Компонент | Прототип (Фаза 0–4) | Production (Фаза 5) | Причина |
|---|---|---|---|
| LLM backend | Anthropic Claude API | Anthropic Claude API | Tool use, long context, нужен для агентного цикла |
| Векторная БД | ChromaDB (локально, persistent client) | Qdrant | Chroma — нулевая настройка, простой API; Qdrant — горизонтальное масштабирование |
| Граф памяти | NetworkX (in-process) | Neo4j | NetworkX достаточен пока граф в памяти процесса; Neo4j — при росте/персистентности/конкурентном доступе |
| Оркестрация | Собственная реализация (raw SDK) | Собственная реализация | Полный контроль над goal stack и topology; LangGraph добавляет abstraction overhead, который мешает кастомным self-correction loops |
| Протоколы | MCP (инструменты), заглушка A2A-интерфейса | MCP + A2A | MCP уже используется в Claude Code/SDK; A2A — когда появится внешняя межагентная интеграция |
| Язык | Python 3.11+ | Python 3.11+ (возможен Rust-core для memory consolidation, если профилирование покажет bottleneck) | Скорость разработки прототипа важнее в Фазе 0-4 |
| Платформа сборки | Windows (PyInstaller, onefile exe) | Windows + Linux | Текущее требование — рабочий .exe для Windows |

## Структура зависимостей (requirements.txt)

- `anthropic` — LLM backend
- `chromadb` — episodic/semantic vector store
- `networkx` — semantic graph
- `pydantic` — схемы данных Memory API
- `python-dotenv` — конфигурация (API ключи)
- `pyinstaller` — сборка Windows exe
- `pytest` — тесты
