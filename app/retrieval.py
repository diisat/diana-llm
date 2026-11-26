"""Small multilingual lexical retriever: no embeddings, network calls or extra model."""
import json
import re
import unicodedata

CONTEXT_CHAR_LIMIT = 6500
HISTORY_TURNS = 4
HISTORY_TURN_CHARS = 500


def normalize(text):
    return ' '.join(re.findall(r'\w+', ''.join(c for c in unicodedata.normalize('NFKD', text.casefold()) if not unicodedata.combining(c))))


def contains(text, phrase):
    return f' {normalize(phrase)} ' in f' {text} '


ENTITIES = {
    'covea': ['covea'], 'assura': ['assura', 'atlas'],
    'engie': ['engie'], 'cd93': ['cd93', 'seine saint denis', 'iodas', 'departement'],
    'transunion': ['transunion', 'trans union', 'gml', 'credit score'],
    'intevo': ['intevo', 'colpensiones'], 'leanovia': ['leanovia'],
    'mio': ['mio', 'm i o', 'bus', 'predictive', 'predictif', 'predictivo'],
    'marketing-ai': ['marketing', 'streamlit'],
}
TOPICS = {
    'languages': ['speak', 'spoken', 'langues', 'parle', 'idiomas', 'habla', 'languages'],
    'hobbies': ['hobbies', 'hobby', 'art', 'artistic', 'artistique', 'artistico', 'creative', 'creatif', 'creativo', 'peint', 'peinture', 'painting', 'pinta', 'pintura', 'monet', 'ballet', 'tennis', 'loisirs', 'passions'],
    'education': ['education', 'formation', 'formations', 'studies', 'study', 'studied', 'etudes', 'estudios', 'estudio', 'degree', 'diplome', 'universite', 'universidad', 'icesi', 'bootcamp', 'wave it', 'waveit', 'paul valery'],
    'certifications': ['certification', 'certifications', 'certificat', 'certificats', 'certificados', 'certificaciones', 'certified', 'badge', 'badges', 'istqb', 'tosca'],
    'ai': ['ai', 'ia', 'genai', 'intelligence artificielle', 'artificial intelligence', 'inteligencia artificial', 'langchain', 'groq', 'chatgpt', 'codex', 'learning', 'apprend', 'aprendiendo', 'autodidacte'],
    'skills': ['skills', 'skill', 'tech', 'technologies', 'technos', 'tecnologias', 'tool', 'tools', 'outils', 'herramientas', 'competences', 'java', 'python', 'javascript', 'selenium', 'playwright', 'automation', 'automatisation'],
    'projects': ['projects', 'project', 'projets', 'projet', 'proyectos', 'proyecto', 'built', 'build', 'cree', 'realises', 'creado', 'developpe'],
    'career': ['career', 'parcours', 'trayectoria', 'experience', 'experiences', 'experiencia', 'background', 'professionnel', 'professional', 'professionnelle', 'who is', 'qui est', 'quien es', 'present', 'presente', 'resum', 'summary'],
}
STOP = set(normalize('what which when where why how did does do has have is are she her he his diana torres about tell me the a an and or of at in to with for en et ou de du des la le les un une son sa ses quel quels quelle quelles est elle dans chez sur moi que qui quand comment y o el los las su sus cual cuales cuando como por para con se ha es hizo hizo').split())


def compact(item):
    return {k: v for k, v in item.items() if k not in ('portfolio_path', 'experience_id')}


def documents(profile):
    docs = []
    def add(id, facts, topics=(), entities=(), sources=('cv-2026',)):
        docs.append({'id': id, 'facts': facts, 'topics': set(topics), 'entities': set(entities), 'sources': list(sources)})
    add('languages', profile['person']['languages'], ['languages'])
    add('skills', profile['skills'], ['skills'])
    add('ai-learning', {'tools': profile['skills']['ai'], 'learning': profile['personal']['current_learning']}, ['ai'], sources=['cv-2026', 'owner-confirmed'])
    add('hobbies', {k:v for k,v in profile['personal'].items() if k not in ('current_learning','sources')}, ['hobbies'], sources=['owner-confirmed'])
    add('education', profile['education'], ['education'], sources=['cv-2026','owner-confirmed'])
    add('certifications', profile['certifications'], ['certifications'])
    experiences = {e['id']:e for e in profile['experiences']}
    add('career-summary', [{k:e[k] for k in ('organization','role','period','location')} for e in experiences.values()], ['career'])
    add('project-summary', [{k:p[k] for k in ('name','status','technologies') if k in p} for p in profile['projects']], ['projects'], sources=['cv-2026','owner-confirmed'])
    for e in experiences.values():
        entity = next((key for key in ('transunion','intevo','leanovia') if key in e['id']), e['id'])
        add(e['id'], compact(e), entities=[entity], sources=e['sources'])
    for p in profile['projects']:
        facts = compact(p)
        if p.get('experience_id'):
            e = experiences[p['experience_id']]
            # Parent employment dates are useful; its combined mission tool list is not.
            facts['employment'] = {k:e[k] for k in ('organization','role','period')}
        add(p['id'], facts, ['ai'] if p['id'] in ('cd93','marketing-ai') else [], [p['id']], p['sources'])
    return docs


def entity_matches(text):
    return {key for key, aliases in ENTITIES.items() if any(contains(text,a) for a in aliases)}


def select_profile(profile, question, history=()):
    query = normalize(question)
    topics = {key for key, aliases in TOPICS.items() if any(contains(query,a) for a in aliases)}
    entities = entity_matches(query)
    # Resolve short follow-ups against user questions, never assistant claims.
    if not entities and history and not topics.intersection({'languages','hobbies','education','certifications','ai','career','projects'}):
        for turn in reversed(history):
            if turn.role == 'user':
                entities = entity_matches(normalize(turn.content))
                if entities:
                    break
    words = set(query.split()) - STOP
    scored = []
    for index, doc in enumerate(documents(profile)):
        overlap = words & (set(normalize(json.dumps(doc['facts'],ensure_ascii=False)).split()) - STOP)
        if entities:
            score = 100 if entities & doc['entities'] else 0
            # Explicit comparisons may also request education, languages, etc.
            if doc['topics'] & topics & {'languages','hobbies','education','certifications'}:
                score += 80
        else:
            score = 30 * len(topics & doc['topics']) + min(len(overlap), 8)
        if not entities and topics and score < 30:
            score = 0
        if score:
            scored.append((score, index, doc))
    scored.sort(key=lambda row: (-row[0], row[1]))
    context = {
        'person': {k:profile['person'][k] for k in ('name','headline','experience','based_in','links')},
        'facts': [],
        'unknowns': profile['unknowns'],
        'source_catalog': [{'id':'cv-2026','title':'Latest CV · Diana Torres'}],
    }
    source_ids = {'cv-2026'}
    for score, _, doc in scored[:5]:
        candidate = {'topic':doc['id'], 'data':doc['facts'], 'sources':doc['sources']}
        new_sources = source_ids | set(doc['sources'])
        catalog = [{'id':s['id'],'title':s['title']} for s in profile['source_catalog'] if s['id'] in new_sources]
        proposed = {**context, 'facts':context['facts']+[candidate], 'source_catalog':catalog}
        if len(json.dumps(proposed,ensure_ascii=False,separators=(',',':'))) <= CONTEXT_CHAR_LIMIT:
            context = proposed
            source_ids = new_sources
    return context
