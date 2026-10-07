import os
import re
import time
import unicodedata
from collections import OrderedDict
from pathlib import Path

from dotenv import load_dotenv

import database as db
from bm25_service import load_policy_chunks, rank_text_chunks, rank_books

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
POLICY_FILE = BASE_DIR / 'chinh_sach_thu_vien.txt'

try:
    from google import genai
except Exception:
    genai = None


def normalize(text):
    text = str(text or '').lower().strip().replace('đ','d')
    text = unicodedata.normalize('NFD', text)
    text = ''.join(ch for ch in text if unicodedata.category(ch) != 'Mn')
    return re.sub(r'\s+', ' ', text)


def _policy_like(query):
    q=normalize(query)
    keys=['quy dinh','chinh sach','muon bao nhieu','muon toi da','qua han','tien phat','gia han','dat truoc','khong tra','mat sach','han tra','the doc gia']
    return any(k in q for k in keys)


def _book_like(query):
    q=normalize(query)
    keys=['tim sach','tim truyen','sach ve','sach nao','tac gia','the loai','ma sach','isbn','con sach','goi y sach','kho sach','tin hoc','trinh tham','triet ly']
    return bool(re.search(r'\bb\d{3}\b',q)) or any(k in q for k in keys)


def _book_context(books):
    lines=[]
    for b in books:
        lines.append(
            f"[{b['id']}] {b['title']} | tác giả: {b['author']} | thể loại: {b['category']} | "
            f"còn {b['available']}/{b['quantity']} bản | vị trí: {b.get('location') or '—'} | "
            f"mô tả: {b.get('description') or '—'}"
        )
    return '\n'.join(lines)


def _local_book_answer(books):
    if not books:
        return 'Mình chưa tìm thấy sách phù hợp trong kho. Bạn thử tên tác giả, thể loại hoặc từ khóa cụ thể hơn nhé.'
    top=float(books[0].get('_bm25_score',0) or 0)
    cutoff=top*0.45 if top>0 else 0
    shown=[b for b in books if float(b.get('_bm25_score',top) or 0)>=cutoff][:5]
    if not shown: shown=books[:5]
    lines=['Dựa trên **kho sách hiện tại**, mình gợi ý:']
    for i,b in enumerate(shown,1):
        status=f"còn {b['available']} bản" if int(b.get('available') or 0)>0 else 'hiện đã hết'
        lines.append(f"{i}. **{b['title']}** (`{b['id']}`) — {b['author']} · {b['category']} · {status}")
    lines.append('Bạn có thể nhập tên hoặc mã sách để xem chi tiết/mượn sách.')
    return '\n'.join(lines)

def _local_policy_answer(chunks):
    if not chunks:
        return 'Mình chưa tìm thấy quy định phù hợp trong dữ liệu chính sách thư viện.'
    return '**Thông tin chính sách liên quan:**\n\n' + '\n\n'.join(f'- {c["text"]}' for c in chunks[:4])


def _popular_like(query):
    q=normalize(query)
    return any(k in q for k in ['quan tam nhat','doc nhieu','xem nhieu','pho bien','top sach','noi bat'])


def _vague_recommendation(query):
    q=normalize(query)
    return ('goi y' in q or 'tu van' in q) and not any(k in q for k in ['python','lap trinh','ai','trinh tham','tinh yeu','lang man','triet ly','ky nang','kinh te','suc khoe','tam ly','van hoc'])

def _needs_generation(query, route):
    q=normalize(query)
    if route=='GENERAL': return True
    keys=['tom tat','phan tich','so sanh','giai thich','vi sao','review','noi dung chi tiet','tu van hoc']
    return any(k in q for k in keys)


