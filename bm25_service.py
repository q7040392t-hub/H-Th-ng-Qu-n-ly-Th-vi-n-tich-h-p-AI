import math
import re
import unicodedata
from collections import Counter
from pathlib import Path


def normalize_text(text):
    text = str(text or '').lower().strip().replace('đ','d')
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def tokenize(text):
    return [t for t in normalize_text(text).split() if len(t) > 1]


def _book_tokens(book):
    # Field boosting by repeating important fields. This keeps the implementation
    # dependency-free while making title / id / author matches rank higher.
    weighted = []
    fields = [
        ('id', 5), ('title', 5), ('author', 3), ('category', 3), ('type', 2),
        ('isbn', 3), ('publisher', 2), ('description', 1), ('location', 1),
    ]
    for field, weight in fields:
        toks = tokenize(book.get(field, ''))
        for _ in range(weight):
            weighted.extend(toks)
    return weighted



STOPWORDS = {
    'sach','cuon','quyen','ve','cho','toi','minh','muon','tim','goi','y','hay','nao','nhung','mot','vai','co','khong','giup','voi'
}

QUERY_EXPANSIONS = {
    'tinh yeu': ['tinh cam','lang man','chua lanh','tinh yeu','tuoi tre'],
    'lang man': ['tinh cam','tinh yeu','lang man'],
    'lap trinh': ['cong nghe thong tin','python','java','coding','phan mem'],
    'python': ['python','lap trinh','cong nghe thong tin'],
    'tri tue nhan tao': ['ai','tri tue nhan tao','machine learning','deep learning','khoa hoc du lieu'],
    'ai': ['tri tue nhan tao','machine learning','deep learning','khoa hoc du lieu'],
    'trinh tham': ['trinh tham','tham tu','bi an','vu an','toi pham'],
    'triet ly': ['triet ly','phat trien ban than','tu duy','niem tin'],
    'ky nang': ['ky nang song','phat trien ban than','giao tiep','tu duy'],
    'kinh te': ['kinh te','kinh doanh','tai chinh','dau tu'],
    'suc khoe': ['suc khoe','dinh duong','tam ly','tim mach'],
}

def _semantic_query(query):
    norm=normalize_text(query)
    # Keep BM25 tokens faithful to what the user typed. Multi-word semantic
    # expansions are applied later as phrase/category boosts. Splitting expansion
    # phrases into common tokens (e.g. 'toi pham' -> 'toi') caused false matches.
    core=[t for t in norm.split() if t not in STOPWORDS]
    seen=set(); result=[]
    for tok in core:
        if tok and tok not in seen:
            seen.add(tok); result.append(tok)
    return norm, result

def rank_books(books, query, top_k=None, min_score=0.0):
    books = list(books or [])
    query_norm, q_tokens = _semantic_query(query)
    if not books or not q_tokens:
        return books[:top_k] if top_k else books
    docs = [_book_tokens(b) for b in books]
    lengths = [max(len(d), 1) for d in docs]
    avgdl = sum(lengths) / max(len(lengths), 1)
    n_docs = len(docs)
    dfs = Counter()
    for doc in docs:
        for term in set(doc): dfs[term] += 1
    k1, b = 1.5, 0.75
    ranked = []
    for book, doc, dl in zip(books, docs, lengths):
        tf = Counter(doc); score = 0.0
        for term in q_tokens:
            df = dfs.get(term, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))
            freq = tf.get(term, 0)
            if freq:
                denom = freq + k1 * (1 - b + b * dl / avgdl)
                score += idf * (freq * (k1 + 1)) / denom
        title = normalize_text(book.get('title', '')); author = normalize_text(book.get('author', ''))
        bid = normalize_text(book.get('id', '')); cat = normalize_text(book.get('category', '')); desc = normalize_text(book.get('description', ''))
        core_phrase = ' '.join([x for x in query_norm.split() if x not in STOPWORDS]).strip()
        if core_phrase and core_phrase in title: score += 8.0
        if core_phrase and core_phrase in author: score += 4.0
        if query_norm and query_norm == bid: score += 12.0
        for phrase, terms in QUERY_EXPANSIONS.items():
            if phrase in query_norm:
                for term in terms:
                    nterm = normalize_text(term)
                    if nterm and nterm in cat: score += 6.0
                    if nterm and nterm in title: score += 4.0
                    if nterm and nterm in desc: score += 2.5
        if score > min_score:
            item = dict(book); item['_bm25_score'] = round(score, 4); ranked.append(item)
    ranked.sort(key=lambda x: (-x['_bm25_score'], normalize_text(x.get('title',''))))
    if top_k: ranked = ranked[:int(top_k)]
    return ranked

def chunk_text(text, max_chars=650):
    paragraphs = [re.sub(r'\s+', ' ', p).strip() for p in re.split(r'\n\s*\n|\n', text or '') if p.strip()]
    chunks, buf = [], ''
    for p in paragraphs:
        if not buf:
            buf = p
        elif len(buf) + len(p) + 1 <= max_chars:
            buf += ' ' + p
        else:
            chunks.append(buf)
            buf = p
    if buf:
        chunks.append(buf)
    return chunks


def rank_text_chunks(chunks, query, top_k=4):
    chunks = list(chunks or [])
    q_tokens = tokenize(query)
    if not chunks or not q_tokens:
        return []
    docs = [tokenize(c) for c in chunks]
    lengths = [max(len(d),1) for d in docs]
    avgdl = sum(lengths)/len(lengths)
    n_docs = len(docs)
    dfs = Counter()
    for doc in docs:
        for term in set(doc): dfs[term] += 1
    k1,b=1.5,0.75
    result=[]
    for idx,(chunk,doc,dl) in enumerate(zip(chunks,docs,lengths)):
        tf=Counter(doc); score=0.0
        for term in q_tokens:
            df=dfs.get(term,0)
            idf=math.log(1+(n_docs-df+0.5)/(df+0.5))
            freq=tf.get(term,0)
            if freq:
                score += idf*(freq*(k1+1))/(freq+k1*(1-b+b*dl/avgdl))
        if score>0:
            result.append({'text':chunk,'score':round(score,4),'index':idx})
    result.sort(key=lambda x:-x['score'])
    return result[:int(top_k)]


def load_policy_chunks(path):
    p=Path(path)
    if not p.exists(): return []
    return chunk_text(p.read_text(encoding='utf-8',errors='ignore'))
