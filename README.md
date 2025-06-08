# Próbafeladat Megoldás - AI Social Media Agent
Sziasztok, látni fogjatok a többi doksiba a feladat megoldas részleteit de itt csak annyit akartam össztefogalalni hogy kb hogyan gondolkoztam mivel lenne mas ha ebben sokkal tobb időt fektettem volna.

## 🎯 Projekt Áttekintés

A feladat AI rendszer fejlesztése volt, amely képes különböző közösségi média platformokra optimalizált tartalmakat generálni. A megoldás LangGraph workflow orchestration-t használ, human-in-the-loop feedback mechanizmussal.

## 🏗️ Technológiai Stack & Architekturális Döntések

### Backend Framework
- **Python + LangGraph**: Multi-agent workflow orchestration
- **Indoklás**: Bár személyesen nem a Python a kedvencem, a LangGraph kiváló keretrendszer komplex agent workflow-k építéséhez. A LangGraph-et sokat használtam szakdoga alatt. Amin gondolkoztam még hogy valami react native megoldás és akkor javascript amit tökre megszeretttem mostanában.

### Alkalmazott LangGraph Technikák

#### Implementált Agent Architektúra
A kódanalízis alapján az alábbi agent típusokat és prompt stratégiákat használtam:

**1. Context Analysis Agent**
```python
# Szerepkör: Kampány kontextus elemzése
system_prompt = """
Te egy kreatív magyar marketing szakértő vagy. A feladatod hogy elemezd a kampányüzenetet és célközönséget, majd ötleteket generálj a különböző közösségi média platformokra.
"""
```

**2. Content Generation Agent**
```python
# Szerepkör: Platform-specifikus tartalom készítés
system_prompt = """
Te egy szakértő közösségi média tartalomkészítő vagy. A feladatod hogy 
platform-specifikus posztokat generálj.
"""
```

**3. Content Refinement Agent**
```python
# Szerepkör: Felhasználói visszajelzés alapján finomítás
system_prompt = """
Te egy szakértő közösségi média tartalomkészítő vagy. A felhasználó 
visszajelzést adott a meglévő posztokra, és a feladatod hogy javítsd őket.
"""
```

Nagyon kezdetleges promptok nem is én írtam hanem ai generált. As said a célom h megmutassam hogy értem ismerem ezeket a rendszereket és gyorsan tudok fejleszteni. A jó promptok viszont időigényesek erre hogy igazan jó legyen sok időt kellene beletenni de próbafealdat révén ezt nem vittem túlzásba. Maga a metodológiám a következő szokott lenni:
### Fejlesztési Metodológia
1. **Iteratív fejlesztés**: Chat interface-en keresztül prototípus készítés (ahonna indulunk eljutni a megoldáshoz, elvárt elfogadható outputig). 
2. **Információ aggregáció**: Ez után vissza nézem és megvizsgálom mi minden információ kell a sikeres válaszig. Ez lesz a releváns kontextus ezt össze kell állítani és típusokba szedni. 
3. **Prompt chaining**: Ez után vissza nézem milyen lépseket írtam össze. Ezeket a sikeres lépések összefűzése workflow-ba
4. **Inkrementális optimalizáció**: Lépésenkénti finomhangolás
5. **Validáció**: Elvárt output konzisztencia ellenőrzése

#### Workflow Patterns amiket itt alkalmazok
- **Prompt Chaining**: Kontextus elemzés → Tartalom generálás → Finomítás
- **Routing**: Conditional edges a feedback alapján
- **Orchestrator-Workers**: Központi workflow koordináció
- **Human-in-the-Loop**: Interaktív feedback integration

### AI Infrastructure
- **Groq API + Llama 3.3 70B**: Cost-effective, decent teljesítmény
- **Preferált alternatívák**: Claude Sonnet (kedvenc modellem), Gemini 2.5 Pro is jó mostanában szoktam használni
- **Indoklás**: Groq ingyenes és rohadt gyors az LPU-k miatt, de production környezetben Sonnet-re váltanék

### Frontend & Deployment
- **Streamlit**: Gyors prototípus fejlesztés és egyszerű deployment, hogy nektek ne kelljen futtatni meg baszakodni. De am ha lokálisan akarjátok akkor se nehez 3 command-ot kell beirni
- **Élő környezet**: Elérhető webes alkalmazás

## 🧠 Prompt Engineering Stratégia
### Standard Prompt Architektúra
```xml
<system_context>
    [Role and purpose definition]
</system_context>

<context> 
    [Relevant context]
</context>

<instruction>
    [Primary task description]
    [Step-by-step process]
    [Output requirements]
</instruction>

<examples>
    [Relevant examples]
</examples>

<format>
    [Expected output structure]
</format>
```



## 🔄 Workflow Architektúra

### LangGraph State Management
```python
class WorkflowState(BaseModel):
    request: SocialMediaRequest
    campaign_context: Optional[Dict[str, Any]] = None
    generated_posts: Optional[SocialMediaResponse] = None
    user_feedback: Optional[str] = None
    iteration_count: int = 0
    max_iterations: int = 3
```

### Node Implementáció
1. **Context Analysis Node**: Kampány kontextus és célközönség elemzése
2. **Generate Posts Node**: Platform-specifikus tartalom létrehozása
3. **Await Feedback Node**: Human feedback collection pont
4. **Refine Posts Node**: Visszajelzés alapú optimalizáció
5. **Finalize Node**: Végső JSON output formázás

## 📱 Platform Optimalizáció

### Technikai Korlátok Implementálása
```python
# Platform-specifikus limits
- Facebook: max 63206 karakter, max 30 hashtag
- Instagram: max 2200 karakter, max 30 hashtag, 2 kép ötlet
- LinkedIn: max 1300 karakter, max 3 hashtag, professzionális hangnem
- X (Twitter): max 280 karakter, max 2 hashtag
```

## 🔧 Error Handling & Robustness

### Fallback Stratégiák
- **AI Service Failures**: Strukturált fallback válaszok
- **JSON Parse Errors**: Graceful degradation
- **Rate Limiting**: Retry logic és timeout handling
- **State Management**: Workflow state persistence

## 📊 Fejlesztési Megfontolások

### Időkorlátok & Trade-offs
- **Prompt Optimalizáció**: Production környezetben több iterációt igényelne
- **Model Selection**: Cost vs. Performance optimalizáció

### Production Ready Features
- **Type Safety**: Pydantic models mindenhol
- **Logging**: Comprehensive error tracking
- **Configuration**: Environment-based setup
- **Testing**: Unit test coverage

## 🎓 Kutatási Háttér

A megoldás a hawaii-i előadásomban bemutatott advanced prompting technikákon alapul, amelyek közé tartoznak a CoT, step-back prompting, planning prompting, adaptive prompting, reflection és collaboration patterns.

**Előadás referencia**: [Advanced Prompting Techniques](https://www.canva.com/design/DAGmkDBJvAc/1u_CmnrKx5Pn3iL6LoFuEQ/edit)

## 🚀 Következő Lépések

Production környezetben az alábbi területekre fókuszálnék:
1. **Prompt Optimization**: Extensive A/B testing és fine-tuning
2. **Model Upgrade**: Claude Sonnet integráció
3. **Caching Strategy**: Redis-based result caching
4. **Analytics**: Performance metrics és user behavior tracking