class AIService:
    """Fast automatic RAG router.

    Speed strategy:
    - GENERAL questions skip MySQL/BM25 entirely.
    - BOOK questions search an in-memory catalog cache (short TTL).
    - POLICY questions only rank policy chunks; they do not scan books.
    - Exact repeated questions reuse a small in-memory response cache.
    - Gemini receives only the top 3 context items and 3 recent turns.
    """
    def __init__(self):
        api_key=os.getenv('GEMINI_API_KEY','').strip()
        self.model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite').strip()
        self.enabled=bool(genai and api_key and api_key!='PASTE_YOUR_GEMINI_API_KEY_HERE')
        self.client=genai.Client(api_key=api_key) if self.enabled else None
        self.policy_chunks=load_policy_chunks(POLICY_FILE)

        # Keep retrieval intentionally small; shorter context = faster generation.
        try:
            configured=int(db.get_setting('rag_top_k',3) or 3)
        except Exception:
            configured=3
        self.top_k=max(1,min(configured,3))

        # Small short-lived catalog cache. MySQL is refreshed automatically after TTL.
        try:
            self.book_cache_seconds=max(3,float(os.getenv('AI_BOOK_CACHE_SECONDS','15') or 15))
        except Exception:
            self.book_cache_seconds=15.0
        self._books_cache=[]
        self._books_cache_at=0.0

        # Repeated questions become instant without calling Gemini/MySQL again.
        self._answer_cache=OrderedDict()
        self._answer_cache_limit=40

    def _cache_get(self, query):
        key=normalize(query)
        value=self._answer_cache.get(key)
        if value is None:
            return None
        self._answer_cache.move_to_end(key)
        return value

    def _cache_put(self, query, answer):
        key=normalize(query)
        if not key or not answer:
            return
        self._answer_cache[key]=answer
        self._answer_cache.move_to_end(key)
        while len(self._answer_cache)>self._answer_cache_limit:
            self._answer_cache.popitem(last=False)

    def _catalog(self):
        now=time.monotonic()
        if not self._books_cache or (now-self._books_cache_at)>=self.book_cache_seconds:
            self._books_cache=db.list_books()
            self._books_cache_at=now
        return self._books_cache

    def invalidate_catalog(self):
        self._books_cache=[]
        self._books_cache_at=0.0
        self._answer_cache.clear()

    def _book_search(self, query):
        ranked=rank_books(self._catalog(),query,top_k=self.top_k)
        if not ranked:
            return []
        top=float(ranked[0].get('_bm25_score',0) or 0)
        threshold=max(0.8,top*0.30) if top>0 else 0.8
        filtered=[b for b in ranked if float(b.get('_bm25_score',0) or 0)>=threshold]
        return (filtered or ranked)[:self.top_k]

    def retrieve(self, query):
        # Fast-path routing: do not calculate both retrieval branches for every message.
        if _policy_like(query):
            policies=rank_text_chunks(self.policy_chunks,query,top_k=min(self.top_k,3))
            score=policies[0].get('score',0) if policies else 0
            return {'route':'POLICY','books':[],'policies':policies,'book_score':0,'policy_score':score}

        if _book_like(query):
            books=self._book_search(query)
            score=books[0].get('_bm25_score',0) if books else 0
            return {'route':'BOOK','books':books,'policies':[],'book_score':score,'policy_score':0}

        # Most normal/general questions go straight to Gemini: zero MySQL queries.
        q=normalize(query)
        library_words=['thu vien','doc gia','muon sach','tra sach','tien phat','dat truoc','kho sach']
        if not any(k in q for k in library_words):
            return {'route':'GENERAL','books':[],'policies':[],'book_score':0,'policy_score':0}

        # Ambiguous library question: only then compare both small retrieval branches.
        books=self._book_search(query)
        policies=rank_text_chunks(self.policy_chunks,query,top_k=min(self.top_k,3))
        book_score=books[0].get('_bm25_score',0) if books else 0
        policy_score=policies[0].get('score',0) if policies else 0
        if policy_score > book_score*1.15 and policy_score>0.5:
            route='POLICY'
        elif book_score>=1.0:
            route='BOOK'
        else:
            route='GENERAL'
        return {'route':route,'books':books,'policies':policies,'book_score':book_score,'policy_score':policy_score}

    def route_info(self, query=None, rag=None):
        r=rag if rag is not None else self.retrieve(query or '')
        return {
            'route':r['route'],'book_score':round(r['book_score'],3),'policy_score':round(r['policy_score'],3),
            'retrieved_books':[b['id'] for b in r['books']],'policy_chunks':len(r['policies']),
        }

    def answer(self, query, history=None, rag=None):
        # Exact repeat = instant answer.
        cached=self._cache_get(query)
        if cached is not None:
            return cached

        rag=rag if rag is not None else self.retrieve(query)
        route=rag['route']

        if _popular_like(query):
            answer=_local_book_answer(db.top_viewed_books(5))
            self._cache_put(query,answer)
            return answer

        if _vague_recommendation(query):
            answer=('Bạn muốn mình gợi ý theo chủ đề nào? Ví dụ: **tình yêu, trinh thám, Python/AI, triết lý, kỹ năng sống, tâm lý, kinh tế**. '
                    'Bạn chỉ cần nhập một chủ đề, mình sẽ lấy đúng sách đang có trong kho.')
            self._cache_put(query,answer)
            return answer

        # Search/policy questions should answer locally whenever possible: no network wait.
        if not _needs_generation(query, route):
            if route=='BOOK':
                answer=_local_book_answer(rag['books']); self._cache_put(query,answer); return answer
            if route=='POLICY':
                answer=_local_policy_answer(rag['policies']); self._cache_put(query,answer); return answer

        if not self.enabled:
            if route=='BOOK': return _local_book_answer(rag['books'])
            if route=='POLICY': return _local_policy_answer(rag['policies'])
            return ('Gemini AI chưa được cấu hình. Tra cứu sách/chính sách vẫn hoạt động cục bộ. '
                    'Để hỏi kiến thức tổng quát, hãy điền `GEMINI_API_KEY` trong file `.env`.')

        # Less history and less context greatly reduce request size/latency.
        history_lines=[]
        for item in (history or [])[-3:]:
            role='Người dùng' if item.get('role')=='user' else 'Trợ lý'
            content=str(item.get('content',''))[:700]
            history_lines.append(f"{role}: {content}")

        if route=='BOOK':
            context='DỮ LIỆU SÁCH TỪ MYSQL:\n'+_book_context(rag['books'][:3])
            instruction='Chỉ dùng dữ liệu sách dưới đây. Trả lời tối đa khoảng 6 câu, không bịa dữ liệu.'
        elif route=='POLICY':
            context='CHÍNH SÁCH THƯ VIỆN:\n'+'\n'.join(f"- {x['text']}" for x in rag['policies'][:3])
            instruction='Chỉ dựa trên chính sách dưới đây. Trả lời ngắn gọn, nếu thiếu dữ liệu thì nói rõ.'
        else:
            context=''
            instruction='Trả lời ngắn gọn, trực tiếp bằng tiếng Việt; ưu tiên dưới 8 câu.'

        prompt=(
            f"Bạn là trợ lý SmartLibrary. Chế độ: {route}.\n"
            f"{instruction}\n{context}\n"
            f"Hội thoại gần đây:\n{chr(10).join(history_lines) if history_lines else '(không có)'}\n"
            f"Câu hỏi: {query}"
        )
        candidate_models=[self.model]
        for fallback_m in ['gemini-2.5-flash','gemini-2.0-flash','gemini-1.5-flash','gemini-2.5-flash-lite']:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        for target_model in candidate_models:
            try:
                response=self.client.models.generate_content(model=target_model,contents=prompt)
                text=(getattr(response,'text','') or '').strip()
                if text:
                    self._cache_put(query,text)
                    return text
            except Exception:
                continue

        if route=='BOOK': return _local_book_answer(rag['books'])
        if route=='POLICY': return _local_policy_answer(rag['policies'])
        return ('Hệ thống AI hiện đang bận (server capacity limit). '
                'Bạn vui lòng thử lại sau giây lát hoặc sử dụng ô tìm kiếm để tra cứu trực tiếp.')

    def answer_stream(self, query, history=None, rag=None):
        """Streaming generator for smooth, word-by-word UI rendering in Streamlit."""
        cached=self._cache_get(query)
        if cached is not None:
            yield cached
            return

        rag=rag if rag is not None else self.retrieve(query)
        route=rag['route']

        if _popular_like(query):
            answer=_local_book_answer(db.top_viewed_books(5))
            self._cache_put(query,answer)
            yield answer
            return

        if _vague_recommendation(query):
            answer=('Bạn muốn mình gợi ý theo chủ đề nào? Ví dụ: **tình yêu, trinh thám, Python/AI, triết lý, kỹ năng sống, tâm lý, kinh tế**. '
                    'Bạn chỉ cần nhập một chủ đề, mình sẽ lấy đúng sách đang có trong kho.')
            self._cache_put(query,answer)
            yield answer
            return

        if not _needs_generation(query, route):
            if route=='BOOK': answer=_local_book_answer(rag['books'])
            elif route=='POLICY': answer=_local_policy_answer(rag['policies'])
            else: answer='Dữ liệu đang được xử lý.'
            self._cache_put(query,answer)
            yield answer
            return

        if not self.enabled:
            if route=='BOOK': yield _local_book_answer(rag['books'])
            elif route=='POLICY': yield _local_policy_answer(rag['policies'])
            else:
                yield ('Gemini AI chưa được cấu hình. Tra cứu sách/chính sách vẫn hoạt động cục bộ. '
                       'Để hỏi kiến thức tổng quát, hãy điền `GEMINI_API_KEY` trong file `.env`.')
            return

        history_lines=[]
        for item in (history or [])[-3:]:
            role='Người dùng' if item.get('role')=='user' else 'Trợ lý'
            content=str(item.get('content',''))[:700]
            history_lines.append(f"{role}: {content}")

        if route=='BOOK':
            context='DỮ LIỆU SÁCH TỪ MYSQL:\n'+_book_context(rag['books'][:3])
            instruction='Chỉ dùng dữ liệu sách dưới đây. Trả lời tối đa khoảng 6 câu, không bịa dữ liệu.'
        elif route=='POLICY':
            context='CHÍNH SÁCH THƯ VIỆN:\n'+'\n'.join(f"- {x['text']}" for x in rag['policies'][:3])
            instruction='Chỉ dựa trên chính sách dưới đây. Trả lời ngắn gọn, nếu thiếu dữ liệu thì nói rõ.'
        else:
            context=''
            instruction='Trả lời ngắn gọn, trực tiếp bằng tiếng Việt; ưu tiên dưới 8 câu.'

        prompt=(
            f"Bạn là trợ lý SmartLibrary. Chế độ: {route}.\n"
            f"{instruction}\n{context}\n"
            f"Hội thoại gần đây:\n{chr(10).join(history_lines) if history_lines else '(không có)'}\n"
            f"Câu hỏi: {query}"
        )

        candidate_models=[self.model]
        for fallback_m in ['gemini-2.5-flash','gemini-2.0-flash','gemini-1.5-flash','gemini-2.5-flash-lite']:
            if fallback_m not in candidate_models:
                candidate_models.append(fallback_m)

        full_text=""
        success=False

        for target_model in candidate_models:
            try:
                response_stream=self.client.models.generate_content_stream(model=target_model,contents=prompt)
                chunk_found=False
                for chunk in response_stream:
                    txt=(getattr(chunk,'text','') or '')
                    if txt:
                        chunk_found=True
                        full_text+=txt
                        yield txt
                if chunk_found and full_text.strip():
                    success=True
                    break
            except Exception:
                full_text=""
                continue

        if success and full_text.strip():
            self._cache_put(query,full_text.strip())
        else:
            if route=='BOOK': fb=_local_book_answer(rag['books'])
            elif route=='POLICY': fb=_local_policy_answer(rag['policies'])
            else:
                fb=('Hệ thống AI đang bận (server capacity). Dưới đây là tra cứu từ thư viện:\n\n' +
                    (_local_book_answer(rag['books']) if rag.get('books') else _local_policy_answer(rag['policies']) if rag.get('policies') else 'Bạn có thể thử lại sau giây lát hoặc sử dụng ô tra cứu sách.'))
            yield fb


